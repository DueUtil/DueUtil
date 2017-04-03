import math
import time
import json
import time
import emoji #The emoji list in this is outdated.
from botstuff import events
from botstuff import util
from fun import stats, weapons, players, quests

exp_per_level = dict()
QUEST_DAY = 86400
QUEST_COOLDOWN = 360
MAX_DAILY_QUESTS = 30
MAX_ACTIVE_QUESTS = 7

async def player_progress(message):
    
    """ 
    W.I.P. Function to allow a small amount of exp
    to be gained from messaging.
    
    """
  
    player = players.find_player(message.author.id)
    if(player != None):
        if(player.w_id != weapons.NO_WEAPON_ID):
            if(player.weapon_sum != player.weapon.weapon_sum):
                pass
        
        if  time.time() - player.last_progress >= 60:
            player.last_progress = time.time()
            exp_for_next_level = get_exp_for_next_level(player.level)
            add_attack = len(message.content) / 2000
            add_strg = sum(1 for char in message.content if char.isupper()) / 1400
            add_accy = ((message.content.count(' ') 
                        + message.content.count('.') 
                        + message.content.count("'")) / 3 / 2000)

            player.progress(add_attack, add_strg, add_accy)
            #player.hp = 10 * player.level
            
            if player.exp >= exp_for_next_level:
                player.exp -= exp_for_next_level
                player.level += 1
                level_up_reward = player.level * 10
                player.money += level_up_reward
                
                stats.increment_stat(stats.Stat.MONEY_CREATED,level_up_reward)
                stats.increment_stat(stats.Stat.PLAYERS_LEVELED)
                
                if not (message.server.id+"/"+message.channel.id in util.muted_channels):
                    await imagehelper.level_up_screen(message.channel,player,level_up_reward)
                else:
                    print("Won't send level up image - channel blocked.")
                    
                rank = int(player.level / 10) + 1
                if(rank == 2):
                    await give_award(message, player, 2, "Attain rank 2.")
                elif (rank > 2 and rank <= 9):
                    await give_award(message, player, rank+2, "Attain rank "+str(rank)+".")                
            player.save()
    if player == None:
        players.Player(message.author)
        stats.increment_stat(stats.Stat.NEW_PLAYERS_JOINED)
        
async def manage_quests(message):
    player = players.find_player(message.author.id)
    if time.time() - player.quest_day_start > QUEST_DAY and player.quest_day_start != 0:
        player.quests_completed_today = 0
        player.quest_day_start = 0
        # print(filter_func(player.name)+" ("+player.userid+") daily completed quests reset")
    if time.time() - player.last_quest >= QUEST_COOLDOWN:
        player.last_quest = time.time()
        if quests.has_quests(message.channel) and len(player.quests) < MAX_ACTIVE_QUESTS and player.quests_completed_today < MAX_DAILY_QUESTS:
            quest = quests.get_random_quest_in_channel(message.channel)
            quests.ActiveQuest(quest.q_id,player)
            await util.say("DEBUG: NEW QUEST")
            stats.increment_stat(stats.Stat.QUESTS_GIVEN)
            # print(filter_func(player.name)+" ("+player.userid+") has received a quest ["+filter_func(n_q.qID)+"]")
        
def get_exp_for_next_level(level):
    for level_range, exp_details in exp_per_level.items():
        if level in level_range:
            return eval(exp_details.replace("oldLevel",str(level)))
    return -1

def load_game_rules():
    global exp_per_level
    with open('fun/configs/progression.json') as progression_file:  
        progression = json.load(progression_file)
    exp = progression["dueutil-ranks"]
    for levels, exp_details in exp.items():
        if "," in levels:
            level_range = eval("range("+levels+"+1)")
        else:
            level_range = eval("range("+levels+","+levels+"+1)")
        exp_expression = str(exp_details["expForNextLevel"])
        exp_per_level[level_range] = exp_expression

async def on_message(message): 
    await player_progress(message)
    
load_game_rules()

events.register_message_listener(on_message)
events.register_message_listener(manage_quests)
