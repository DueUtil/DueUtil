import discord
import random

import dueutil.game.awards as game_awards
import generalconfig as gconf
from ..game import players, customizations
from ..game import stats, game
from ..game.helpers import misc, playersabstract, imagehelper
from .. import commands, util, dbconn

DAILY_AMOUNT = 50
TRAIN_RANGE = (0.1, 0.2)


@commands.command(args_pattern=None)
@commands.ratelimit(cooldown=86400, error="You can't collect your daily reward again for **[COOLDOWN]**!", save=True)
async def daily(ctx, **details):
    """
    [CMD_KEY]daily

    ¤50! Your daily pocket money!

    You can use this command once very 24 hours!
    """

    player = details["author"]
    player.money += DAILY_AMOUNT
    player.save()
    await util.say(ctx.channel, ":moneybag: **%s** collected their daily ¤%d!" % (player, DAILY_AMOUNT))


@commands.command(args_pattern=None)
@commands.ratelimit(cooldown=21600,
                    error="You've done all the training you can for now! You can train again in **[COOLDOWN]**!",
                    save=True)
async def train(ctx, **details):
    """
    [CMD_KEY]train

    Train to get a little exp to help you with quests.

    This will never give you much exp! But should help you out with quests early on!

    You can use this command once every 6 hours!
    """

    player = details["author"]

    attack_increase = random.uniform(*TRAIN_RANGE)
    strg_increase = random.uniform(*TRAIN_RANGE)
    accy_increase = random.uniform(*TRAIN_RANGE)
    player.progress(attack_increase, strg_increase, accy_increase,
                    max_exp=100, max_attr=0.3)
    progress_message = ":crossed_swords:+%.2f:muscle:+%.2f:dart:+%.2f"\
                       % (attack_increase, strg_increase, accy_increase)
    await game.check_for_level_up(ctx, player)
    player.save()
    await util.say(ctx.channel, "**%s** training complete!\n%s" % (player, progress_message))


@commands.command(args_pattern=None)
async def mylimit(ctx, **details):
    """
    [CMD_KEY]mylimit

    Shows the weapon price you're limited to.
    """

    player = details["author"]
    await util.say(ctx.channel, "You're currently limited to weapons with a value up to **%s**!"
                                % util.format_number(player.item_value_limit, money=True, full_precision=True))


@commands.command(args_pattern="S?")
async def battlename(ctx, name="", **details):
    """
    [CMD_KEY]battlename (name)
    
    Sets your name in DueUtil.
    To reset your name to your discord name run the
    command with no arguments
    
    """

    player = details["author"]
    if name != "":
        name_len_range = players.Player.NAME_LENGTH_RANGE
        if len(name) not in name_len_range:
            raise util.DueUtilException(ctx.channel, ("Battle name must be between **"
                                                      + str(min(name_len_range)) + "-" + str(
                                                        max(name_len_range)) + "** characters long!"))
        player.name = name
    else:
        player.name = details["author_name"]
    player.save()
    await util.say(ctx.channel, "Your battle name has been set to **" + player.name_clean + "**!")


@commands.command(args_pattern=None)
@commands.imagecommand()
async def myinfo(ctx, **details):
    """
    [CMD_KEY]myinfo
    
    Shows your info!
    
    """

    await imagehelper.stats_screen(ctx.channel, details["author"])


@commands.command(args_pattern=None)
async def myprofile(ctx, **details):
    """
    [CMD_KEY]myprofile

    Gives the link to your dueutil.tech profile
    """

    player = details["author"]

    private_record = dbconn.conn()["public_profiles"].find_one({"_id": player.id})

    if private_record is None or private_record["private"]:
        await util.say(ctx.channel, (":lock: Your profile is currently set to private!\n"
                                     + "If you want a public profile login to <https://dueutil.tech/>"
                                     + " and make your profile public."))
    else:
        await util.say(ctx.channel, "Your profile is at https://dueutil.tech/player/id/%s" % player.id)


@commands.command(args_pattern='P')
@commands.imagecommand()
async def info(ctx, player, **details):
    """
    [CMD_KEY]info @player
    
    Shows the info of another player!
    
    """

    await imagehelper.stats_screen(ctx.channel, player)


async def show_awards(ctx, player, page=0, **options):

    if page > len(player.awards) // 5:
        raise util.DueUtilException(ctx.channel, "Page not found")

    await imagehelper.awards_screen(ctx.channel, player, page, **options)


@commands.command(args_pattern='C?')
@commands.imagecommand()
async def myawards(ctx, page=1, **details):
    """
    [CMD_KEY]myawards (page number)
    
    Shows your awards!
    
    """

    await show_awards(ctx, details["author"], page-1, is_player_sender=True)


@commands.command(args_pattern='PC?')
@commands.imagecommand()
async def awards(ctx, player, page=1, **details):
    """
    [CMD_KEY]awards @player (page number)
    
    Shows a players awards!
    
    """

    await show_awards(ctx, player, page-1)


@commands.command(args_pattern="S?")
async def resetme(ctx, cnf="", **details):
    """
    [CMD_KEY]resetme
    
    Resets all your stats & any customization.
    This cannot be reversed!
    
    """
    if cnf.lower() == "cnf":
        player = details["author"]
        player.reset(ctx.author)
        await util.say(ctx.channel, "Your user has been reset.")
    else:
        await util.say(ctx.channel, ("Are you sure?! This will **__permanently__** reset your user!"
                                     + "\nDo ``" + details["cmd_key"] + "resetme cnf`` if you're sure!"))


@commands.command(args_pattern='PCS?')
async def sendcash(ctx, receiver, transaction_amount, message="", **details):
    """
    [CMD_KEY]sendcash @player amount (optional message)
    
    Sends some cash to another player.
    Note: The maximum amount someone can receive is ten times their limit.
    
    Example usage:
    
    [CMD_KEY]sendcash @MacDue 1000000 "for the lit bot fam"
    
    or
    
    [CMD_KEY]sendcash @MrAwais 1
    
    """

    sender = details["author"]
    amount_string = util.format_number(transaction_amount, money=True, full_precision=True)

    if receiver.id == sender.id:
        raise util.DueUtilException(ctx.channel, "There is no reason to send money to yourself!")

    if sender.money - transaction_amount < 0:
        if sender.money > 0:
            await util.say(ctx.channel, ("You do not have **" + amount_string + "**!\n"
                                                                                "The maximum you can transfer is **"
                                         + util.format_number(sender.money, money=True, full_precision=True) + "**"))
        else:
            await util.say(ctx.channel, "You do not have any money to transfer!")
        return

    max_receive = int(receiver.item_value_limit * 10)

    if transaction_amount > max_receive:
        await util.say(ctx.channel, ("**" + amount_string
                                     + "** is more than ten times **" + receiver.name_clean
                                     + "**'s limit!\nThe maximum **" + receiver.name_clean
                                     + "** can receive is **"
                                     + util.format_number(max_receive, money=True, full_precision=True) + "**!"))
        return

    sender.money -= transaction_amount
    receiver.money += transaction_amount

    sender.save()
    receiver.save()

    stats.increment_stat(stats.Stat.MONEY_TRANSFERRED, transaction_amount)
    if transaction_amount >= 50:
        await game_awards.give_award(ctx.channel, sender, "SugarDaddy", "Sugar daddy!")

    transaction_log = discord.Embed(title=":money_with_wings: Transaction complete!", type="rich",
                                    color=gconf.EMBED_COLOUR)
    transaction_log.add_field(name="Sender:", value=sender.name_clean)
    transaction_log.add_field(name="Recipient:", value=receiver.name_clean)
    transaction_log.add_field(name="Transaction amount (DUT):", value=amount_string, inline=False)
    if message != "":
        transaction_log.add_field(name=":pencil: Attached note:", value=message, inline=False)
    transaction_log.set_footer(text="Please keep this receipt for your records.")

    await util.say(ctx.channel, embed=transaction_log)


@commands.command(hidden=True, args_pattern=None)
async def benfont(ctx, **details):
    """
    [CMD_KEY]benfont 
    
    Shhhhh...
    
    """

    player = details["author"]
    player.benfont = not player.benfont
    player.save()
    if player.benfont:
        await util.get_client(ctx.server.id).send_file(ctx.channel, 'assets/images/nod.gif')
        await game_awards.give_award(ctx.channel, player, "BenFont", "ONE TRUE *type* FONT")


"""
WARNING: Setter & my commands use decorators to be lazy

Setters just return the item type & inventory slot. (could be done without
the decorators but setters must be fucntions anyway to be commands)

This is part of my quest in finding lazy ways to do things I cba.
"""


# Think about clean up & reuse
@commands.command(args_pattern='M?')
@playersabstract.item_preview
def mythemes(player):
    """
    [CMD_KEY]mythemes (optional theme name)
    
    Shows the amazing themes you can use on your profile.
    If you use this command with a theme name you can get a preview of the theme!
    
    """

    return {"thing_type": "theme",
            "thing_list": list(player.get_owned_themes().values()),
            "thing_lister": theme_page,
            "my_command": "mythemes",
            "thing_info": theme_info,
            "thing_getter": customizations.get_theme}


@commands.command(args_pattern='S')
@playersabstract.item_setter
def settheme():
    """
    [CMD_KEY]settheme (theme name)
    
    Sets your profile theme
    
    """

    return {"thing_type": "theme", "thing_inventory_slot": "themes"}


@commands.command(args_pattern='M?')
@playersabstract.item_preview
def mybgs(player):
    """
    [CMD_KEY]mybgs (optional background name)
    
    Shows the backgrounds you've bought!
    
    """

    return {"thing_type": "background",
            "thing_list": list(player.get_owned_backgrounds().values()),
            "thing_lister": background_page,
            "my_command": "mybgs",
            "thing_info": background_info,
            "thing_getter": customizations.get_background}


@commands.command(args_pattern='S')
@playersabstract.item_setter
def setbg():
    """
    [CMD_KEY]setbg (background name)
    
    Sets your profile background
    
    """

    return {"thing_type": "background", "thing_inventory_slot": "backgrounds"}


@commands.command(args_pattern='M?')
@playersabstract.item_preview
def mybanners(player):
    """
    [CMD_KEY]mybanners (optional banner name)
    
    Shows the banners you've bought!
    
    """
    return {"thing_type": "banner",
            "thing_list": list(player.get_owned_banners().values()),
            "thing_lister": banner_page,
            "my_command": "mybanners",
            "thing_info": banner_info,
            "thing_getter": customizations.get_banner}


@commands.command(args_pattern='S')
@playersabstract.item_setter
def setbanner():
    """
    [CMD_KEY]setbanner (banner name)
    
    Sets your profile banner
    
    """

    return {"thing_type": "banner", "thing_inventory_slot": "banners"}


# Part of the shop buy command
@misc.paginator
def theme_page(themes_embed, theme, **extras):
    price_divisor = extras.get('price_divisor', 1)
    themes_embed.add_field(name=theme["icon"] + " | " + theme["name"], value=(theme["description"] + "\n ``"
                                                                              + util.format_number(
        theme["price"] // price_divisor, money=True, full_precision=True) + "``"))


@misc.paginator
def background_page(backgrounds_embed, background, **extras):
    price_divisor = extras.get('price_divisor', 1)
    backgrounds_embed.add_field(name=background["icon"] + " | " + background["name"],
                                value=(background["description"] + "\n ``"
                                       + util.format_number(background["price"] // price_divisor, money=True,
                                                            full_precision=True) + "``"))


@misc.paginator
def banner_page(banners_embed, banner, **extras):
    price_divisor = extras.get('price_divisor', 1)
    banners_embed.add_field(name=banner.icon + " | " + banner.name,
                            value=(banner.description + "\n ``"
                                                      + util.format_number(banner.price // price_divisor,
                                                                           money=True, full_precision=True) + "``"))


def theme_info(theme_name, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    theme = details.get('theme', customizations.get_theme(theme_name))
    embed.title = str(theme)
    embed.set_image(url=theme["preview"])
    embed.set_footer(text="Buy this theme for " + util.format_number(theme["price"] // price_divisor, money=True,
                                                                     full_precision=True))
    return embed


def background_info(background_name, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    background = customizations.get_background(background_name)
    embed.title = str(background)
    embed.set_image(url="https://dueutil.tech/duefiles/backgrounds/" + background["image"])
    embed.set_footer(
        text="Buy this background for " + util.format_number(background["price"] // price_divisor, money=True,
                                                             full_precision=True))
    return embed


def banner_info(banner_name, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    banner = customizations.get_banner(banner_name)
    embed.title = str(banner)
    if banner.donor:
        embed.description = ":star2: This is a __donor__ banner!"
    embed.set_image(url="https://dueutil.tech/duefiles/banners/" + banner.image_name)
    embed.set_footer(text="Buy this banner for " + util.format_number(banner.price // price_divisor, money=True,
                                                                      full_precision=True))
    return embed
