import random
import re
import time

import enchant
import ssdeep
from guess_language import guess_language

import generalconfig as gconf
from .. import events
from .. import util, dbconn
from ..game import players
from ..game import stats, weapons, quests, awards
from ..game.configs import dueserverconfig
from ..game.helpers import imagehelper
from . import gamerules

from threading import Lock

SPAM_TOLERANCE = 50
# For awards in the first week. Not permanent.
old_players = open('oldplayers.txt').read()  # For comeback award
testers = open('testers.txt').read()  # For testers award
spelling_lock = Lock()


def get_spam_level(player, message_content):
    """
    Get's a spam level for a message using a 
    fuzzy hash > 50% means it's probably spam
    """

    message_hash = ssdeep.hash(message_content)
    spam_level = 0
    spam_levels = [ssdeep.compare(message_hash, prior_hash) for prior_hash in player.last_message_hashes if
                   prior_hash is not None]
    if len(spam_levels) > 0:
        spam_level = max(spam_levels)
    player.last_message_hashes.append(message_hash)
    if spam_level > SPAM_TOLERANCE:
        player.spam_detections += 1
    return spam_level


def progress_time(player):
    return time.time() - player.last_progress >= 60


def quest_time(player):
    return time.time() - player.last_quest >= quests.QUEST_COOLDOWN


async def player_message(message, player, spam_level):
    """
    W.I.P. Function to allow a small amount of exp
    to be gained from messaging.
    
    """

    def get_words():
        return re.compile('\w+').findall(message.content)

    if player is not None:

        # Mention the old bot award
        if gconf.DEAD_BOT_ID in message.raw_mentions:
            await awards.give_award(message.channel, player, "SoCold", "They're not coming back.")
        # Art award
        if player.misc_stats["art_created"] >= 100:
            await awards.give_award(message.channel, player, "ItsART")

        if progress_time(player) and spam_level < SPAM_TOLERANCE:

            if len(message.content) > 0:
                player.last_progress = time.time()
            else:
                return

            # Special Awards
            # Comeback award
            if player.id in old_players:
                await awards.give_award(message.channel, player, "CameBack", "Return to DueUtil")
            # Tester award
            if player.id in testers:
                await awards.give_award(message.channel, player, "Tester", ":bangbang: **Something went wrong...**")
            # Donor award
            if player.donor:
                await awards.give_award(message.channel, player, "Donor",
                                        "Donate to DueUtil!!! :money_with_wings: :money_with_wings: :money_with_wings:")
            # DueUtil tech award
            if dbconn.conn()["dueutiltechusers"].find({"_id": player.id}).count() > 0:
                if "DueUtilTech" not in player.awards:
                    player.inventory["themes"].append("dueutil.tech")
                await awards.give_award(message.channel, player, "DueUtilTech", "<https://dueutil.tech/>")

            ### DueUtil - the hidden spelling game!
            # The non-thread safe Apsell calls
            spelling_lock.acquire()
            lang = guess_language(message.content)
            if lang in enchant.list_languages():
                spelling_dict = enchant.Dict(lang)
            else:
                spelling_dict = enchant.Dict("en_GB")

            spelling_score = 0
            big_word_count = 1
            big_word_spelling_score = 0
            message_words = get_words()
            for word in message_words:
                if len(word) > 4:
                    big_word_count += 1
                if spelling_dict.check(word):
                    spelling_score += 3
                    if len(word) > 4:
                        big_word_spelling_score += 1
                else:
                    spelling_score -= 1
            spelling_lock.release()
            # We survived?!
            
            spelling_score = max(1, spelling_score / ((len(message_words) * 3) + 1))
            spelling_avg = player.misc_stats["average_spelling_correctness"]
            1 - abs(spelling_score - spelling_avg)
            spelling_strg = big_word_spelling_score / big_word_count
            # Not really an average (like quest turn avg) (but w/e)
            player.misc_stats["average_spelling_correctness"] = (spelling_avg + spelling_score) / 2

            len_limit = max(1, 120 - len(message.content))
            player.progress(spelling_score / len_limit, spelling_strg / len_limit, spelling_avg / len_limit)

            player.hp = 10 * player.level
            await check_for_level_up(message, player)
            player.save()

    else:
        players.Player(message.author)
        stats.increment_stat(stats.Stat.NEW_PLAYERS_JOINED)


async def check_for_level_up(ctx, player):
    """
    Handles player level ups.
    """

    exp_for_next_level = gamerules.get_exp_for_next_level(player.level)
    level_up_reward = 0
    while player.exp >= exp_for_next_level:
        player.exp -= exp_for_next_level
        player.level += 1
        level_up_reward += (player.level * 10)
        player.money += level_up_reward

        stats.increment_stat(stats.Stat.PLAYERS_LEVELED)

        exp_for_next_level = gamerules.get_exp_for_next_level(player.level)
    stats.increment_stat(stats.Stat.MONEY_CREATED, level_up_reward)
    if level_up_reward > 0:
        if dueserverconfig.mute_level(ctx.channel) < 0:
            await imagehelper.level_up_screen(ctx.channel, player, level_up_reward)
        else:
            util.logger.info("Won't send level up image - channel blocked.")
        rank = player.rank
        if 1 <= rank <= 10:
            await awards.give_award(ctx.channel, player, "Rank%d" % rank, "Attain rank %d." % rank)


async def manage_quests(message, player, spam_level):
    """
    Gives out quests!
    """

    channel = message.channel
    if time.time() - player.quest_day_start > quests.QUEST_DAY and player.quest_day_start != 0:
        player.quests_completed_today = 0
        player.quest_day_start = 0
        util.logger.info("%s (%s) daily completed quests reset", player.name_assii, player.id)

    # Testing   
    if len(quests.get_server_quest_list(channel.server)) == 0:
        quests.add_default_quest_to_server(message.server)
    if quest_time(player) and spam_level < SPAM_TOLERANCE:
        if quests.has_quests(channel) and len(
                player.quests) < quests.MAX_ACTIVE_QUESTS and player.quests_completed_today < quests.MAX_DAILY_QUESTS:
            player.last_quest = time.time()
            quest = quests.get_random_quest_in_channel(channel)
            if random.random() <= quest.spawn_chance * player.quest_spawn_build_up:
                new_quest = quests.ActiveQuest(quest.q_id, player)
                stats.increment_stat(stats.Stat.QUESTS_GIVEN)
                player.quest_spawn_build_up = 1
                if dueserverconfig.mute_level(message.channel) < 0:
                    await imagehelper.new_quest_screen(channel, new_quest, player)
                else:
                    util.logger.info("Won't send new quest image - channel blocked.")
                util.logger.info("%s has received a quest [%s]", player.name_assii, new_quest.q_id)
            else:
                player.quest_spawn_build_up += 0.5


async def check_for_recalls(ctx, player):
    """
    Checks for weapons that have been recalled
    """

    current_weapon_id = player.equipped["weapon"]

    weapons_to_recall = [weapon_id for weapon_id in player.inventory["weapons"] + [current_weapon_id]
                         if (weapons.get_weapon_from_id(weapon_id).id == weapons.NO_WEAPON_ID
                             and weapon_id != weapons.NO_WEAPON_ID)]

    if len(weapons_to_recall) == 0:
        return
    if current_weapon_id in weapons_to_recall:
        player.weapon = weapons.NO_WEAPON_ID
    player.inventory["weapons"] = [weapon_id for weapon_id in player.inventory["weapons"] if
                                   weapon_id not in weapons_to_recall]
    recall_amount = sum([weapons.get_weapon_summary_from_id(weapon_id).price for weapon_id in weapons_to_recall])
    player.money += recall_amount
    player.save()
    await util.say(ctx.channel, (
        ":bangbang: " + ("One" if len(weapons_to_recall) == 1 else "Some") + " of your weapons has been recalled!\n"
        + "You get a refund of ``" + util.format_number(recall_amount, money=True, full_precision=True) + "``"))


async def on_message(message):
    player = players.find_player(message.author.id)
    spam_level = 100
    if player is not None and (quest_time(player) or progress_time(player)):
        spam_level = get_spam_level(player, message.content)
    await player_message(message, player, spam_level)
    if player is not None:
        await manage_quests(message, player, spam_level)
        await check_for_recalls(message, player)


events.register_message_listener(on_message)
