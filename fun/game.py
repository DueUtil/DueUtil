import enchant
#import language_check
import ssdeep
import time
import json
import random
import re
import time
import emoji #The emoji list in this is outdated.
from botstuff import events
from botstuff import util
from fun import stats, weapons, players, quests, imagehelper

exp_per_level = dict()
QUEST_DAY = 86400
QUEST_COOLDOWN = 360
MAX_DAILY_QUESTS = 30
MAX_ACTIVE_QUESTS = 7
SPAM_TOLERANCE = 50
SPELLING_DICT = enchant.Dict("en_GB")
#LANG_TOOL = language_check.LanguageTool('en-GB')

def get_spam_level(player,message_content):
    message_hash = ssdeep.hash(message_content)
    spam_level = 0     
    spam_levels = [ssdeep.compare(message_hash, prior_hash) for prior_hash in player.last_message_hashes if prior_hash != None]
    if len(spam_levels) > 0:
        spam_level = max(spam_levels)
    player.last_message_hashes.append(message_hash)
    if spam_level > SPAM_TOLERANCE:
        player.spam_detections += 1
    return spam_level

async def player_message(player,message):
    
    """ 
    W.I.P. Function to allow a small amount of exp
    to be gained from messaging.
    
    """
    def get_words():
        return re.compile('\w+').findall(message.content)
    
    if player != None:
      
        if time.time() - player.last_progress >= 60 and get_spam_level(player,message.content) < SPAM_TOLERANCE:
          
            ### NEW TEST STUFF
            spelling_score = 0
            message_words = get_words()
            for word in message_words:
                if SPELLING_DICT.check(word):
                    spelling_score += 3
                else:
                    spelling_score -= 1
            spelling_score = (spelling_score/(len(message_words)*3))*100
            
            #await util.say(message.channel,"Spelling score: "+str(spelling_score))
            #grammer_score = 100 - ((len(LANG_TOOL.check(message.content))/len(message_words))*100)
            #await util.say(message.channel,"Grammer score: "+str(grammer_score))
            
            # await util.say(message.channel,"Spam level: "+str(get_spam_level(player,message.content)))

            # print (list(player.last_message_hashes))

            """
            if player.w_id != weapons.NO_WEAPON_ID:
                if player.weapon_sum != player.weapon.weapon_sum:
                    pass
            if time.time() - player.last_progress >= 60:
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
            """

    else:
        players.Player(message.author)
        stats.increment_stat(stats.Stat.NEW_PLAYERS_JOINED)
        
async def manage_quests(player,message):
  
    """ 
    Give out quests!
    
    """
    channel = message.channel
    if time.time() - player.quest_day_start > QUEST_DAY and player.quest_day_start != 0:
        player.quests_completed_today = 0
        player.quest_day_start = 0
        # print(filter_func(player.name)+" ("+player.userid+") daily completed quests reset")
    
    # Testing
    if not quests.has_quests(channel):
        quests.add_default_quest_to_server(message.server)
    # Testing    
    if time.time() - player.last_quest >= QUEST_COOLDOWN and get_spam_level(player,message.content) < SPAM_TOLERANCE:
        player.last_quest = time.time()
        if quests.has_quests(channel) and len(player.quests) < MAX_ACTIVE_QUESTS and player.quests_completed_today < MAX_DAILY_QUESTS:
            quest = quests.get_random_quest_in_channel(channel)
            if random.random() <= quest.spawn_chance:
                new_quest = quests.ActiveQuest(quest.q_id,player)
                stats.increment_stat(stats.Stat.QUESTS_GIVEN)
                await imagehelper.new_quest_screen(channel,new_quest,player)
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
    player = players.find_player(message.author.id)
    await player_message(player,message)
    await manage_quests(player,message)
    
load_game_rules()
events.register_message_listener(on_message)
