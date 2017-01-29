import discord;
from botstuff import commands,util,events;

@commands.command(args_pattern="?S")
async def help(ctx,*args):
  
    """
    [CMD_KEY]help (command name)
    
    INCEPTION SOUND
    """
    
    help = discord.Embed();
    server_key = util.get_server_cmd_key(ctx.server);
            
    if len(args) == 1:
        command = events.get_command(args[0]);
    
        if command == None:
            command_name = 'Not found.';
            command_help = 'That command was not found!';
        else:
            command_name = command.__name__;
            if command.__doc__ != None:
                command_help = command.__doc__.replace('[CMD_KEY]',server_key);
            else:
                command_help = 'Sorry there is no help for that command!';
            
        help.title = title="Help: "+command_name;
        help.add_field(name='Information',value=command_help);

    else:
        help.title = "DueUtil's help!";
        help.description='Welcome to the help! Simply do '+server_key+'help (command name).';
        help.add_field(name='Available commands',value=str(events.command_event));
      
    await util.say(ctx.channel,embed=help);
