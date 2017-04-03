import collections
import discord
from fun.misc import DueUtilObject
from fun.players import Player

class QuestMap(collections.MutableMapping):
  
    """ A 2D Mapping of quests to servers
    Much wow
    
    ServerID/QuestName
    
    This class has
    """
    
    def __init__(self):
        self.quest_servers = dict()

    def __getitem__(self, key):
        quest_key = self.__parse_key__(key)
        return self.quest_servers[quest_key[0]][quest_key[1]]

    def __setitem__(self, key, value):
        quest_key = self.__parse_key__(key)
        if key[0] not in self.quest_servers:
            quests = dict()
            quests[key[1]] = value
            self.quest_servers[key[0]] = quests
        else:
            self.quest_servers[key[0]][key[1]] = value

    def __delitem__(self, key):
        del self.store[self.__parse_key__(key)[0]]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __parse_key__(self, key):
        return key.split('/',1)
        
quest_map = QuestMap()

class Quest(DueUtilObject):
  
    """A class to hold info about a server quest"""
  
    def __init__(self,name,base_attack,base_strg,base_accy,base_hp,**extras):
        message = extras.get('ctx',None)
      
        if message != None:
            if message.server.id in server_quests:
                if name.strip().lower() in server_quests[message.server.id]:
                    raise util.DueUtilException(message.channel,"A foe with that name already exists on this server!")
      
            if base_accy < 1 or base_attack < 1 or base_strg < 1:
                raise util.DueUtilException(message.channel,"No quest stats can be less than 1!")

            if base_hp < 30:
                raise util.DueUtilException(message.channel,"Base HP must be at least 30!")

            if len(name) > 30 or len(name) == 0 or name.strip == "":
                raise util.DueUtilException(message.channel,"Quest names must be between 1 and 30 characters!")
                
            self.server_id = message.server.id
            self.created_by = message.author.id
        else:
            self.server_id = "DEFAULT"
            self.created_by = ""
      
        self.name = name
        super().__init__(self.__quest_id())
        self.task = extras.get('task',"Battle a")
        self.w_id = extras.get('weapon_id',Weapons.NO_WEAPON_ID)
        self.spawn_chance = extras.get('spawn_chance',4) / 100
        self.image_url = extras.get('image_url',"")
        self.base_attack = base_attack
        self.base_strg = base_strg
        self.base_accy = base_accy
        self.base_hp = base_hp
        self.base_reward = 0 #self__reward()
        self.channel = extras.get('channel',"ALL")
            
        self.__add()
        
    def __quest_id(self):
        return self.server_id+'/'+self.name.lower()
      
    def __reward(self):
        if(Weapon.get_weapon_from_id(self.w_id).melee):
            base_reward = (self.base_attack + self.base_strg) / 10 / 0.0883
        else:
            base_reward = (self.base_accy + self.base_strg) / 10 / 0.0883
    
        base_reward += base_reward * math.log10(self.base_hp) / 20 / 0.75
        base_reward *= self.base_hp / abs(self.base_hp - 0.01)
        
        return base_reward
                        
    def __add(self):
        global servers_quests
        location = self.q_id.split('/',1)
        servers_quests[location[0]][location[1]]
    
    @property
    def made_on(self):
        return self.server_id
        
    @property    
    def creator(self):
        game.Player.find_player(quest_info.created_by)
        
    @property
    def q_id(self):
        return self.id
    
    @property
    def home(self):
        try:
            util.get_client(self.server_id).get_server(server_id)
        except:
            return None
        
class ActiveQuest(Player):
  
    def __init__(self,q_id, quester : Player):
        self.q_id = q_id
        super(ActiveQuest,self).__init__()
        self.__calculate_stats(player)
        
    def __calculate_stats(self, player):
        quest_info = self.info
        self.level = random.randrange(player.level, player.level * 2)
        hp_multiplier = random.randrange(self.level / 2, self.level)
        accy_multiplier = random.randrange(self.level / 2, self.level) / random.uniform(1.5, 1.9)
        strg_multiplier = random.randrange(self.level / 2, self.level) / random.uniform(1.5, 1.9)
        attack_multiplier = random.randrange(self.level / 2, self.level) / random.uniform(1.5, 1.9)
        self.name = quest_info.name
        self.hp = quest_info.base_hp * hp_multiplier
        self.attack = quest_info.base_attack * attack_multiplier
        self.strg = quest_info.base_strg * strg_multiplier
        self.accy = quest_info.base_accy * accy_multiplier
        self.money = abs(quest_info.base_reward) * (hp_multiplier
                                                    + accy_multiplier 
                                                    + strg_multiplier 
                                                    + attack_multiplier) // 4
        if self.money == 0:
            self.money = 1
        self.w_id = quest_info.w_id
        player.quests.append(self)
        
    def get_avatar_url(self,*args):
        return self.info.image_url
  
    @property
    def info(self):
        try:
            quest_id = self.q_id.split('/',1)
            return ServersQuests[quest_id[0]][quest_id[1]]
        except:
            return None

def get_server_quest_list(server):
    # TODO
    pass
    
def get_quest_from_id(quest_id):
    try:
        quest_map[quest_id]
    except:
        return None

def get_random_quest_in_channel(channel):
    if channel.server.id in quest_map:
        quests = quest_map[channel.server.id]
        for quest in quests:
            if quest.channel == "ALL" or quest.channel == channel.id:
                if random.random() <= quest.spawn_chance:
                    return quest
                    
def has_quests(place):
    if isinstance(place,discord.Server):
        return place.id in quest_map and len(quest_map[place.id]) > 0
    elif isinstance(place,discord.Channel):
        if place.server.id in quest_map:
            return next((quest for quest in quest[place.server.id] if quest.channel in ("ALL",place.id)), None) != None
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
              weapon_id = quest_data(quest_data["weapon"]),
              image_url = quest_data["image"],
              spawn_chance = quest_data["spawnChance"],
              no_save = True)
  
def load():
    global quest_map
    reference = Quest('Reference',0,0,0,0)
    load_default_quests()
    for quest in dbconn.get_collection_for_object(Quest).find():
        loaded_quest = jsonpickle.decode(quest['data'])
        quest_map[loaded_quest.q_id]
