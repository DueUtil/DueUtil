import math
import time
from collections import OrderedDict

import discord

import generalconfig as gconf
from dueutil.game.helpers import imagehelper
from dueutil.permissions import Permission
from ..game import (
    quests,
    game,
    battles,
    weapons,
    stats,
    awards)
from .. import commands, util


@commands.command(permission=Permission.DUEUTIL_MOD, args_pattern="S?P?C?I?I?R?", hidden=True)
async def spawnquest(ctx, *args, **details):
    """
    [CMD_KEY]spawnquest (name) (@user) (level) (money,wep damage,wep accy)
    
    A command for TESTING only please (awais) do not abuse this power.
    All arguments are optional however the final three must all be entered
    to use them. 
    
    """

    player = details["author"]
    if len(args) == 0:
        quest = quests.get_random_quest_in_channel(ctx.channel)
    else:
        if len(args) >= 2:
            player = args[1]
        quest_name = args[0].lower()
        quest = quests.get_quest_from_id(ctx.server.id + "/" + quest_name)
    try:
        active_quest = quests.ActiveQuest(quest.q_id, player)
        if len(args) >= 3:
            active_quest.level = args[2]
            spoofs = args[3:]
            spoof_values = {}
            if len(spoofs) == 3:
                spoof_values = {'q_stats': spoofs[0], 'w_damage': spoofs[1], 'w_accy': spoofs[2]}
            active_quest._calculate_stats(**spoof_values)
        player.save()
        await util.say(ctx.channel,
                       ":cloud_lightning: Spawned **" + quest.name_clean + "** [Level " + str(active_quest.level) + "]")
    except:
        raise util.DueUtilException(ctx.channel, "Failed to spawn quest!")


@commands.command(args_pattern='C')
@commands.imagecommand()
async def questinfo(ctx, *args, **details):
    """
    [CMD_KEY]questinfo index
    
    Shows a simple stats page for the quest
    """

    player = details["author"]
    quest_index = args[0] - 1
    if 0 <= quest_index < len(player.quests):
        await imagehelper.quest_screen(ctx.channel, player.quests[quest_index])
    else:
        raise util.DueUtilException(ctx.channel, "Quest not found!")


@commands.command(args_pattern='C?')
@commands.imagecommand()
async def myquests(ctx, *args, **details):
    """
    [CMD_KEY]myquests
    
    Shows the list of active quests you have pending.
    
    """

    player = details["author"]
    if len(args) == 0:
        page = 0
    else:
        page = args[0] - 1
    if page > len(player.quests) // 5:
        raise util.DueUtilException(ctx.channel, "Page not found")
    await imagehelper.quests_screen(ctx.channel, player, page)


@commands.command(args_pattern='C')
@commands.imagecommand()
async def acceptquest(ctx, *args, **details):
    """
    [CMD_KEY]acceptquest (quest number)

    You know what to do. Spam ``[CMD_KEY]acceptquest 1``!
    
    """

    player = details["author"]
    quest_index = args[0] - 1
    if quest_index >= len(player.quests):
        raise util.DueUtilException(ctx.channel, "Quest not found!")
    if player.money - player.quests[quest_index].money // 2 < 0:
        raise util.DueUtilException(ctx.channel, "You can't afford the risk!")
    if player.quests_completed_today >= quests.MAX_DAILY_QUESTS:
        raise util.DueUtilException(ctx.channel,
                                    "You can't do more than " + str(quests.MAX_DAILY_QUESTS) + " quests a day!")

    quest = player.quests.pop(quest_index)
    battle_log = battles.get_battle_log(player_one=player, player_two=quest, p2_prefix="the ")
    battle_embed = battle_log.embed
    turns = battle_log.turn_count
    winner = battle_log.winner
    stats.increment_stat(stats.Stat.QUESTS_ATTEMPTED)
    # Not really an average (but w/e)
    average_quest_battle_turns = player.misc_stats["average_quest_battle_turns"] = (player.misc_stats[
                                                                                        "average_quest_battle_turns"] + turns) / 2
    if winner == quest:
        quest_results = (":skull: **" + player.name_clean + "** lost to the **" + quest.name_clean + "** and dropped ``"
                         + util.format_number(quest.money // 2, full_precision=True, money=True) + "``")
        player.money -= quest.money // 2
        player.quest_spawn_build_up += 0.1
    elif winner == player:
        if player.quest_day_start == 0:
            player.quest_day_start = time.time()
        player.quests_completed_today += 1
        player.quests_won += 1

        reward = (
            ":sparkles: **" + player.name_clean + "** defeated the **" + quest.name + "** and was rewarded with ``"
            + util.format_number(quest.money, full_precision=True, money=True) + "``\n")
        quest_scale = quest.get_quest_scale()
        avg_player_stat = player.get_avg_stat()

        def attr_gain(stat): return ((stat / avg_player_stat)
                                     * quest.level / (player.level * 2)
                                     * turns / average_quest_battle_turns / quest_scale)

        add_attack = min(attr_gain(quest.attack), 100)
        add_strg = min(attr_gain(quest.strg), 100)
        add_accy = min(attr_gain(quest.accy), 100)

        stats_reward = ":crossed_swords:+%.2f:muscle:+%.2f:dart:+%.2f" % (add_attack, add_strg, add_accy)
        quest_results = reward + stats_reward

        player.progress(add_attack, add_strg, add_accy, max_attr=100, max_exp=10000)
        player.money += quest.money
        stats.increment_stat(stats.Stat.MONEY_CREATED, quest.money)

        quest_info = quest.info
        if quest_info is not None:
            quest_info.times_beaten += 1
            quest_info.save()
        await game.check_for_level_up(ctx, player)
    else:
        quest_results = ":question: Against all you drew with the quest!"
    battle_embed.add_field(name="Quest results", value=quest_results, inline=False)
    await imagehelper.battle_screen(ctx.channel, player, quest)
    await util.say(ctx.channel, embed=battle_embed)
    # Put this here to avoid 'spoiling' results before battle log
    if winner == player:
        await awards.give_award(ctx.channel, player, "QuestDone", "*Saved* the server!")
    elif winner == quest:
        await awards.give_award(ctx.channel, player, "RedMist", "Red mist...")
    else:
        await awards.give_award(ctx.channel, player, "InconceivableQuest")
    player.save()


@commands.command(args_pattern='C')
async def declinequest(ctx, *args, **details):
    """
    [CMD_KEY]declinequest index

    Declines a quest because you're too wimpy to accept it.
    
    """

    player = details["author"]
    quest_index = args[0] - 1
    if quest_index < len(player.quests):
        quest = player.quests[quest_index]
        del player.quests[quest_index]
        player.save()
        quest_info = quest.info
        if quest_info is not None:
            quest_task = quest_info.task
        else:
            quest_task = "do a long forgotten quest:"
        await util.say(ctx.channel, ("**" + player.name_clean + "** declined to "
                                     + quest_task + " **" + quest.name_clean
                                     + " [Level " + str(math.trunc(quest.level)) + "]**!"))
    else:
        raise util.DueUtilException(ctx.channel, "Quest not found!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SRRRRS?S?S?R?')
async def createquest(ctx, *args, **details):
    """
    [CMD_KEY]createquest name (base attack) (base strg) (base accy) (base hp)
    
    You can also add (task string) (weapon) (image url) (spawn chance)
    after the first four args.
    
    Note a base value is how strong the quest would be at level 1
    
    __Example__:
    Basic Quest:
        ``[CMD_KEY]createquest "Mega Mouse" 1.3 2 1.1 32``
        This creates a quest named "Mega Mouse".
        With base values:
            Attack = 1.3
            Strg = 2
            Accy = 1.1
            HP = 32
    Advanced Quest:
        ``[CMD_KEY]createquest "Snek Man" 1.3 2 1.1 32 "Kill the" "Gun" http://i.imgur.com/sP8Rnhc.png 21``
        This creates a quest with the same base values as before but with the message "Kill the"
        when the quest pops up, a gun, a quest icon image and a spawn chance of 21%
        
    """

    extras = dict()
    if len(args) >= 6:
        extras['task'] = args[5]
    if len(args) >= 7:
        weapon_name_or_id = args[6]
        weapon = weapons.find_weapon(ctx.server, weapon_name_or_id)
        if weapon is None:
            raise util.DueUtilException(ctx.channel, "Weapon for the quest not found!")
        extras['weapon_id'] = weapon.w_id
    if len(args) >= 8:
        extras['image_url'] = args[7]
    if len(args) == 9:
        extras['spawn_chance'] = args[8]

    new_quest = quests.Quest(*args[:5], **extras, ctx=ctx)
    await util.say(ctx.channel, ":white_check_mark: " + util.ultra_escape_string(
        new_quest.task) + " **" + new_quest.name_clean + "** is now active!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SSSS*')
async def editquest(ctx, *args, **details):
    """
    [CMD_KEY]editquest name (property value)+
    
    Any number of properties can be set at once.
    Invalid values will just be ignored!
    
    This is also how you set quest channels!
    
    Properties:
        __attack__, __hp__, __accy__, __spawn__, __weap__,
        __image__, __task__ and __channel__
        
    Example usage:
    
        [CMD_KEY]editquest slime hp 43 attack 4.2 task "Kill the monster"
        
        [CMD_KEY]editquest slime channel ``#slime_fields``
    
    """

    editable_props = ("attack", "hp", "accy", "spawn", "weap", "image", "task", "channel")
    changes = OrderedDict()
    quest_name = args[0].lower()
    updates = args[1:]
    quest = quests.get_quest_on_server(ctx.server, quest_name)
    if quest is None:
        raise util.DueUtilException(ctx.channel, "Quest not found!")

    next_prop = 0
    while next_prop < len(updates):
        quest_property = updates[next_prop].lower()
        if quest_property in editable_props:
            if editable_props.index(quest_property) <= 3:
                try:
                    value = float(updates[next_prop + 1])
                except ValueError:
                    value = -1
            else:
                value = updates[next_prop + 1]
            changed = True
            if quest_property == "attack" and value >= 1:
                quest.base_attack = value
            elif quest_property == "hp" and value >= 30:
                quest.base_hp = value
            elif quest_property == "accy" and value >= 1:
                quest.base_accy = value
            elif quest_property == "spawn" and 25 >= value >= 1:
                quest.spawn_chance = value / 100
            elif quest_property == "weap" and weapons.find_weapon(ctx.server, value) is not None:
                weapon = weapons.find_weapon(ctx.server, value)
                quest.w_id = weapon.w_id
                value = str(weapon)
            elif quest_property == "image":
                quest.image_url = value
            elif quest_property == "task":
                quest.task = value
            elif quest_property == "channel":
                channel_id = value.replace("<#", "").replace(">", "")
                channel = util.get_client(ctx.server.id).get_channel(channel_id)
                if channel is not None:
                    quest.channel = channel.id
            else:
                changed = False
            if changed:
                if quest_property != "channel":
                    changes[quest_property] = util.ultra_escape_string(str(value))
                else:
                    changes[quest_property] = value
        next_prop += 2
    quest.save()
    changes_message = ""
    for quest_property, value in changes.items():
        changes_message += "``%s`` → %s\n" % (quest_property, value)
    if len(changes_message):
        await util.say(ctx.channel, (":white_check_mark: Quest **" + quest_name + "** edited:\n"
                                     + changes_message))
    else:
        await util.say(ctx.channel, (":x: **No changes made!**\n"
                                     + "__Note:__ Values that are out of range or incorrect will be ignored!"))


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='S')
async def removequest(ctx, *args, **details):
    """
    [CMD_KEY]removequest (quest name)
    
    Systematically exterminates all instances of the quest...
    ...Even those yet to be born
    
    """

    quest_name = args[0].lower()
    quest = quests.get_quest_on_server(ctx.server, quest_name)
    if quest is None:
        raise util.DueUtilException(ctx.channel, "Quest not found!")

    quests.remove_quest_from_server(ctx.server, quest_name)
    await util.say(ctx.channel, ":white_check_mark: **" + quest.name_clean + "** is no more!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='C?')
async def serverquests(ctx, *args, **details):
    page = 0
    if len(args) == 1:
        page = args[0] - 1
    embed = discord.Embed(title=(":crossed_swords: Quests on " + details["server_name_clean"]
                                 + (" : Page " + str(page + 1) if page > 0 else "")), type="rich",
                          color=gconf.EMBED_COLOUR)
    page_size = 12
    quests_list = list(quests.get_server_quest_list(ctx.server).values())
    if page * page_size >= len(quests_list):
        raise util.DueUtilException(None, "Page not found")
    if len(quests_list) > 0:
        quest_index = 0
        for quest_index in range(page_size * page, page_size * page + page_size):
            if quest_index >= len(quests_list):
                break
            quest = quests_list[quest_index]
            embed.add_field(name=quest.name_clean, value="Completed " + str(quest.times_beaten) + " time" + (
                "s" if quest.times_beaten != 1 else ""))
        if quest_index < len(quests_list) - 1:
            embed.set_footer(text="But wait there more! Do " + details["cmd_key"] + "serverquests " + str(page + 2))
        else:
            embed.set_footer(text="That's all!")
    else:
        embed.description = "There are no quests on this server!\nHow sad."

    await util.say(ctx.channel, embed=embed)
