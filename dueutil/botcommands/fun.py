import math
from datetime import datetime

import discord
import repoze.timeago

import generalconfig as gconf
from .. import commands, util, dbconn
from ..game import awards, players, leaderboards
from ..game.helpers import misc, imagehelper


async def glitter_text(channel, text):
    gif_text = await misc.get_glitter_text(text)
    await util.get_client(channel).send_file(channel, fp=gif_text,
                                             filename="glittertext.gif",
                                             content=":sparkles: Your glitter text!")


@commands.command(args_pattern='S')
@commands.imagecommand()
async def glitter(ctx, text, **details):
    """
    [CMD_KEY]glitter(text)
    
    Creates a glitter text gif!
    
    (Glitter text from http://www.gigaglitters.com/)
    """
    details["author"].misc_stats["art_created"] += 1
    await glitter_text(ctx.channel, text)


@commands.command(args_pattern="S?")
@commands.imagecommand()
async def eyes(ctx, eye_description="", **details):
    """
    [CMD_KEY]eyes modifiers
    
    __Modifiers:__
        snek - Snek eyes (slits)
        ogre - Ogre colours
        evil - Red eyes
        gay  - Pink stuff
        high - Large pupils + red eyes
        emoji - emoji size + no border
        small - Small size (larger than emoji)
        left - Eyes look left
        right - Eyes look right
        top - Eyes look to the top
        bottom - Eyes look to the bottom
        derp - Random pupil positions
        bottom left - Eyes look bottom left
        bottom right - Eyes look bottom right
        top right - Eyes look top right
        top left - Eyes look top left
        no modifiers - Procedurally generated eyes!!!111
    """
    details["author"].misc_stats["art_created"] += 1
    await imagehelper.googly_eyes(ctx.channel, eye_description)


@commands.command(args_pattern="C?")
async def leaderboard(ctx, page=1, **details):
    """
    [CMD_KEY]leaderboard (page)
    
    The global leaderboard of DueUtil!
    
    The leaderboard updated every hour.
    
    Bet someone's gonna whine about there not being a server leaderboard now.
    Don't worry I'll add one if there is demand.
    
    """

    page_size = 10
    # Subtract one as the count arg type starts at 1 not zero.
    page -= 1

    leaderboard_embed = discord.Embed(title="DueUtil Leaderboard", type="rich", color=gconf.EMBED_COLOUR)

    player_leaderboard = leaderboards.get_leaderboard("levels")
    if player_leaderboard is not None:

        leaderboard_data = player_leaderboard[0]

        if page > 0:
            leaderboard_embed.title += ": Page " + str(page + 1)
        if page * page_size >= len(leaderboard_data):
            raise util.DueUtilException(ctx.channel, "Page not found")

        index = 0
        for index in range(page_size * page, page_size * page + page_size):
            if index >= len(leaderboard_data):
                break
            bonus = ""
            if index == 0:
                bonus = "     :first_place:"
            elif index == 1:
                bonus = "     :second_place:"
            elif index == 2:
                bonus = "     :third_place:"
            player = leaderboard_data[index]
            name = player.name_clean
            player_id = "<@" + player.id + ">"
            level = str(math.trunc(player.level))
            leaderboard_embed.add_field(name="#" + str(index + 1) + bonus,
                                        value=(name + " " + player_id + " ``Level " + level + "``"
                                               + " ``Total Exp: " + str(math.trunc(player.total_exp))) + "``",
                                        inline=False)
            last_updated = datetime.utcfromtimestamp(leaderboards.last_leaderboard_update)
            leaderboard_embed.set_footer(text="Leaderboard calculated " + repoze.timeago.get_elapsed(last_updated))
        if index < len(leaderboard_data) - 1:
            leaderboard_embed.add_field(name="+" + str(len(leaderboard_data) - (page_size * (page + 1))) + " more!",
                                        value="Do ``" + details["cmd_key"] + "leaderboard " + str(
                                            page + 2) + "`` for the next page!", inline=False)
    else:
        leaderboard_embed.set_image(url="http://i.imgur.com/KQd9EJ9.gif")
        leaderboard_embed.add_field(name="Sorry", value=("The leaderboard has yet to be calculated!\n"
                                                         + "Check again soon!"))
    await util.say(ctx.channel, embed=leaderboard_embed)


@commands.command(args_pattern=None)
async def myrank(ctx, **details):
    """
    [CMD_KEY]myrank
    
    Tells you where you are in the [CMD_KEY]leaderboard. 
    """

    player = details["author"]
    try:
        leaderboard_data = leaderboards.get_leaderboard("levels")[0]
        position = leaderboard_data.index(player)
        page = position // 10
        await util.say(ctx.channel, (":sparkles: You're position **" + str(position + 1) + "** on the leaderboard!\n"
                                     + "That's on ``" + details["cmd_key"]
                                     + "leaderboard`` page " + str(page + 1) + "!"))
    except (IndexError, ValueError):
        await util.say(ctx.channel, (":confounded: I can't find you in the leaderboard!?\n"
                                     + "This probably means you're new and leaderboard has not updated yet!"))


async def give_emoji(channel, sender, receiver, emoji):
    if not util.char_is_emoji(emoji) and not util.is_server_emoji(channel.server, emoji):
        raise util.DueUtilException(channel, "You can only send emoji!")
    if sender == receiver:
        raise util.DueUtilException(channel, "You can't send a " + emoji + " to yourself!")
    await util.say(channel, "**" + receiver.name_clean + "** " + emoji + " :heart: **" + sender.name_clean + "**")


@commands.command(args_pattern='PS')
async def giveemoji(ctx, receiver, emoji, **details):
    """
    [CMD_KEY]giveemoji player emoji
    
    Give a friend an emoji.
    Why? Who knows.
    I'm sure you can have loads of game with the :cancer: emoji though!
    Also see ``[CMD_KEY]givepotato``
    
    """
    sender = details["author"]

    try:
        await give_emoji(ctx.channel, sender, receiver, emoji)
        sender.misc_stats["emojis_given"] += 1
        receiver.misc_stats["emojis"] += 1
    except util.DueUtilException as command_error:
        raise command_error
    await awards.give_award(ctx.channel, sender, "Emoji", ":fire: __Breakdown Of Society__ :city_dusk:")
    if emoji == "🍆":
        await awards.give_award(ctx.channel, sender, "Sauce", "*Saucy*")
    if sender.misc_stats["emojis_given"] == 100:
        await awards.give_award(ctx.channel, sender, "EmojiKing", ":biohazard: **__WIPEOUT HUMANITY__** :radioactive:")


@commands.command(args_pattern='P')
async def givepotato(ctx, receiver, **details):
    """
    [CMD_KEY]givepotato player
    
    Who doesn't like potatoes?
    """
    sender = details["author"]

    try:
        await give_emoji(ctx.channel, sender, receiver, '🥔')
        sender.misc_stats["potatoes_given"] += 1
        receiver.misc_stats["potatoes"] += 1
    except util.DueUtilException as command_error:
        raise command_error
    await awards.give_award(ctx.channel, sender, "Potato", ":potato: Bringer Of Potatoes :potato:")
    if sender.misc_stats["potatoes_given"] == 100:
        await awards.give_award(ctx.channel, sender, "KingTat", ":crown: :potato: **Potato King!** :potato: :crown:")


@commands.command(args_pattern=None)
async def topdog(ctx, **details):
    """
    [CMD_KEY]topdog

    View the "top dog"
    """
    top_dog_stats = awards.get_award_stat("TopDog")
    if top_dog_stats is not None and "top_dog" in top_dog_stats:
        top_dog = players.find_player(top_dog_stats["top_dog"])
        await util.say(ctx.channel, (":dog: The current top dog is **%s** (%s)!\n"
                                     + "They are the **%s** to earn the rank of top dog!")
                       % (top_dog, top_dog.id, util.int_to_ordinal(top_dog_stats["times_given"])))
    else:
        await util.say(ctx.channel, "There is not a top dog yet!")


@commands.command(args_pattern=None)
async def pandemic(ctx, **details):
    """
    [CMD_KEY]pandemic

    Tracks the current DueUtil pandemic.
    """
    virus_stats = awards.get_award_stat("Duerus")

    if virus_stats is None or virus_stats["times_given"] == 0:
        await util.say(ctx.channel, "All looks good now though a pandemic could break out any day.")
        return

    warning_symbols = {0: ":heart: - Healthy", 1: ":yellow_heart: - Worrisome", 2: ":black_heart: - Doomed"}
    thumbnails = {0: "http://i.imgur.com/NENJMOP.jpg",
                  1: "http://i.imgur.com/we6XgpG.gif",
                  2: "http://i.imgur.com/EJVYJ9C.gif"}

    total_players = dbconn.get_collection_for_object(players.Player).count()
    total_infected = virus_stats["times_given"]
    total_uninfected = total_players - total_infected
    percent_infected = (total_infected / total_players) * 100
    pandemic_level = percent_infected // 33
    pandemic_embed = discord.Embed(title=":biohazard: DueUtil Pandemic :biohazard:", type="rich",
                                   color=gconf.EMBED_COLOUR)
    pandemic_embed.set_thumbnail(url=thumbnails.get(pandemic_level, thumbnails[2]))
    pandemic_embed.description = "Monitoring the spread of the __loser__ pandemic."
    pandemic_embed.add_field(name="Pandemic stats", value=("Out of a total of **%s** players:\n"
                                                           + ":biohazard: **%s** are infected.\n"
                                                           + ":pill: **%s** are uninfected.\n\n"
                                                           + "This means **%.2g**%% of all players are infected!")
                                                          % (total_players, total_infected,
                                                             total_uninfected, percent_infected))
    pandemic_embed.add_field(name="Health level",
                             value=warning_symbols.get(pandemic_level, warning_symbols[2]))

    await util.say(ctx.channel, embed=pandemic_embed)
