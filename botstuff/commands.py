import time
import asyncio
from functools import wraps
from fun import players,misc,dueserverconfig
from botstuff import events,util,permissions
from botstuff.permissions import Permission

IMAGE_REQUEST_COOLDOWN = 5

def command(**command_rules):
  
    """A command wrapper for command functions"""
    
    # TODO: Include sender, timesent, etc in details
    
    def check(user,command):
        return permissions.has_permission(user,command.permission)

    def is_spam_command(ctx,command,*args):
        if command.permission != Permission.SERVER_ADMIN:
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
                if not await check_pattern(args_pattern,args[2]):
                    await util.get_client(ctx.server.id).add_reaction(ctx,u"\u2753")
                elif not is_spam_command(ctx,wrapped_command,*args):
                    # await util.say(ctx.channel,str(args))
                    kwargs["cmd_key"] = args[0]
                    kwargs["command_name"] = args[1]
                    await command_func(ctx,*args[2],**get_command_details(ctx,**kwargs))
                else:
                    raise util.DueUtilException(ctx.channel,"Please don't include spam mentions in commands.")
            else:
                raise util.DueUtilException(ctx.channel,"You can't use that command!")
            return True
        events.register_command(wrapped_command)
        
        wrapped_command.is_hidden = command_rules.get('hidden',False)
        wrapped_command.permission = command_rules.get('permission',Permission.ANYONE)
            
        return wrapped_command
        
    return wrap
    
def imagecommand(**command_rules):

    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            rate_limit = command_rules.get('rate_limit',True)
            player = players.find_player(ctx.author.id)
            if rate_limit:
                if time.time() - player.last_image_request < IMAGE_REQUEST_COOLDOWN:
                    await util.say(ctx.channel,":cold_sweat: Please don't break me!")
                    return
                else:
                    player.last_image_request = time.time()
            await util.get_client(ctx).send_typing(ctx.channel)
            await asyncio.ensure_future(command_func(ctx,*args,**kwargs))
        return wrapped_command
    return wrap
          
def parse(command_message):
  
    """A basic command parser with support for escape strings."""
    
    
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
            args = args + [current_arg,]
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
        
    return (key,args[0],args[1:])
    
async def check_pattern(pattern,args):
    
    """A string to define the expected args of a command
    
    e.g. SIRIIP
    
    means String, Integer, Real, Integer, Integer, Player.
    
    """
   
    def represents_int(string):
        try: 
            return int(string)
        except:return False  
        
    def represents_count(string):
        value = represents_int(string)
        if not value:
            return False
        elif value-1 >= 0:
            return value
    
    def represents_float(string):
        try: 
            return float(string)
        except:return False 
        
    def check_optional():
        nonlocal pattern,args
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
        pattern = pattern.replace('?','')
        return True
    
    if pattern == None and len(args) > 0:
        return False
    elif pattern == None and len(args) == 0:
        return True
    if len(pattern) == 0:
        return True
    if '*' not in pattern:
        if not check_optional():
            return False
        if len(args) > len(pattern):
            return False
        
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
            'S': args[args_index].strip('`') if not (args[args_index].isspace() and len(args[args_index]) == 0) else False,
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
    return checks_satisfied == len(args)
        
    
def point_error(command_string):
  
    """Maybe make a programming lang style error string."""
    
    error_string = command_string+"\n"
    for char_pos in range(len(command_string),-1,-1):
        if command_string[char_pos-1] == '"':
            error_string += ' ' * (char_pos-1)
            break
    return error_string + '^'
