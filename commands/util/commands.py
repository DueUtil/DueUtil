from functools import wraps
import util_due;

def command(**command_rules):
  
    """A command wrapper for command functions"""
  
    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, *args,**kwargs):
            if(args[0].lower() != command_func.__name__):
                return False;
            if(ctx.author.id != "IDK"):
                await util_due.say(ctx.channel,"```"+str(args)+"```");
                await command_func(ctx,*args[1:],**kwargs);
            else:
                raise util_due.DueUtilException(channel,"You can't use that command! ");
            return True;
        return wrapped_command;
    return wrap;

def parse(command_message):
  
    """A basic command parser with support for escape strings."""
    
    key = util_due.get_server_cmd_key(command_message.server);
    command_string = command_message.content.replace(key,'',1);
    
    escaped = False;
    is_string = False;
    args = ();
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
            current_arg, args = __add_arg(current_arg,args);
    return args;
                    
def __add_arg(arg,args):
    if len(arg) > 0:
        return ("",args + (arg,),);
    else:
        return ("",args);
            
#print(command_parse('!createweapon "Ultra \\"Bob" 1 2.2 1.1'));
