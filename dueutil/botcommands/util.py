import discord
import aiohttp
import asyncio

import generalconfig as gconf
from ..game.configs import dueserverconfig
from ..permissions import Permission
from ..game import stats, awards, discoin
from ..game.stats import Stat
from .. import commands, events, util, permissions


@commands.command(permission=Permission.DISCORD_USER, args_pattern="S?", aliases=("helpme",))
async def help(ctx, *args, **details):
    """
    [CMD_KEY]help (command name or category)
    
    INCEPTION SOUND
    """

    help_logo = 'https://cdn.discordapp.com/attachments/173443449863929856/275299953528537088/helo_458x458.jpg'

    help_embed = discord.Embed(title="DueUtil's Help", type="rich", color=gconf.EMBED_COLOUR)
    server_key = details["cmd_key"]
    categories = events.command_event.category_list()

    if len(args) == 1:

        help_embed.set_thumbnail(url=help_logo)
        arg = args[0].lower()
        if arg not in categories:
            chosen_command = events.get_command(arg)
            # Dumb award
            if chosen_command is None:
                alias_count = 0
                if arg != "dumbledore":
                    command_name = 'Not found'
                    command_help = 'That command was not found!'
                else:
                    # Stupid award reference
                    command_name = 'dumbledore?!?'
                    command_help = 'Some stupid *joke?* reference to old due!!!111'
                    help_embed.set_image(url='http://i.imgur.com/UrWhI9P.gif')
                    await awards.give_award(ctx.channel, details["author"], "Daddy",
                                            "I have no memory of this award...")
            else:
                command_name = chosen_command.__name__
                alias_count = len(chosen_command.aliases)
                if chosen_command.__doc__ is not None:
                    command_help = chosen_command.__doc__.replace('[CMD_KEY]', server_key)
                else:
                    command_help = 'Sorry there is no help for that command!'

            help_embed.description = "Showing help for **" + command_name + "**"
            help_embed.add_field(name=command_name, value=command_help)
            if alias_count > 0:
                help_embed.add_field(name=("Alias" if alias_count == 1 else "Aliases"),
                                     value=', '.join(chosen_command.aliases), inline=False)
        else:
            category = arg
            help_embed.description = "Showing ``" + category + "`` commands."

            commands_for_all = events.command_event.command_list(
                filter=lambda command:
                    command.permission in (Permission.PLAYER, Permission.DISCORD_USER) and command.category == category)
            admin_commands = events.command_event.command_list(
                filter=lambda command:
                    command.permission == Permission.SERVER_ADMIN and command.category == category)
            server_op_commands = events.command_event.command_list(
                filter=lambda command:
                    command.permission == Permission.REAL_SERVER_ADMIN and command.category == category)

            if len(commands_for_all) > 0:
                help_embed.add_field(name='Commands for everyone', value=', '.join(commands_for_all), inline=False)
            if len(admin_commands) > 0:
                help_embed.add_field(name='Admins only', value=', '.join(admin_commands), inline=False)
            if len(server_op_commands) > 0:
                help_embed.add_field(name='Server managers only', value=', '.join(server_op_commands), inline=False)
    else:

        help_embed.set_thumbnail(url=util.get_client(ctx.server.id).user.avatar_url)

        help_embed.description = 'Welcome to the help!\n Simply do ' + server_key + 'help (category) or (command name).'
        help_embed.add_field(name='Command categories', value=', '.join(categories))
        help_embed.add_field(name="Tips", value=("If DueUtil reacts to your command it means something is wrong!\n"
                                                 + "\":question:\": Something is wrong with the commands syntax.\n"
                                                 + "\":x:\": You don't have the required permissions to use the command."))
        help_embed.add_field(name="Links", value=("**Invite me: %s**\n" % gconf.BOT_INVITE
                                                  + "DueUtil site: https://dueutil.tech/\n"
                                                  + "DueUtil guide: https://dueutil.tech/howto\n"
                                                  + "Support server: https://discord.gg/n4b94VA\n"))
        help_embed.set_footer(
            text="To use admin commands you must have the manage server permission or the 'Due Commander' role.")

    await util.say(ctx.channel, embed=help_embed)


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def botinfo(ctx,**_):

    """
    [CMD_KEY]botinfo

    General information about DueUtil.
    """

    info_embed = discord.Embed(title="DueUtil's Information", type="rich", color=gconf.EMBED_COLOUR)
    info_embed.description = "DueUtil is customizable bot to add fun commands, quests and battles to your server."
    info_embed.add_field(name="Created by", value="[MacDue#4453](https://dueutil.tech/)")
    info_embed.add_field(name="Framework",
                         value="[discord.py %s :two_hearts:](http://discordpy.readthedocs.io/en/latest/)"
                               % discord.__version__)
    info_embed.add_field(name="Version", value=gconf.VERSION),
    info_embed.add_field(name="Invite Due!", value="https://dueutil.tech/invite", inline=False)
    info_embed.add_field(name="Support server",
                         value="For help with the bot or a laugh join **https://discord.gg/n4b94VA**!")
    await util.say(ctx.channel, embed=info_embed)


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def prefix(ctx, **details):
    """
    ``@DueUtil``prefix

    Tells you what the prefix is on a server.
    """

    server_prefix = dueserverconfig.server_cmd_key(ctx.server)
    await util.say(ctx.channel, "The prefix on **%s** is ``%s``" % (details.get("server_name_clean"), server_prefix))


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def dustats(ctx, **_):
    """
    [CMD_KEY]dustats
    
    DueUtil's stats since the dawn of fucking time!
    """

    game_stats = stats.get_stats()

    stats_embed = discord.Embed(title="DueUtil's Stats", type="rich", color=gconf.EMBED_COLOUR)

    stats_embed.description = "DueUtil's global stats since the dawn of time"
    stats_embed.add_field(name=":frame_photo: Images Served",
                          value=util.format_number(game_stats.get(Stat.IMAGES_SERVED.value, 0), full_precision=True))
    stats_embed.add_field(name=":moneybag: Awarded",
                          value=util.format_number(game_stats.get(Stat.MONEY_CREATED.value, 0), full_precision=True,
                                                   money=True))
    stats_embed.add_field(name=":left_right_arrow: Players have transferred",
                          value=util.format_number(game_stats.get(Stat.MONEY_TRANSFERRED.value, 0), full_precision=True,
                                                   money=True))
    stats_embed.add_field(name=":crossed_swords: Quests Given",
                          value=util.format_number(game_stats.get(Stat.QUESTS_GIVEN.value, 0), full_precision=True))
    stats_embed.add_field(name=":fist: Quests Attempted",
                          value=util.format_number(game_stats.get(Stat.QUESTS_ATTEMPTED.value, 0), full_precision=True))
    stats_embed.add_field(name=":up: Level Ups",
                          value=util.format_number(game_stats.get(Stat.PLAYERS_LEVELED.value, 0), full_precision=True))
    stats_embed.add_field(name=":new: New Players",
                          value=util.format_number(game_stats.get(Stat.NEW_PLAYERS_JOINED.value, 0),
                                                   full_precision=True))
    stats_embed.add_field(name=":money_with_wings: Discoin Received",
                          value=util.format_number(game_stats.get(Stat.DISCOIN_RECEIVED.value, 0), full_precision=True))
    stats_embed.set_footer(text="DueUtil Shard \"" + str(util.get_client(ctx.server.id).name) + "\"")

    await util.say(ctx.channel, embed=stats_embed)


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def duservers(ctx, **_):
    """
    [CMD_KEY]duservers
    
    Shows the number of servers DueUtil is chillin on.
    
    """

    server_count = util.get_server_count()
    await util.say(ctx.channel, "DueUtil is active on **" + str(server_count) + " server"
                                + ("s" if server_count != 1 else "") + "**")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S", aliases=("setprefix",))
async def setcmdkey(ctx, new_key, **details):
    """
    [CMD_KEY]setcmdkey
    
    Sets the prefix for commands on your server.
    The default is '!'
    """

    if len(new_key) in (1, 2):
        dueserverconfig.server_cmd_key(ctx.server, new_key)
        await util.say(ctx.channel,
                       "Command prefix on **" + details["server_name_clean"] + "** set to ``" + new_key + "``!")
    else:
        raise util.DueUtilException(ctx.channel, "Command prefixes can only be one or two characters!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S?")
async def shutupdue(ctx, *args, **details):
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
            await util.say(ctx.channel, (":mute: I won't send any alerts in this channel!\n"
                                         + "If you meant to disable commands too do ``" + details[
                                             "cmd_key"] + "shutupdue all``."))
        else:
            await util.say(ctx.channel, (":mute: I've already been set not to send alerts in this channel!\n"
                                         + "If you want to disable commands too do ``" + details[
                                             "cmd_key"] + "shutupdue all``.\n"
                                         + "To unmute me do ``" + details["cmd_key"] + "unshutupdue``."))
    else:
        mute_level = args[0].lower()
        if mute_level == "all":
            mute_success = dueserverconfig.mute_channel(ctx.channel, mute_all=True)
            if mute_success:
                await util.say(ctx.channel, ":mute: Disabled all commands in this channel for non-admins!")
            else:
                await util.say(ctx.channel, (":mute: Already mute af in this channel!.\n"
                                             + "To allow commands & alerts again do ``" + details[
                                                 "cmd_key"] + "unshutupdue``."))
        else:
            await util.say(ctx.channel, ":thinking: If you wanted to mute all the command is ``" + details[
                "cmd_key"] + "shutupdue all``.")


@commands.command(permission=Permission.REAL_SERVER_ADMIN, args_pattern="S?")
async def leave(ctx, cnf="", **details):
    """
    [CMD_KEY]leave
    
    Makes DueUtil leave your server cleanly.
    This will delete all quests & weapons created
    on your server.
    
    This command can only be run by real server admins
    (you must have manage server permissions).
    
    """

    if cnf.lower() == "cnf":

        bye_embed = discord.Embed(title="Goodbye!", color=gconf.EMBED_COLOUR)
        bye_embed.set_image(url="http://i.imgur.com/N65P9gL.gif")
        await util.say(ctx.channel, embed=bye_embed)
        try:
            await util.get_client(ctx.server.id).leave_server(ctx.server)
        except:
            raise util.DueUtilException(ctx.channel, "Could not leave server!")
    else:
        await util.say(ctx.channel,
                       (":cry: You sure? The bot will leave your server and __**everything**__ will be reset!\n"
                        + "\nDo ``" + details["cmd_key"] + "leave cnf`` if you're sure!"))


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern=None)
async def unshutupdue(ctx, **_):
    if dueserverconfig.unmute_channel(ctx.channel):
        await util.say(ctx.channel,
                       ":speaker: Okay! I'll once more send alerts and listen for commands in this channel!")
    else:
        await util.say(ctx.channel, ":thinking: Okay... I'm unmuted but I was not muted anyway.")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S*")
async def whitelist(ctx, *args, **_):
    """
    [CMD_KEY]whitelist
    
    Choose what DueUtil commands you want to allow in a channel.
    E.g. ``[CMD_KEY]whitelist help battle shop myinfo info``
    
    Normal users will not be able to use any other commands than the ones you
    choose.
    The whitelist does not effect server admins.
    
    To reset the whitelist run the command with no arguments.

    Note: Whitelisting a command like !info will also whitelist !myinfo
    (since !info is mapped to !myinfo)
    """

    if len(args) > 0:
        due_commands = events.command_event.command_list(aliases=True)
        whitelisted_commands = set(commands.replace_aliases([command.lower() for command in args]))
        if whitelisted_commands.issubset(due_commands):
            dueserverconfig.set_command_whitelist(ctx.channel, list(whitelisted_commands))
            await util.say(ctx.channel, (":notepad_spiral: Whitelist in this channel set to the following commands: ``"
                                         + ', '.join(whitelisted_commands) + "``"))
        else:
            incorrect_commands = whitelisted_commands.difference(due_commands)
            await util.say(ctx.channel, (":confounded: Cannot set whitelist! The following commands don't exist: ``"
                                         + ', '.join(incorrect_commands) + "``"))
    else:
        dueserverconfig.set_command_whitelist(ctx.channel, [])
        await util.say(ctx.channel, ":pencil: Command whitelist set back to all commands.")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S*")
async def blacklist(ctx, *args, **_):
    """
    [CMD_KEY]blacklist
    
    Choose what DueUtil commands you want to ban in a channel.
    E.g. ``[CMD_KEY]blacklist acceptquest battleme sell``
    
    Normal users will only be able to use commands not in the blacklist.
    The blacklist does not effect server admins.
    
    To reset the blacklist run the command with no arguments.
    
    The blacklist is not independent from the whitelist.

    Note: Blacklisting a command like !info will also blacklist !myinfo
    (since !info is mapped to !myinfo)
    """

    if len(args) > 0:
        due_commands = events.command_event.command_list(aliases=True)
        blacklisted_commands = set(commands.replace_aliases([command.lower() for command in args]))
        if blacklisted_commands.issubset(due_commands):
            whitelisted_commands = list(set(due_commands).difference(blacklisted_commands))
            whitelisted_commands.append("is_blacklist")
            dueserverconfig.set_command_whitelist(ctx.channel, whitelisted_commands)
            await util.say(ctx.channel, (":notepad_spiral: Blacklist in this channel set to the following commands: ``"
                                         + ', '.join(blacklisted_commands) + "``"))
        else:
            incorrect_commands = blacklisted_commands.difference(due_commands)
            await util.say(ctx.channel, (":confounded: Cannot set blacklist! The following commands don't exist: ``"
                                         + ', '.join(incorrect_commands) + "``"))
    else:
        dueserverconfig.set_command_whitelist(ctx.channel, [])
        await util.say(ctx.channel, ":pencil: Command blacklist removed.")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern=None)
async def setuproles(ctx, **_):
    """
    [CMD_KEY]setuproles
    
    Creates any discord roles DueUtil needs. These will have been made when
    DueUtil joined your server but if you deleted any & need them you'll 
    want to run this command.
    
    """
    server = ctx.server
    if not any(role.name == "Due Commander" for role in server.roles):
        await util.get_client(ctx).create_role(server, name="Due Commander", color=discord.Color(gconf.EMBED_COLOUR))
        await util.say(ctx.channel, ":white_check_mark: Created ``Due Commander`` role!")
    else:
        await util.say(ctx.channel, "No roles need to be created!")


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def optout(ctx, **details):

    """
    [CMD_KEY]optout

    Opt out of DueUtil.

    When you opt out:
        You don't get quests or exp.
        Other players can't use you in commands.
        You lose access to all "game" commands.

    Server admins (that opt out) still have access to admin commands.

    (This applies to all servers with DueUtil)
    """

    player = details["author"]
    if player.is_playing():
        current_permission = permissions.get_special_permission(ctx.author)
        if "TopDog" in player.awards:
            await util.say(ctx.channel, (":dog: You cannot opt out while you're top dog!\n"
                                         + "Pass on the title before you leave us!"))
            return
        if current_permission >= Permission.DUEUTIL_MOD:
            raise util.DueUtilException(ctx.channel, "You cannot opt out and stay a dueutil mod or admin!")
        permissions.give_permission(ctx.author, Permission.DISCORD_USER)
        await util.say(ctx.channel, (":ok_hand: You've opted out of DueUtil.\n"
                                     + "You won't get exp, quests, and other players can't use you in commands."))
    else:
        await util.say(ctx.channel, ("You've already opted out!\n"
                                     + "You can join the fun again with %soptin." % details["cmd_key"]))


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def optin(ctx, **details):

    """
    [CMD_KEY]optin

    Opt in to DueUtil.

    (This applies to all servers with DueUtil)
    """

    player = details["author"]
    if player.is_playing():
        await util.say(ctx.channel, "You've already opted in!")
    else:
        permissions.give_permission(ctx.author, Permission.PLAYER)
        await util.say(ctx.channel, "You've opted in!\n"
                                    + "Glad to have you back.")


@commands.command(args_pattern="CS")
async def exchange(ctx, amount, currency, **details):

    """
    [CMD_KEY]exchange (amount) (currency)

    Exchange your DUT (DueUtil Tokens) for other bot currencies!

    For more information go to: https://discoin.disnodeteam.com/

    Note: Exchanges can take a few minutes to process!
    """

    player = details["author"]
    currency = currency.upper()

    if currency == "DUT":
        raise util.DueUtilException(ctx.channel, "There is no reason to exchange DUT for DUT!")

    if player.money - amount < 0:
        if player.money - amount > 0:
            await util.say(ctx.channel, "You do not have **%s**!\n"
                                        % util.format_number(amount, full_precision=True, money=True)
                                        + "The maximum you can exchange is **%s**"
                                        % util.format_number(player.money, full_precision=True, money=True))
        else:
            await util.say(ctx.channel, "You don't have any money to exchange!")
        return

    try:
        result = await discoin.start_transaction(player.id, amount, currency)
    except Exception as discoin_error:
        util.logger.error("Discoin exchange failed %s", discoin_error)
        raise util.DueUtilException(ctx.channel, "Something went wrong at Discoin!")

    if "error" in result:
        # Error
        error = result
        if "verify" in error:
            await util.say(ctx.channel, "You must verify at <%s> to use Discoin!" % error["verify"])
        elif error.get("error") == "currency_not_found":
            await util.say(ctx.channel, "The currency you tried exchange to does not exist!")
        else:
            raise util.DueUtilException(ctx.channel, "An unexpected error occurred!")
    else:
        transaction = result
        status = transaction.get("status").lower().strip()
        if status == "declined":
            # Declined
            limit = transaction.get("limit", transaction.get("limitTotal"))
            limit_type = "total" if "limitTotal" in transaction else "daily"
            await util.say(ctx.channel, "Your transaction exceeds your %s limit of **Đ%s** for **%s**"
                                        % (limit_type, util.format_number(limit, full_precision=True), currency))
        elif status == "approved":
            # Success
            await awards.give_award(ctx.channel, player, "Discoin")
            player.money -= amount
            player.save()
            limit_now = int(transaction["limitNow"])
            receipt = transaction["receipt"]
            exchange_embed = discord.Embed(title=":money_with_wings: Exchange complete!",
                                           type="rich", color=gconf.EMBED_COLOUR)
            exchange_embed.add_field(name="Exchange amount (DUT):",
                                     value=util.format_number(amount, money=True, full_precision=True))
            exchange_embed.add_field(name="Receipt:", value=receipt)
            exchange_embed.add_field(name="Daily exchange limit to %s left:" % currency,
                                     value="Đ"+util.format_number(limit_now, full_precision=True), inline=False)
            exchange_embed.set_footer(text="Keep the receipt for if something goes wrong!")
            await util.say(ctx.channel, embed=exchange_embed)
        else:
            raise util.DueUtilException(ctx.channel, "Something unexpected happened!")
