from functools import wraps
import util_due;
import due_battles_quests as game;
from commands.util import events;

def command(**command_rules):
  
    """A command wrapper for command functions"""
  
    def wrap(command_func):
  
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            if(args[0].lower() != command_func.__name__):
                return False;
            if(ctx.author.id != "IDK"):
                print(ctx.author.server_permissions);
                args_pattern = command_rules.get('args_pattern',"");
                if not await check_pattern(args_pattern,*args[1:]):
                    await util_due.get_client(ctx.server.id).add_reaction(ctx,u"\u2753");
                    return False;
                await util_due.say(ctx.channel,str(args));
                await command_func(ctx,*args[1:],**kwargs);
            else:
                raise util_due.DueUtilException(ctx.channel,"You can't use that command!");
            return True;
        events.register_command(wrapped_command);
        return wrapped_command;
        
    return wrap;
    

def parse(command_message):
  
    """A basic command parser with support for escape strings."""
    
    key = util_due.get_server_cmd_key(command_message.server);
    command_string = command_message.content.replace(key,'',1);
    user_mentions = command_message.raw_mentions;
    escaped = False;
    is_string = False;
    args = [];
    current_arg = '';
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
                    current_arg, args = __add_arg(current_arg,args);
                    continue;
            else:
                escaped = False;
            current_arg += command_string[char_pos];
        else:
            for mention in user_mentions: #Replade mentions
                if mention in arg and len(arg)-len(mention) < 6:
                    current_arg = mention;
                    del user_mentions[user_mentions.index(mention)];
            current_arg, args = __add_arg(current_arg,args);
    if is_string:
        raise util_due.DueUtilException(command_message.channel,"Unclosed string in command!");
        
    return args;
    
async def check_pattern(pattern,*args):
    
    """A string to define the expected args of a command
    
    e.g. SIRIIP
    
    means String, Integer, Real, Integer, Integer, Player.
    
    """
        
    if len(pattern) == 0:
        return True;
    
    if len(pattern) != len(args):
        return False;
    
    for pos in range(0,len(pattern)):
        current_rule = pattern[pos];
        switch = {
            'S': not args[pos].isspace(),
            'I': represents_int(args[pos]),
            'R': represents_float(args[pos]),
            'P': game.Player.find_player(args[pos])
        }
        if not switch.get(current_rule):
            return False;
    return True;
        
def represents_int(string):
    try: 
        int(string)
        return True
    except:return False  
    
def represents_float(string):
    try: 
        float(string)
        return True
    except:return False 
    
def point_error(command_string):
  
    """Maybe make a programming lang style error string."""
    
    error_string = command_string+"\n";
    for char_pos in range(len(command_string),-1,-1):
        if command_string[char_pos-1] == '"':
            error_string += ' ' * (char_pos-1);
            break;
    return error_string + '^';
        
                    
def __add_arg(arg,args):
    if len(arg) > 0:
        return ("",args + [arg,],);
    else:
        return ("",args);
            
