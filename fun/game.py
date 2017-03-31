import discord
import jsonpickle
import json
import math
import time
import random 
import numpy
import emoji #The emoji list in this is outdated.
from botstuff import dbconn, util, events
from PIL import Image, ImageDraw, ImageFont
from fun.misc import DueUtilObject
from fun import stats, weapons, players
import awards

async def player_progress(message):

    player = players.find_player(message.author.id)
    if(player != None):
        if(player.w_id != weapons.NO_WEAPON_ID):
            if(player.weapon_sum != player.weapon.weapon_sum):
                pass
                #await sell(message,player.user_id,True)
        #await validate_weapon_store(message,player)
        
        if  time.time() - player.last_progress >= 60:
            player.last_progress = time.time()
            start_level = player.level
            add_attack = len(message.content) / 600
            if add_attack < 0.02:
                add_attack += 0.02
                
            add_strg = sum(1 for char in message.content if char.isupper()) / 400
            if add_strg < 0.03:
                add_strg += 0.03
                
            add_accy = (message.content.count(' ') + message.content.count('.') + message.content.count("'")) / 3 / 200
            if add_accy < 0.01:
                add_accy += 0.01
                
            player.attack += add_attack
            player.strg += add_strg
            player.accy += add_accy
            player.level += (player.attack + player.strg + player.accy -3) / 3 / math.pow(player.level, 3)                                      
            player.hp = 10 * player.level
            
            if math.trunc(player.level) > math.trunc(start_level):
                level_up_reward = math.trunc(player.level) * 10
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
                elif (rank > 2 and rank <=9):
                    await give_award(message, player, rank+2, "Attain rank "+str(rank)+".")                
            player.save()
    if player == None:
        new_player = players.Player(message.author)
        
async def on_message(message): 
    print("Test")
    await player_progress(message)
    
events.register_message_listener(on_message)
