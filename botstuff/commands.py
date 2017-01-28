from functools import wraps
from fun import game;
from botstuff import events,util;

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
                if not await check_pattern(args_pattern,args[1]):
                    await util.get_client(ctx.server.id).add_reaction(ctx,u"\u2753");
                else:
                    await util.say(ctx.channel,str(args));
                    await command_func(ctx,*args[1],**kwargs);
            else:
                raise util.DueUtilException(ctx.channel,"You can't use that command!");
            return True;
        events.register_command(wrapped_command);
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
        for mention in user_mentions: #Replade mentions
            if mention in current_arg and len(current_arg)-len(mention) < 6:
                current_arg = mention;
                del user_mentions[user_mentions.index(mention)];
                
    def add_arg():
        replace_mentions();
        nonlocal current_arg,args;
        if len(current_arg) > 0:
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
    
    def represents_float(string):
        try: 
            return float(string)
        except:return False 
    
        
    if pattern == None and len(args) > 0:
        return False;
    elif pattern == None and len(args) == 0:
        return True;
   
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
        
                    

            
