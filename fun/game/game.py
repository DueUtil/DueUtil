import enchant
from guess_language import guess_language
import ssdeep
import time
import json
import random
import re
import time
from botstuff import events
from botstuff import util
from . import stats, weapons, players, quests, awards
from ..configs import dueserverconfig
from ..helpers import imagehelper

exp_per_level = dict()
SPAM_TOLERANCE = 50
# For awards in the first week. Not permanent.
old_players = open('oldplayers.txt').read()  # For comeback award
testers = open('testers.txt').read()  # For testers award


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

    if player != None:

        if progress_time(player) and spam_level < SPAM_TOLERANCE:

            if len(message.content) > 0:
                player.last_progress = time.time()
            else:
                return

            ### Comeback award

            if player.id in old_players:
                await awards.give_award(message.channel, player, "CameBack", "Return to DueUtil")

            if player.id in testers:
                await awards.give_award(message.channel, player, "Tester", ":bangbang: **Something went wrong...**")

            ### Donor award

            if player.donor:
                await awards.give_award(message.channel, player, "Donor",
                                        "Donate to DueUtil!!! :money_with_wings: :money_with_wings: :money_with_wings:")

            ### DueUtil - the hidden spelling game!

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

    exp_for_next_level = get_exp_for_next_level(player.level)
    level_up_reward = 0
    while player.exp >= exp_for_next_level:
        player.exp -= exp_for_next_level
        player.level += 1
        level_up_reward += (player.level * 10)
        player.money += level_up_reward

        stats.increment_stat(stats.Stat.PLAYERS_LEVELED)

        exp_for_next_level = get_exp_for_next_level(player.level)
    stats.increment_stat(stats.Stat.MONEY_CREATED, level_up_reward)
    if level_up_reward > 0:
        if dueserverconfig.mute_level(ctx.channel) < 0:
            await imagehelper.level_up_screen(ctx.channel, player, level_up_reward)
        else:
            util.logger.info("Won't send level up image - channel blocked.")
        rank = player.rank
        if rank >= 1 and rank <= 10:
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
    if not quests.has_quests(channel):
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


def get_exp_for_next_level(level):
    for level_range, exp_details in exp_per_level.items():
        if level in level_range:
            return eval(exp_details.replace("oldLevel", str(level)))
    return -1


def _load_game_rules():
    with open('fun/configs/progression.json') as progression_file:
        progression = json.load(progression_file)
        exp = progression["dueutil-ranks"]
        for levels, exp_details in exp.items():
            if "," in levels:
                level_range = eval("range(" + levels + "+1)")
            else:
                level_range = eval("range(" + levels + "," + levels + "+1)")
            exp_expression = str(exp_details["expForNextLevel"])
            exp_per_level[level_range] = exp_expression


async def on_message(message):
    player = players.find_player(message.author.id)
    spam_level = 100
    if player is not None and (quest_time(player) or progress_time(player)):
        spam_level = get_spam_level(player, message.content)
    await player_message(message, player, spam_level)
    if player is not None:
        await manage_quests(message, player, spam_level)
        await check_for_recalls(message, player)


_load_game_rules()
events.register_message_listener(on_message)
