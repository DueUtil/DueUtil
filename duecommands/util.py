import discord
from fun import stats, dueserverconfig
from fun.stats import Stat
from botstuff import commands,util,events
from botstuff.permissions import Permission

@commands.command(args_pattern="S?")
async def help(ctx,*args,**details):
  
    """
    [CMD_KEY]help (command name)
    
    INCEPTION SOUND
    """
    
    help_logo = 'https://cdn.discordapp.com/attachments/173443449863929856/275299953528537088/helo_458x458.jpg'
    
    help = discord.Embed( title="DueUtil's Help",type="rich",color=16038978)
    server_key = details["cmd_key"]
    categories = events.command_event.category_list()
    
    if len(args) == 1:
      
        help.set_thumbnail(url=help_logo)
        if args[0].lower() not in categories:
            command = events.get_command(args[0])
        
            if command == None:
                command_name = 'Not found'
                command_help = 'That command was not found!'
            else:
                command_name = command.__name__
                if command.__doc__ != None:
                    command_help = command.__doc__.replace('[CMD_KEY]',server_key)
                else:
                    command_help = 'Sorry there is no help for that command!'
                
            help.description="Showing help for **"+command_name+"**"
            help.add_field(name=command_name,value=command_help)
        else:
            category = args[0].lower()
            help.description="Showing ``"+category+"`` commands."
            
            commands_for_all = events.command_event.command_list(lambda command: command.permission == Permission.ANYONE and command.category == category)
            admin_commands = events.command_event.command_list(lambda command: command.permission == Permission.SERVER_ADMIN and command.category == category)
            
            if len(commands_for_all) > 0:
                help.add_field(name='Commands for everyone',value= ', '.join(commands_for_all),inline=False) 
            if len(admin_commands) > 0:
                help.add_field(name='Admins only',value=', '.join(admin_commands),inline=False)
    else:
      
        help.set_thumbnail(url=util.get_client(ctx.server.id).user.avatar_url)
       
        help.description='Welcome to the help!\n Simply do '+server_key+'help (category) or (command name).'
        help.add_field(name='Command categories',value = ', '.join(categories))
        help.add_field(name="Links",value = ( "Official site: https://dueutil.tech/"
                                              +"\nOfficial server: https://discord.gg/ZzYvt8J"
                                              +"\nMrAwais' guide: http://dueutil.weebly.com/ (currenly outdated)"))
        help.set_footer(text="To use admin commands you must have the manage server permission or the 'Due Commander' role.")
      
    await util.say(ctx.channel,embed=help)

@commands.command(args_pattern=None)
async def dustats(ctx,*args,**details):
    
    
    """
    [CMD_KEY]dustats
    
    DueUtil's stats since the dawn of fucking time!
    """
    
    game_stats = stats.get_stats()
  
    stats_embed = discord.Embed(title="DueUtil's Stats",type="rich",color=16038978)
    
    stats_embed.description="DueUtil's global stats since the dawn of time"
    stats_embed.add_field(name="Images Served",
                          value = util.format_number(game_stats.get(Stat.IMAGES_SERVED.value,0),full_precision=True))
    stats_embed.add_field(name="Awarded",
                          value = util.format_number(game_stats.get(Stat.MONEY_CREATED.value,0),full_precision=True,money=True))
    stats_embed.add_field(name="Players have transferred",
                          value = util.format_number(game_stats.get(Stat.MONEY_TRANSFERRED.value,0),full_precision=True,money=True))
    stats_embed.add_field(name="Quests Given",
                          value = util.format_number(game_stats.get(Stat.QUESTS_GIVEN.value,0),full_precision=True))
    stats_embed.add_field(name="Quests Attempted",
                          value = util.format_number(game_stats.get(Stat.QUESTS_ATTEMPTED.value,0),full_precision=True))
    stats_embed.add_field(name="Level Ups",
                          value = util.format_number(game_stats.get(Stat.PLAYERS_LEVELED.value,0),full_precision=True))
    stats_embed.add_field(name="New Players",
                          value = util.format_number(game_stats.get(Stat.NEW_PLAYERS_JOINED.value,0),full_precision=True))
    stats_embed.set_footer(text="DueUtil Shard \""+str(util.get_client(ctx.server.id).name)+"\"")
    
    await util.say(ctx.channel,embed=stats_embed)

@commands.command(permission = Permission.SERVER_ADMIN, args_pattern="S")
async def setcmdkey(ctx,*args,**details):
    
    """
    [CMD_KEY]setcmdkey
    
    Sets the prefix for commands on your server.
    The default is '!'
    """
    
    new_key = args[0]
    if len(new_key) in (1,2):
        dueserverconfig.server_cmd_key(ctx.server,new_key)
        await util.say(ctx.channel,"Command preix on **"+details["server_name_clean"]+"** set to ``"+new_key+"``!")
    else:
        raise util.DueUtilException(ctx.channel,"Command prefixes can only be one or two characters!")
    
@commands.command(permission = Permission.SERVER_ADMIN, args_pattern="S?")
async def shutupdue(ctx,*args,**details):
    
    """
    [CMD_KEY]shutupdue 
    
    Mutes DueUtil in the channel the command is used in.
    By default the ``[CMD_KEY]shutupdue`` will stop alerts (level ups, ect)
    using ``[CMD_KEY]shutupdue all`` will make DueUtil ignore all commands
    from non-admins.
  
    """
    
    if len(args) == 0:
        mute_success = dueserverconfig.mute_channel(ctx.channel)
        if mute_success:
            await util.say(ctx.channel,(":mute: I won't send any alerts in this channel!\n"
                                        +"If you meant to disable commands too do ``"+details["cmd_key"]+"shutupdue all``."))
        else:
            await util.say(ctx.channel,(":mute: I've already been set not to send alerts in this channel!\n"
                                     +"If you want to disable commands too do ``"+details["cmd_key"]+"shutupdue all``.\n"
                                     +"To unmute me do ``"+details["cmd_key"]+"unshutupdue``."))
    else:
        mute_level = args[0].lower()
        if mute_level == "all":
            mute_success = dueserverconfig.mute_channel(ctx.channel,mute_all=True)
            if mute_success:
                await util.say(ctx.channel,(":mute: Disabled all commands in this channel for non-admins!"))
            else:
                await util.say(ctx.channel,(":mute: Already mute af in this channel!.\n"
                                         +"To allow commands & alerts again do ``"+details["cmd_key"]+"unshutupdue``."))
        else:
            await util.say(ctx.channel,":thinking: If you wanted to mute all the command is ``"+details["cmd_key"]+"shutupdue all``.")
            
@commands.command(permission = Permission.SERVER_ADMIN, args_pattern=None)
async def unshutupdue(ctx,*args,**details):
    if dueserverconfig.unmute_channel(ctx.channel):
        await util.say(ctx.channel,":speaker: Okay! I'll once more send alerts and listen for commands in this channel!")
    else:
        await util.say(ctx.channel,":thinking: Okay... I'm unmuted but I was not muted anyway.")

@commands.command(permission = Permission.SERVER_ADMIN, args_pattern="S*")
async def whitelist(ctx,*args,**details):

    """
    [CMD_KEY]whitelist
    
    Choose what DueUtil commands you want to allow in a channel.
    E.g. ``[CMD_KEY]whitelist help battle shop myinfo info``
    
    Normal users will not be able to use any other commands than the ones you
    choose.
    The whitelist does not effect server admins.
    
    To reset the whitelist run the command with no arguments.
    """
    
    if len(args) > 0:
        due_commands = events.command_event.command_list()
        whitelisted_commands = set([command.lower() for command in args])
        if whitelisted_commands.issubset(due_commands):
            dueserverconfig.set_command_whitelist(ctx.channel,list(whitelisted_commands))
            await util.say(ctx.channel,(":notepad_spiral: Whitelist in this channel set to the following commands: ``"
                                        +', '.join(whitelisted_commands)+"``"))
        else:
            incorrect_commands = whitelisted_commands.difference(due_commands)
            await util.say(ctx.channel,(":confounded: Cannot set whitelist! The following commands don't exist: ``"
                                        +', '.join(incorrect_commands)+"``"))
    else:
        dueserverconfig.set_command_whitelist(ctx.channel,[])
        await util.say(ctx.channel,":pencil: Command whitelist set back to all commands.")

@commands.command(permission = Permission.SERVER_ADMIN, args_pattern="S*")
async def blacklist(ctx,*args,**details):
  
    """
    [CMD_KEY]blacklist
    
    Choose what DueUtil commands you want to ban in a channel.
    E.g. ``[CMD_KEY]blacklist acceptquest battleme sell``
    
    Normal users will only be able to use commands not in the blacklist.
    The blacklist does not effect server admins.
    
    To reset the blacklist run the command with no arguments.
    
    The blacklist is not independent from the whitelist.
    """
    
    if len(args) > 0:
        due_commands = events.command_event.command_list()
        blacklisted_commands = set([command.lower() for command in args])
        if blacklisted_commands.issubset(due_commands):
            whitelisted_commands = list(set(due_commands).difference(blacklisted_commands))
            whitelisted_commands.append("is_blacklist")
            dueserverconfig.set_command_whitelist(ctx.channel,whitelisted_commands)
            await util.say(ctx.channel,(":notepad_spiral: Blacklist in this channel set to the following commands: ``"
                                        +', '.join(blacklisted_commands)+"``"))
        else:
            incorrect_commands = blacklisted_commands.difference(due_commands)
            await util.say(ctx.channel,(":confounded: Cannot set blacklist! The following commands don't exist: ``"
                                        +', '.join(incorrect_commands)+"``"))
    else:
        dueserverconfig.set_command_whitelist(ctx.channel,[])
        await util.say(ctx.channel,":pencil: Command blacklist removed.")  
  
