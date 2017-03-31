import discord
import random
import math
import sys
import pickle
import requests
import string
import os
import jsonpickle
import hashlib
from urllib.request import urlopen
import time
import re
import os
import shutil
import json
from io import StringIO
import numpy
from fun import weapons, stats
from fun.misc import DueUtilObject
from botstuff import util, dbconn

players = dict()   
banners = dict()
""" DueUtil battles & quests. The main meat of the bot. """

class Player(DueUtilObject):
  
    """The DueUtil player!"""
  
    def __init__(self,*args):
        global players,new_players_joined
        super().__init__(args[0].id if len(args) > 0 and isinstance(args[0],discord.Member) else "","Player")
        self.reset()
        players[self.id] = self
        stats.increment_stat(stats.Stat.NEW_PLAYERS_JOINED)

    def reset(self):
        self.benfont = False
        self.level = 1
        self.attack = 1
        self.strg = 1
        self.accy = 1
        self.banner_id = "discord blue"
        self.hp = 10
        self.donor = False
        self.background = "default.png"
        self.weapon_sum = '"0"01'     # price/attack/sum
        self.w_id = weapons.NO_WEAPON_ID
        self.money = 100000
        self.last_progress = 0
        self.last_quest = 0
        self.wagers_won = 0
        self.quests_won = 0
        self.potatos_given = 0
        self.quest_day_start = 0
        self.potatos = 0
        self.quests_completed_today = 0
        self.last_image_request = 0
        self.quests = []
        self.battlers = []
        self.awards = []
        self.weapon_inventory = []
        self.name = "Player"
        self.save()
        
    def owns_weapon(self,weapon_name):
        for weapon_slot in self.owned_weps:
            if(Weapon.get_weapon_from_id(weapon_slot[0]).name.lower() == weapon_name.lower()):
                return True
        return False
        
    @property    
    def weapon_accy(self):
        max_value = self.item_value_limit
        price = self.weapon.price if self.weapon.price > 0 else 1
        new_accy = numpy.clip(max_value/price * 100,1,86)
        new_accy = self.weapon.accy if new_accy > self.weapon.accy else new_accy
        return new_accy if price > max_value else self.weapon.accy
    
    @property
    def user_id(self):
        self.name
        
    def weapon_hit(self):
        return random.random()<(self.weapon_accy/100)

    async def unequip_weapon(self,channel):
        if weapon.w_id != no_weapon_id:
            if len(self.owned_weps) < 6:
                if not self.owns_weapon(self.weapon.name):
                    self.owned_weps.append([active_wep.wID,self.weapon_sum])
                    self.wID = no_weapon_id
                    self.weapon_sum = weapons(no_weapon_id).weapon_sum
                    await util.say(channel, ":white_check_mark: **"+active_wep.name+"** unequiped!")
                else:
                    raise util.DueUtilException(channel,"You already have a weapon with that name stored!")
            else:
                raise util.DueUtilException(channel, "No room in your weapon storage!")
        else:
            raise util.DueUtilException(channel,"You don't have anything equiped anyway!")
            
    @property
    def item_value_limit(self):
        return math.inf
        return 10 * (math.pow(self.level,2)/3 + 0.5 * math.pow(self.level+1,2) * self.level)

    @property
    def weapon(self):
        return weapons.get_weapon_from_id(self.w_id)
        
    @property
    def rank(self):
        return int(self.level / 10) + 1
        
    @property
    def rank_colour(self):
        if(self.rank == 1):
            return (255, 255, 255)
        elif (self.rank == 2):
            return (235, 196, 42)
        elif (self.rank == 3):
            return (235, 145, 42)
        elif (self.rank == 4):
            return (42, 235, 68)
        elif (self.rank == 5):
            return (174, 42, 235)
        elif (self.rank == 6):
            return (42, 103, 235)
        elif (self.rank == 7):
            return (163, 102, 90)
        elif (self.rank == 8):
            return (224, 33, 11)
        elif (self.rank > 8):
            return (15, 15, 15)
        return (255, 255, 255)
        
    @property
    def banner(self):
        banner = banners.get(self.banner_id,banners["discord blue"])
        if not banner.can_use_banner(self):
            player.banner_id = "discord blue"
            return banners["discord blue"]
        return banner
        
    def get_avatar_url(self,*args):
        server = args[0]
        member = server.get_member(self.id)
        if member.avatar_url != "":
           return member.avatar_url
        else:
           return member.default_avatar_url
        
class PlayerInfoBanner:
    
    """Class to hold details & methods for a profile banner"""
    
    def __init__(self,name,image_name,**kwargs):
      
        self.price = kwargs.get('price',0)
        self.donor = kwargs.get('donor',False)
        self.admin_only = kwargs.get('admin_only',False)
        self.mod_only = kwargs.get('mod_only',False)
        self.unlock_level = kwargs.get('unlock_level',0)
        self.image = None
        self.image_name = image_name
        self.name = name
                
    def banner_restricted(self,player):
        return ((not self.admin_only or self.admin_only == util.is_admin(player.userid)) 
                and (not self.mod_only or self.mod_only == util.is_mod_or_admin(player.userid)))
        
    def can_use_banner(self,player):
        return (not self.donor or self.donor == self.donor) and self.banner_restricted(player)
        
    def save(self):
        dbconn.insert_object(self.name.lower().replace(" ","_"),self)
        
def add_default_banner():
    global banners
    discord_blue_banner = player_info_banner("Discord Blue","info_banner.png")
    banners["discord blue"] = discord_blue_banner
        
def load_backgrounds():
     Backgrounds.clear()
     for file in os.listdir("backgrounds"):
         if file.endswith(".png"):
             filename = str(file)
             background_name = filename.lower().replace("stats_", "").replace(".png", "").replace("_", " ").title()
             Backgrounds[background_name] = filename
             
async def give_award(channel, player, award_id, text):
    if award_id not in player.awards:
        player.awards.append(award_id)
        player.save()
        if not channel.is_private: #or not (message.server.id+"/"+message.channel.id in util.mutedchan):
            await util.get_client(channel.server.id).send_message(channel, "**"+player.name+"** :trophy: **Award!** " + text)
    
def valid_image(bg_to_test,dimensions):
    if(bg_to_test != None):
        width, height = bg_to_test.size
        if(width == dimensions[0] and height == dimensions[1]):
            return True
    return False
    
def find_player(user_id):
    if(user_id in players):
        return players[user_id]
    else:
        return None

def load():
    global players, banners
    
    banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png")
    
    reference = Player()
    for player in dbconn.get_collection_for_object(Player).find():
        loaded_player = jsonpickle.decode(player['data'])
        players[loaded_player.user_id] = util.load_and_update(reference,loaded_player)
        
load()
