import discord;
import time;
from fun import game;
from botstuff import commands,util,events;

@commands.command(args_pattern="S?")
async def help(ctx,*args,**details):
  
    """
    [CMD_KEY]help (command name)
    
    INCEPTION SOUND
    """
    
    help_logo = 'https://cdn.discordapp.com/attachments/173443449863929856/275299953528537088/helo_458x458.jpg';
    
    help = discord.Embed( title="DueUtil's Help",type="rich",color=16038978);
    server_key = util.get_server_cmd_key(ctx.server);
    
    
    if len(args) == 1:
      
        help.set_thumbnail(url=help_logo);
      
        command = events.get_command(args[0]);
    
        if command == None:
            command_name = 'Not found';
            command_help = 'That command was not found!';
        else:
            command_name = command.__name__;
            if command.__doc__ != None:
                command_help = command.__doc__.replace('[CMD_KEY]',server_key);
            else:
                command_help = 'Sorry there is no help for that command!';
            
        help.description="Showing help for **"+command_name+"**";
        help.add_field(name=command_name,value=command_help);

    else:
      
        help.set_thumbnail(url=util.get_client(ctx.server.id).user.avatar_url);
       
        help.description='Welcome to the help! Simply do '+server_key+'help (command name).';
        help.add_field(name='Commands for everyone',value=events.command_event.command_list(lambda command: not command.admin_only));
        help.add_field(name='Admins only',value=events.command_event.command_list(lambda command: command.admin_only));
        
        help.set_footer(text="To use admin commands you must have the manage server permission or the 'Due Commander' role.");
      
    await util.say(ctx.channel,embed=help);

@commands.command(args_pattern=None)
async def dustats(ctx,*args,**details):
    
    game_stats = game.Stats.get_stats();
  
    stats = discord.Embed(title="DueUtil's Stats",type="rich",color=16038978);
    
    stats.description="DueUtil's global stats since "+time.strftime("%m/%d/%Y at %H:%M", time.gmtime(0))+"!";
    stats.add_field(name="Images Served",value=game_stats['images_served']);
    stats.add_field(name="Awarded",value=game_stats['money_created']);
    stats.add_field(name="Players have transferred",value=game_stats['money_transferred']);
    stats.add_field(name="Quests Given",value=game_stats['quests_given']);
    stats.add_field(name="Quests Attempted",value=game_stats['quests_attempted']);
    stats.add_field(name="Level Ups",value=game_stats['players_leveled']);
    stats.add_field(name="New Players",value=game_stats['new_players_joined']);
    
    stats.set_footer(text="DueUtil Shard "+str(util.get_client(ctx.server.id).shard_id+1));
    
    await util.say(ctx.channel,embed=stats);
             
            