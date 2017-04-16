import discord
import json
import random
import math
import jsonpickle
from botstuff import util, dbconn
from fun import weapons, players
from fun.misc import DueUtilObject, DueMap
from fun.players import Player
        
quest_map = DueMap()
MAX_QUEST_IV = 60
MIN_QUEST_IV = 0

class Quest(DueUtilObject):
  
    """A class to hold info about a server quest"""
  
    def __init__(self,name,base_attack,base_strg,base_accy,base_hp,**extras):
        message = extras.get('ctx',None)
        given_spawn_chance = extras.get('spawn_chance',4)
      
        if message != None:
            if message.server in quest_map:
                if name.lower() in quest_map[message.server]:
                    raise util.DueUtilException(message.channel,"A foe with that name already exists on this server!")
      
            if base_accy < 1 or base_attack < 1 or base_strg < 1:
                raise util.DueUtilException(message.channel,"No quest stats can be less than 1!")

            if base_hp < 30:
                raise util.DueUtilException(message.channel,"Base HP must be at least 30!")

            if len(name) > 30 or len(name) == 0 or name.strip == "":
                raise util.DueUtilException(message.channel,"Quest names must be between 1 and 30 characters!")
                
            if given_spawn_chance > 25:
                raise util.DueUtilException(message.channel,"Spawn chance cannot be greater than 25%")
                
            self.server_id = message.server.id
            self.created_by = message.author.id
        else:
            self.server_id = extras.get('server_id',"DEFAULT")
            self.created_by = ""
      
        self.name = name
        super().__init__(self.__quest_id())
        self.task = extras.get('task',"Battle a")
        self.w_id = extras.get('weapon_id',weapons.NO_WEAPON_ID)
        self.spawn_chance = given_spawn_chance/100
        self.image_url = extras.get('image_url',"")
        self.base_attack = base_attack
        self.base_strg = base_strg
        self.base_accy = base_accy
        self.base_hp = base_hp
        self.channel = extras.get('channel',"ALL")
        self.times_beaten = 0
        self.__add()
        self.save()
        
    def __quest_id(self):
        return self.server_id+'/'+self.name.lower()
    
    def __add(self):
        global quest_map
        if self.server_id != "":
            quest_map[self.id] = self
            
    def base_values(self):
        return (self.base_hp,self.base_attack,
                self.base_strg,self.base_accy,
                self.base_reward,)
        
    @property
    def made_on(self):
        return self.server_id
        
    @property    
    def creator(self):
        creator = players.find_player(self.created_by)
        if creator != None:
            return creator.name
        else:
            return "Unknown"
        
    @property
    def q_id(self):
        return self.id
    
    @property
    def home(self):
        try:
            return util.get_client(self.server_id).get_server(self.server_id).name
        except:
            return "Unknown"
        
class ActiveQuest(Player):
  
    def __init__(self,q_id, quester : Player):
        self.q_id = q_id
        super(ActiveQuest,self).__init__()
        self.name = self.info.name
        self.quester_id = quester.id
        self.w_id = self.info.w_id
        self.level = random.randint(quester.level, quester.level * 2)
        self.__calculate_stats__()
        quester.quests.append(self)
        quester.save()
        
    def __calculate_stats__(self,**spoof_values):
        base_quest = self.info
        quester = players.find_player(self.quester_id)
        base_values = base_quest.base_values()
        stats = []
        # For testing purposes only
        quester_money = spoof_values.get('q_money',quester.money)
        weapon_damage = spoof_values.get('w_damage',self.weapon.damage)
        weapon_accy = spoof_values.get('w_accy',self.weapon.accy)
        for stat_calculation in range(0,4):
            iv = random.randint(MIN_QUEST_IV,MAX_QUEST_IV)
            stat = ((((base_values[stat_calculation]+iv)*2 
                    + quester_money**0.8/2) * self.level**1.5/100) + self.level)
            stats.append(stat)
        self.hp =  stats[0] 
        self.attack = stats[1]
        self.strg = stats[2]
        self.accy = stats[3] 
        self.cash_iv = random.randint(MIN_QUEST_IV,MAX_QUEST_IV/5)*weapon_damage*(weapon_accy/100)
        # self.money = reward
        
    def get_avatar_url(self,*args):
        quest_info = self.info
        if quest_info != None:
            return quest_info.image_url
  
    def get_reward(self):
        if not hasattr(self,"cash_iv"):
            self.cash_iv = 0
        quester = players.find_player(self.quester_id)
        avg_stat = self.get_avg_stat()
        reward_multiplier = avg_stat/quester.get_avg_stat()
        quester_weapon = quester.weapon
        weapon_scale = quester_weapon.damage*(quester_weapon.accy/100)
        return int(avg_stat/quester.level*self.cash_iv/weapon_scale*reward_multiplier) + 1

    @property
    def money(self):
        return self.get_reward()
    
    @money.setter
    def money(self,value):
        # To maintain backwards compatibility
        pass
        
    @property
    def info(self):
        return quest_map[self.q_id]

    def get_threat_level(self,player):
        return [
            player.attack/max(player.attack,self.attack),
            player.strg/max(player.strg,self.strg),
            player.accy/max(player.accy,self.accy),
            self.money/max(player.money,self.money),
            player.weapon.damage/max(player.weapon.damage,self.weapon.damage)
        ]
    
def get_server_quest_list(server):
    return quest_map[server]
    
def get_quest_on_server(server,quest_name):
    return quest_map[server.id+"/"+quest_name.lower()]

def remove_quest_from_server(server,quest_name):
    quest_id = server.id+"/"+quest_name.lower()
    del quest_map[quest_id]
    dbconn.get_collection_for_object(Quest).remove({'_id': quest_id})

def get_quest_from_id(quest_id):
    return quest_map[quest_id]
    
def get_channel_quests(channel):
    return [quest for quest in quest_map[channel.server].values() if quest.channel in ("ALL",channel.id)]

def get_random_quest_in_channel(channel):
    if channel.server in quest_map:
        return random.choice(get_channel_quests(channel))
        
def add_default_quest_to_server(server):
    default = random.choice(list(quest_map["DEFAULT"].values()))
    Quest(default.name,
          default.base_attack, 
          default.base_strg,
          default.base_accy,
          default.base_hp,
          task = default.task,
          weapon_id = default.w_id,
          image_url = default.image_url,
          spawn_chance = default.spawn_chance * 100,
          server_id = server.id)
                    
def has_quests(place):
    if isinstance(place,discord.Server):
        return place in quest_map and len(quest_map[place]) > 0
    elif isinstance(place,discord.Channel):
        if place.server in quest_map:
            return len(get_channel_quests(place)) > 0
    return False
        
def load_default_quests():
    with open('fun/configs/defaultquests.json') as defaults_file:  
        defaults = json.load(defaults_file)
    for quest_data in defaults.values():
        Quest(quest_data["name"],
              quest_data["baseAttack"],
              quest_data["baseStrg"],
              quest_data["baseAccy"],
              quest_data["baseHP"],
              task = quest_data["task"],
              weapon_id = weapons.stock_weapon(quest_data["weapon"]),
              image_url = quest_data["image"],
              spawn_chance = quest_data["spawnChance"],
              no_save = True)
  
def load():
    global quest_map
    reference = Quest('Reference',1,1,1,1,server_id="")
    load_default_quests()
    for quest in dbconn.get_collection_for_object(Quest).find():
        loaded_quest = jsonpickle.decode(quest['data'])
        quest_map[loaded_quest.q_id] = loaded_quest

load()
