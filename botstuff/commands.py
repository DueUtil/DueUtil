import time
import asyncio
import re
from functools import wraps
from fun.game import players
from fun.configs import dueserverconfig
from fun.helpers import misc
from botstuff import events,util,permissions
from botstuff.permissions import Permission
import sys

IMAGE_REQUEST_COOLDOWN = 5

"""
DueUtils random command system.
"""

def command(**command_rules):
  
    """A command wrapper for command functions"""
    
    # TODO: Include sender, timesent, etc in details
    
    def check(user,command):
        return permissions.has_permission(user,command.permission)

    def is_spam_command(ctx,command,*args):        
        if command.permission < Permission.SERVER_ADMIN:
          return (sum(isinstance(arg,players.Player) for arg in args)
                  < len(ctx.raw_mentions) or ctx.mention_everyone
                  or '@here' in ctx.content or '@everyone' in ctx.content)
        return False
      
    def get_command_details(ctx,**details):
        details["timestamp"] = ctx.timestamp
        details["author"] = players.find_player(ctx.author.id)
        details["server_id"] = ctx.server.id
        details["server_name"] = ctx.server.name
        details["server_name_clean"] = util.ultra_escape_string(ctx.server.name)
        details["author_name"] = ctx.author.name
        details["author_name_clean"] = util.ultra_escape_string(ctx.author.name)
        details["channel"] = ctx.channel
        details["channel_name"] = ctx.channel.name
        details["channel_name_clean"] = util.ultra_escape_string(ctx.channel.name)
        return details
        
    def wrap(command_func):
  
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            if args[1].lower() != command_func.__name__:
                return False
            is_admin = permissions.has_permission(ctx.author,Permission.SERVER_ADMIN)
            if not is_admin and dueserverconfig.mute_level(ctx.channel) == 1:
                return True
            command_whitelist = dueserverconfig.whitelisted_commands(ctx.channel)
            if command_whitelist != None and not is_admin and args[1].lower() not in command_whitelist:
                if "is_blacklist" not in command_whitelist:
                    await util.say(ctx.channel,(":anger: That command is not whitelisted in this channel!\n"
                                                +" You can only use the following commands: ``"
                                                +', '.join(command_whitelist)+"``."))
                else:
                    await util.say(ctx.channel,(":anger: That command is blacklisted in this channel!"))
                return True
            if check(ctx.author,wrapped_command):
                args_pattern = command_rules.get('args_pattern',"")
                command_args = await determine_args(args_pattern,args[2])
                if command_args is False:
                    await util.get_client(ctx.server.id).add_reaction(ctx,u"\u2753")
                elif not is_spam_command(ctx,wrapped_command,*args):
                    # await util.say(ctx.channel,str(args))
                    kwargs["cmd_key"] = args[0]
                    kwargs["command_name"] = args[1]
                    await command_func(ctx,*command_args,**get_command_details(ctx,**kwargs))
                else:
                    raise util.DueUtilException(ctx.channel,"Please don't include spam mentions in commands.")
            else:
                await util.get_client(ctx.server.id).add_reaction(ctx,u"\u274C")
            return True
        events.register_command(wrapped_command)
        
        wrapped_command.is_hidden = command_rules.get('hidden',False)
        wrapped_command.permission = command_rules.get('permission',Permission.ANYONE)
            
        return wrapped_command
        
    return wrap
    
def imagecommand(**command_rules):

    def wrap(command_func):
        @ratelimit(slow_command=True,cooldown=IMAGE_REQUEST_COOLDOWN,error=":cold_sweat: Please don't break me!")
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            await util.get_client(ctx).send_typing(ctx.channel)
            await asyncio.ensure_future(command_func(ctx,*args,**kwargs))
        return wrapped_command
    return wrap

def ratelimit(**command_info):

    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**details):
            player = details["author"]
            command_name = details["command_name"]
            if time.time() - player.command_rate_limts.get(command_name,0) < command_info["cooldown"]:
                await util.say(ctx.channel,command_info["error"])
                return 
            else:
                player.command_rate_limts[command_name] = time.time()
            await command_func(ctx,*args,**details)
        return wrapped_command
    return wrap
          
def parse(command_message):
  
    """A basic command parser with support for escape strings.
    I don't think one like this exists that is not in a package
    that adds a lot more stuff I don't want.
    
    This is meant to be like a shell command lite style.
    
    Supports strings in double quotes & escape strings
    (e.g. \" for a quote character)
    
    The limitations of this parser are 'fixed' in determine_args
    that can guess where quotes should be most times.
    """
    
    key = dueserverconfig.server_cmd_key(command_message.server)
    command_string = command_message.content.replace(key,'',1)
    user_mentions = command_message.raw_mentions
    escaped = False
    is_string = False
    args = []
    current_arg = ''
    
    def replace_mentions():
        nonlocal user_mentions,current_arg
        for mention in user_mentions: # Replade mentions
            if mention in current_arg and len(current_arg)-len(mention) < 6:
                current_arg = mention
                del user_mentions[user_mentions.index(mention)]
                
    def add_arg():
        nonlocal current_arg,args
        if len(current_arg) > 0:
            replace_mentions()
            args = args + [current_arg]
            current_arg = ""
    
    for char_pos in range(0,len(command_string)+1):
        current_char = command_string[char_pos] if char_pos < len(command_string) else ' '
        next_char = command_string[char_pos +1] if char_pos + 1 < len(command_string) else ' '
        if char_pos < len(command_string) and (not current_char.isspace() or is_string):
            if not escaped:
                if current_char == '\\' and not (current_char.isspace() or current_char.isalpha()):
                    escaped = True
                    continue
                elif current_char == '"':
                    is_string = not is_string
                    add_arg()
                    continue
            else:
                escaped = False
            current_arg += command_string[char_pos]
        else:
            add_arg()
            
    if is_string:
        raise util.DueUtilException(command_message.channel,"Unclosed string in command!")
        
    if len(args) > 0:    
        return (key,args[0],args[1:])
    else:
        return (key,"",[])
        
async def determine_args(pattern,args):
    
    """
    
    Takes the args coming from parse()
    (all strings) and using the pattern defined with the 
    command attempts to derermine the args turple with the
    correct types (not just strings).
    
    Types: S(tring), I(nteger), C(ount), R(eal), P(layer), M(ixed) & B(oolean)
    Mods: * (zero or more) & ? (zero or one)
    Valid: SIR?
    Valid SI*PB?R?I?C?
    Invalid: SI?S
    
    This allows the commands to not need to parse their args
    unless they're doing something strange.
    
    TODO: This method probably can be improved and simplified
    
    Returns False if the args could not be determined or
    a turple of args if they could.
    
    WARNING: Python will resolve an empty turple to False so
    use 'is False' for checks insted of 'not determine_args(....)'
    
    """
   
    def represents_int(string):
        try: 
            return min(int(string),int(sys.float_info.max))
        except:return False  
        
    def represents_count(string):
        value = represents_int(string)
        if not value:
            return False
        elif value-1 >= 0:
            return value
    
    def represents_float(string):
        try: 
            return min(float(string),sys.float_info.max)
        except:return False 
        
    def remove_optional(pattern):
        nonlocal args
        pattern_pos = len(pattern)-1
        while pattern_pos >= 0:
            if len(pattern.replace('?','')) == len(args):
                break
            elif pattern_pos == 0:
                return False
            if pattern[pattern_pos] == '?':
                pattern = pattern[:pattern_pos-1]
                pattern_pos = len(pattern)-1
                continue
            pattern_pos -= 1
        return pattern.replace('?','')
        
    def could_be_string(pattern):
        if pattern[0] == 'S':
            if len(pattern) > 1:
                pattern_pos = len(pattern)-1
                while pattern_pos > 0:
                    if pattern[pattern_pos] == '?':
                        pattern_pos -= 2
                        continue
                    return False
            return True
        return False
        
    def valid_args_len(args,pattern):
        pattern_type_count = len(pattern) - pattern.count('*')
        if '*' in pattern:
            return len(args) >= pattern_type_count
        return len(args) == pattern_type_count
    
    def represents_string(string):
        
        """
        This may seem dumb. But not all strings are strings in my
        world. Fuck zerowidth bullshittery & stuff like that.
        
        -xoxo MacDue
        """
        # Remove zero width bullshit & extra spaces
        string = re.sub(r'[\u200B-\u200D\uFEFF]','',string.strip())
        # Remove extra spaces/tabs/new lines ect.
        string = " ".join(string.split())
        if len(string) > 0:
            return string
        return False

    guessing_arguments = False  
    if pattern == None and len(args) > 0:
        return False
    elif pattern == None and len(args) == 0:
        return args
    if len(pattern) == 0:
        return args
    if '*' not in pattern:
        pattern_optional_removed = remove_optional(pattern)
        if pattern_optional_removed is False or len(args) > len(pattern_optional_removed):
            if could_be_string(pattern):
                # If the command is wrong by all other tests and it could be a string
                # merge the arguments to a single string.
                if len(args) > 0:
                    return (' '.join(args),)
                return False
            # Guesing args: Trying to figure out if the user has forgot quotes.
            # With no context on the command it's fiddly
            guessing_arguments = True
        if not guessing_arguments: 
            pattern = pattern_optional_removed
        else:
            pattern = pattern.replace('?','')
    pos = 0
    args_index = 0
    current_rule = ''
    checks_satisfied = 0
    while pos < len(pattern) and args_index < len(args):
        pos_change = pattern[pos] != '*'
        if pos_change:
            current_rule = pattern[pos]
        if pos + 1 < len(pattern) and pattern[pos + 1] == '*':
            pos += 1
            pos_change = False
        switch = {
            'S': represents_string(args[args_index]),
            'I': represents_int(args[args_index]),
            'C': represents_count(args[args_index]),
            'R': represents_float(args[args_index]),
            'P': players.find_player(args[args_index]),
            # This one is for page selectors that could be a page number or a string like a weapon name.
            'M': represents_count(args[args_index]) if represents_count(args[args_index]) else args[args_index],
            'B': args[args_index].lower() in misc.POSTIVE_BOOLS,
        }
        value = switch.get(current_rule)
        if (value is False and current_rule != 'B') or value == None:
            if pattern[pos] != '*':
                return False
            else:
                if pos + 1 < len(pattern):
                    args_index -= 1
                    pos_change = True
                else:
                    return False
        else:
            args[args_index] = value
            checks_satisfied+=1
        args_index+=1
        if pos_change:
            pos+=1
    if (checks_satisfied == len(args) and not guessing_arguments
        and valid_args_len(args,pattern)):
        return args
    elif guessing_arguments:
        """
        If they've forgot quotes for the last sting
        so !command arg0 arg1 arg2 "A String here"
        and they've done
        !command arg0 arg1 arg2 A String here
        """
        if len(args) > len(pattern):
            last_string = pattern.rfind('S')
            if last_string != -1:
                if could_be_string(pattern[last_string:]):
                    new_args = tuple(args[:last_string])+(' '.join(args[last_string:]),)
                    if checks_satisfied == len(new_args) and valid_args_len(new_args,pattern):
                        return new_args
    return False
        

def point_error(command_string):
  
    """Maybe make a programming lang style error string."""
    
    error_string = command_string+"\n"
    for char_pos in range(len(command_string),-1,-1):
        if command_string[char_pos-1] == '"':
            error_string += ' ' * (char_pos-1)
            break
    return error_string + '^'
