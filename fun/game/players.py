import discord
import random
import math
import jsonpickle
import numpy
from . import weapons
from ..helpers.misc import DueUtilObject, Ring
from collections import defaultdict
from .customization import Themes, Backgrounds, Banners, Theme
from botstuff import util, dbconn
from botstuff.util import SlotPickleMixin
from copy import copy

players = dict()   
banners = Banners()
backgrounds = Backgrounds()
profile_themes = Themes()

""" DueUtil battles & quests. The main meat of the bot. """

class Player(DueUtilObject,SlotPickleMixin):
  
    """
    The DueUtil player!
    This (and a few other classes) are very higgledy-piggledy due to
    being make very early on in development & have been changed so many
    times while trying not to break older versions & code.
    
    defaultdict is to hold sets of attributes that can be changed/Added to
    randomly.
    
    It allows attrs to be added automatically
    """
    
    # These are all the attrbs needed for a player
    # This is meant to optimize players. One caveat all new attributes
    # Must be a misc_stat, inventory item or equipped item
    __slots__ = ["level","attack","strg","hp",
                  "exp","money","total_exp","accy",
                  "last_progress","last_quest",
                  "wagers_won","quests_won",
                  "quest_day_start","benfont",
                  "quests_completed_today",
                  "spam_detections","quests",
                  "received_wagers","awards",
                  "quest_spawn_build_up","donor",
                  "misc_stats","equipped","inventory",
                  "last_message_hashes","command_rate_limts",
                  "additional_attributes"]
                  
    # additional_attributes is not defined but is there for possible future use.
    # I expect new types of quests/weapons to be subclasses.
  
    def __init__(self,*args,**kwargs):
        if len(args) > 0 and isinstance(args[0],discord.User):
            super().__init__(args[0].id,args[0].name,**kwargs)
            players[self.id] = self
        else:
            super().__init__("NO_ID","DueUtil Player",**kwargs)
        self.reset()
        self.money = 100

    def reset(self,discord_user = None):
      
        ### New rule: The default of all new items MUST have the id default now.
        
        if discord_user != None:
            self.name = discord_user.name
        self.benfont = False
        
        ##### STATS #####
        self.level = 1
        self.exp = 0
        self.total_exp = 0
        self.attack = 1
        self.strg = 1
        self.accy = 1
        self.hp = 10
        self.money = 0
        
        ##### USAGE STATS #####
        self.last_progress = 0
        self.last_quest = 0
        self.wagers_won = 0
        self.quests_won = 0
        self.quest_day_start = 0
        self.quests_completed_today = 0
        self.last_message_hashes = Ring(10)
        self.spam_detections = 0
        self.command_rate_limts = {}
        
        ##### THINGS #####
        self.quests = []
        self.received_wagers = []
        self.awards = []
        
        # To help the noobz
        self.quest_spawn_build_up = 1
        
        # lol no
        self.donor = False
        
        ##### Dumb misc stats (easy to add & remove)
        self.misc_stats = defaultdict(int,
                                      emojis_given = 0,
                                      emojis = 0,
                                      potatoes = 0,
                                      potatoes_given = 0,
                                      average_spelling_correctness = 1,
                                      average_quest_battle_turns = 1)

        ##### Equiped items
        self.equipped = defaultdict(lambda: "default",
                                    weapon = weapons.NO_WEAPON_ID,
                                    banner = "discord blue",
                                    theme = "default",
                                    background = "default")               
        
        ##### Inventory. defaultdict so I can add more stuff - without fuss
        ##### Also makes shop simpler
        self.inventory = defaultdict(lambda: ["default"],
                                     weapons = [],
                                     themes = ["default"],
                                     backgrounds = ["default"],
                                     banners = ["discord blue"])

        self.save()
        
    def progress(self,attack,strg,accy,**options):
        max_attr = options.get('max_attr',0.1)
        max_exp = options.get('max_exp',15)
        self.attack += min(attack,max_attr)
        self.strg += min(strg,max_attr)
        self.accy += min(accy,max_attr)
        exp = min((attack + strg + accy) * 100,max_exp)
        self.exp += exp
        self.total_exp += exp
        
    def get_owned(self,item_type,all_items):
        return {item_id:item for item_id,item in all_items.items() if item_id in self.inventory[item_type]}
        
    def get_owned_themes(self):
        return self.get_owned("themes",profile_themes)
        
    def get_owned_backgrounds(self):
        return self.get_owned("backgrounds",backgrounds)

    def get_owned_banners(self):
        return self.get_owned("banners",banners)
                
    def get_owned_weapons(self):
        return [weapons.get_weapon_from_id(weapon_id) for weapon_id in self.inventory["weapons"] if weapon_id != weapons.NO_WEAPON_ID]
        
    def get_weapon(self,weapon_name):
        return next((weapon for weapon in self.get_owned_weapons() if weapon.name.lower() == weapon_name.lower()),None)
        
    def owns_weapon(self,weapon_name):
        return self.get_weapon(weapon_name) != None
        
    def get_name_possession(self):
        if self.name.endswith('s'):
            return self.name + "'"
        return self.name + "'s"
        
    def get_name_possession_clean(self):
        return util.ultra_escape_string(self.get_name_possession())
        
    def discard_stored_weapon(self,weapon):
        if weapon.id in self.inventory["weapons"]:
            self.inventory["weapons"].remove(weapon.id)
            return True
        return False
          
    def store_weapon(self,weapon):
        self.inventory["weapons"].append(weapon.id)
        
    def weapon_hit(self):
        return random.random()<(self.weapon_accy)
            
    def get_avatar_url(self,*args):
        server = args[0]
        member = server.get_member(self.id)
        if member.avatar_url != "":
           return member.avatar_url
        return member.default_avatar_url
           
    def get_avg_stat(self):
        return sum((self.attack,self.strg,self.accy))/4
        
    @property
    def item_value_limit(self):
        return int(100 * (math.pow(self.level,2)/3 + 0.5 * math.pow(self.level+1,2) * self.level))

    @property
    def rank(self):
        return self.level // 10
        
    @property
    def rank_colour(self):
        rank_colours = self.theme["rankColours"]
        return rank_colours[self.rank % len(rank_colours)]
        
    @property    
    def weapon_accy(self):
        max_value = self.item_value_limit
        price = self.weapon.price if self.weapon.price > 0 else 1
        new_accy = numpy.clip(max_value/price * 100,1,86)
        new_accy = self.weapon.accy if new_accy > self.weapon.accy else new_accy
        return new_accy if price > max_value else self.weapon.accy
    
    @property
    def user_id(self):
        return self.id
        
    @property
    def weapon(self):
        return weapons.get_weapon_from_id(self.equipped["weapon"])
        
    @weapon.setter
    def weapon(self,weapon):
        self._setter("weapon",weapon)
        
    @property
    def background(self):
        current_background = self.equipped["background"]
        if not current_background in backgrounds:
            # Check (just to quick fix)
            # TODO: Remove later
            if current_background in self.inventory["backgrounds"]: self.inventory["backgrounds"].remove(current_background)
            self.equipped.background = "default"
        return backgrounds[self.equipped["background"]]
    
    @background.setter
    def background(self,background):
        self._setter("background",background)
        
    @property
    def banner(self):
        banner = banners.get(self.equipped["banner"],banners["discord blue"])
        if not (self.equipped["banner"] in banners or banner.can_use_banner(self)):
            self.inventory["banners"].remove(self.banner_id)
            self.equipped["banner"] = "discord blue"
        return banner
        
    @banner.setter
    def banner(self,banner):
        self._setter("banner",banner)
        
    @property
    def theme(self):
        current_theme = self.equipped["theme"]
        if current_theme in profile_themes: 
            theme = copy(profile_themes[current_theme])
        else:
            theme = profile_themes["default"].copy()
        if theme["background"] != self.equipped["background"]:
            theme["background"] = self.equipped["background"]
        if theme["banner"] != self.equipped["banner"]:
            theme["banner"] = self.equipped["banner"]
        return theme

    @theme.setter
    def theme(self,theme):
        self._setter("theme",theme)
        if not isinstance(theme,Theme):
            theme = profile_themes[theme]
        self.equipped["banner"] = theme["banner"]
        self.equipped["background"] = theme["background"]
        
    def _setter(self,thing,value):
        if isinstance(value,DueUtilObject):
            self.equipped[thing] = value.id
        elif isinstance(value,str):
            self.equipped[thing] = value
        else:
            raise util.BotException("%s cannot be set to %s" % (thing,value))
            
    def __setstate__(self, object_state):
        SlotPickleMixin.__setstate__(self,object_state)
        self.command_rate_limts = {}
        self.last_message_hashes = Ring(10)
        for quest in self.quests:
            quest.quester = self
        
    def __getstate__(self):
        object_state = SlotPickleMixin.__getstate__(self)
        del object_state["last_message_hashes"]
        del object_state["command_rate_limts"]
        return object_state
           
def find_player(user_id):
    if user_id in players:
        return players[user_id]
    elif load_player(user_id):
        return players[user_id]
      
def get_theme(theme_id):
    theme_id = theme_id.lower()
    if theme_id in profile_themes:
        return profile_themes[theme_id]
        
def get_background(background_id):
    background_id = background_id.lower()
    if background_id in backgrounds:
        return backgrounds[background_id]
        
def get_banner(banner_id):
    banner_id = banner_id.lower()
    if banner_id in banners:
        return banners[banner_id]

def get_themes():
    return profile_themes
            
REFERENCE_PLAYER = Player(no_save = True)

def load_player(player_id):
    response = dbconn.get_collection_for_object(Player).find_one({"_id":player_id})
    if response != None and 'data' in response:
        player_data = response['data']
        loaded_player = jsonpickle.decode(player_data)
        players[loaded_player.id] = util.load_and_update(REFERENCE_PLAYER,loaded_player)
        return True
