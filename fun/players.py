import discord
import random
import math
import jsonpickle
import numpy
from fun import weapons
from fun.misc import DueUtilObject, Themes, Backgrounds, Ring
from botstuff import util, dbconn

players = dict()   
banners = dict()
backgrounds = Backgrounds()
profile_themes = Themes()

""" DueUtil battles & quests. The main meat of the bot. """

class Player(DueUtilObject):
  
    """The DueUtil player!"""
  
    def __init__(self,*args,**kwargs):
        global players,new_players_joined
        if len(args) > 0 and isinstance(args[0],discord.User):
            super().__init__(args[0].id,args[0].name,**kwargs)
        else:
            super().__init__("NO_ID","DueUtil Player",**kwargs)
        self.reset()
        players[self.id] = self

    def reset(self,discord_user = None):
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
        self.money = 1
        self.average_spelling_correctness = 1
        
        ##### CUSTOMIZATIONS #####
        self.banner_id = "discord blue"
        self.theme_id = "test"
        self.background = "default.png"
        self.weapon_sum = weapons.get_weapon_from_id("None").weapon_sum
        self.w_id = weapons.NO_WEAPON_ID
        
        ##### USAGE STATS #####
        self.last_progress = 0
        self.last_quest = 0
        self.wagers_won = 0
        self.quests_won = 0
        self.potatos_given = 0
        self.quest_day_start = 0
        self.potatos = 0
        self.quests_completed_today = 0
        self.last_image_request = 0
        self.last_message_hashes = Ring(10)
        self.spam_detections = 0
        
        ##### THINGS #####
        self.quests = []
        self.battlers = []
        self.awards = []
        self.weapon_inventory = []
        self.themes = ["default"]
        self.backgrounds = []
        
        self.donor = False
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
        
    def set_weapon(self,weapon):
        self.w_id = weapon.w_id
        self.weapon_sum = weapon.weapon_sum
        
    def get_owned_themes(self):
        return {theme_id:theme for theme_id,theme in profile_themes.items() if theme_id in self.themes}
                
    def get_owned_weapons(self):
        return [weapons.get_weapon_from_id(weapon_info[0]) for weapon_info in self.weapon_inventory if weapon_info[0] != weapons.NO_WEAPON_ID]
        
    def get_weapon(self,weapon_name):
        return next((weapon for weapon in self.get_owned_weapons() if weapon.name.lower() == weapon_name.lower()),None)
        
    def owns_weapon(self,weapon_name):
        return self.get_weapon(weapon_name) != None
        
    def get_name_possession(self):
        if self.name.endswith('s'):
            return self.name + "'"
        return self.name + "'s"
        
    def pop_from_invetory(self,weapon):
        for weapon_info in self.weapon_inventory:
          if weapon_info[0] == weapon.id:
              return self.weapon_inventory.pop(self.weapon_inventory.index(weapon_info))
              
    def store_weapon(self,weapon):
        self.weapon_inventory.append([weapon.id,weapon.weapon_sum])
      
    def get_name_possession_clean(self):
        return util.ultra_escape_string(self.get_name_possession())
        
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
    def theme(self):
        if self.theme_id in profile_themes: 
            theme = profile_themes[self.theme_id].copy()
        else:
            theme = profile_themes["default"].copy()
        if theme["background"] != self.background:
            theme["background"] = self.background
        if theme["banner"] != self.banner:
            theme["banner"] = self.banner
        return theme
        
    def weapon_hit(self):
        return random.random()<(self.weapon_accy/100)

    @property
    def item_value_limit(self):
        return 10000000000000000000000000000000000000000000
        return 10 * (math.pow(self.level,2)/3 + 0.5 * math.pow(self.level+1,2) * self.level)

    @property
    def weapon(self):
        return weapons.get_weapon_from_id(self.w_id)
        
    @property
    def rank(self):
        return int(self.level / 10) + 1
        
    @property
    def rank_colour(self):
        theme = self.theme
        rank_colours = theme["rankColours"]
        return theme["rankColours"][(self.rank - 1) % len(rank_colours)]
        
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
        
def find_player(user_id):
    if user_id in players:
        return players[user_id]
    elif load_player(user_id):
        return players[user_id]
      
def get_theme(theme_id):
    theme_id = theme_id.lower()
    if theme_id in profile_themes:
        return profile_themes[theme_id]
        
def get_themes():
    return profile_themes
            
def load_player(player_id):
    global players
    response = dbconn.get_collection_for_object(Player).find_one({"_id":player_id})
    if response != None and 'data' in response:
        player_data = response['data']
        loaded_player = jsonpickle.decode(player_data)
        players[loaded_player.id] = util.load_and_update(Player(no_save = True),loaded_player)
        return True
  
def load():
    global banners
    banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png")

load()
