import time;
import asyncio;
from discord import Permissions;
from functools import wraps
from fun import game;
from botstuff import events,util;


def command(**command_rules):
  
    """A command wrapper for command functions"""
    
    
    def check(user,command):
        if command.admin_only:
            return user.server_permissions.manage_server; 
        return True;
  
    def is_spam_command(ctx,command,*args):
        if not command.admin_only:
          return (sum(isinstance(arg,game.Player) for arg in args)
                  < len(ctx.raw_mentions) or ctx.mention_everyone
                  or '@here' in ctx.content or '@everyone' in ctx.content);
        return False;
      
    def wrap(command_func):
  
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            if args[0].lower() != command_func.__name__:
                return False;
            if check(ctx.author,wrapped_command):
                args_pattern = command_rules.get('args_pattern',"");
                if not await check_pattern(args_pattern,args[1]):
                    await util.get_client(ctx.server.id).add_reaction(ctx,u"\u2753");
                elif not is_spam_command(ctx,wrapped_command,*args):
                    await util.say(ctx.channel,str(args));
                    await command_func(ctx,*args[1],**kwargs);
                else:
                    raise util.DueUtilException(ctx.channel,"Please don't include spam mentions in commands.");
            else:
                raise util.DueUtilException(ctx.channel,"You can't use that command!");
            return True;
        events.register_command(wrapped_command);
        
        wrapped_command.is_hidden = command_rules.get('hidden',False);
        wrapped_command.admin_only = command_rules.get('admin_only',False);
        wrapped_command.bot_mod_only = command_rules.get('bot_mod_only',False);
        wrapped_command.bot_admin_only = command_rules.get('bot_admin_only',False);
            
        return wrapped_command;
        
    return wrap;
    
def imagecommand(**command_rules):

    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            rate_limit = command_rules.get('rate_limit',True);
            player = game.Players.find_player(ctx.author.id);
            if rate_limit:
                if time.time() - player.last_image_request < 10:
                    await util.say(ctx.channel,":cold_sweat: Please don't break me!");
                    return;
                else:
                    player.last_image_request = time.time();
            await util.get_client(ctx).send_typing(ctx.channel);
            await asyncio.ensure_future(command_func(ctx,*args,**kwargs));
        return wrapped_command;
    return wrap;
          
def parse(command_message):
  
    """A basic command parser with support for escape strings."""
    
    
    key = util.get_server_cmd_key(command_message.server);
    command_string = command_message.content.replace(key,'',1);
    user_mentions = command_message.raw_mentions;
    escaped = False;
    is_string = False;
    args = [];
    current_arg = '';
    
    def replace_mentions():
        nonlocal user_mentions,current_arg;
        print(user_mentions);
        for mention in user_mentions: #Replade mentions
            if mention in current_arg and len(current_arg)-len(mention) < 6:
                current_arg = mention;
                del user_mentions[user_mentions.index(mention)];
                
    def add_arg():
        nonlocal current_arg,args;
        if len(current_arg) > 0:
            replace_mentions();
            args = args + [current_arg,];
            current_arg = "";
    
    for char_pos in range(0,len(command_string)+1):
        current_char = command_string[char_pos] if char_pos < len(command_string) else ' ';
        next_char = command_string[char_pos +1] if char_pos + 1 < len(command_string) else ' ';
        if char_pos < len(command_string) and (not current_char.isspace() or is_string):
            if not escaped:
                if current_char == '\\' and not (current_char.isspace() or current_char.isalpha()):
                    escaped = True;
                    continue;
                elif current_char == '"':
                    is_string = not is_string;
                    add_arg();
                    continue;
            else:
                escaped = False;
            current_arg += command_string[char_pos];
        else:
            add_arg();
            
    if is_string:
        raise util.DueUtilException(command_message.channel,"Unclosed string in command!");
        
    return (args[0],args[1:]);
    
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
        value = represents_int(string);
        if not value:
            return False;
        elif value-1 >= 0:
            return value;
    
    def represents_float(string):
        try: 
            return float(string)
        except:return False 
        
    def check_optional():
        nonlocal pattern,args;
        pattern_pos = len(pattern)-1
        while pattern_pos >= 0:
            if len(pattern.replace('?','')) == len(args):
                break;
            elif pattern_pos == 0:
                return False;
            if pattern[pattern_pos] == '?':
                pattern = pattern[:pattern_pos-1];
                pattern_pos = len(pattern)-1;
                continue;
            pattern_pos -= 1;
        pattern = pattern.replace('?','');
        return True;
    
    if pattern == None and len(args) > 0:
        return False;
    elif pattern == None and len(args) == 0:
        return True;
    if len(pattern) == 0:
        return True;
    if not check_optional():
        return False;
    if len(args) > len(pattern):
        return False;
        
    for pos in range(0,len(pattern)):
        current_rule = pattern[pos];
        switch = {
            'S': args[pos] if not (args[pos].isspace() and len(args[pos]) == 0) else False,
            'I': represents_int(args[pos]),
            'C': represents_count(args[pos]),
            'R': represents_float(args[pos]),
            'P': game.Players.find_player(args[pos]),
            # This one is for page selectors that could be a page number or a string like a weapon name.
            'M': represents_count(args[pos]) if represents_count(args[pos]) else args[pos],
        }
        value = switch.get(current_rule)
        if not value:
            return False;
        args[pos] = value;
        
    return True;
        
    
def point_error(command_string):
  
    """Maybe make a programming lang style error string."""
    
    error_string = command_string+"\n";
    for char_pos in range(len(command_string),-1,-1):
        if command_string[char_pos-1] == '"':
            error_string += ' ' * (char_pos-1);
            break;
    return error_string + '^';
        
                    

            
