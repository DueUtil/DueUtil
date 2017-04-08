import discord
import random
import math
import jsonpickle
import numpy
from fun import weapons
from fun.misc import DueUtilObject, Themes, Backgrounds
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
        self.level = 1
        self.exp = 0
        self.total_exp = 0
        self.attack = 1
        self.strg = 1
        self.accy = 1
        self.banner_id = "discord blue"
        self.theme_id = "test"
        self.hp = 10
        self.donor = False
        self.background = "default.png"
        self.weapon_sum = '"0"01'     # price/attack/sum
        self.w_id = weapons.NO_WEAPON_ID
        self.money = 1
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
        self.save()
        
    def progress(self,attack,strg,accy):
        self.attack += attack
        self.strg += strg
        self.accy += accy
        exp = util.clamp((attack + strg + accy) * 1000 , 1, 100)
        self.exp += exp
        self.total_exp += exp
        
    def owns_weapon(self,weapon_name):
        for weapon_slot in self.owned_weps:
            if(Weapon.get_weapon_from_id(weapon_slot[0]).name.lower() == weapon_name.lower()):
                return True
        return False
        
    def get_owned_themes(self):
        return profile_themes
        
    def get_name_possession(self):
        if self.name.endswith('s'):
            return self.name + "'"
        return self.name + "'s"
        
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
        theme = profile_themes[self.theme_id].copy()
        if theme["background"] != self.background:
            theme["background"] = self.background
        if theme["banner"] != self.banner:
            theme["banner"] = self.banner
        return theme
        
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
        rank_colours = profile_themes[self.theme_id]["rankColours"]
        return profile_themes[self.theme_id]["rankColours"][(self.rank - 1) % len(rank_colours)]
        
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

def get_theme(theme_name):
    theme_name = theme_name.lower()
    if theme_name in profile_themes:
        return profile_themes[theme_name]
        
def get_themes():
    return profile_themes
            
def load():
    global players, banners
    
    banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png")
    reference = Player(no_save = True)
    for player in dbconn.get_collection_for_object(Player).find():
        loaded_player = jsonpickle.decode(player['data'])
        players[loaded_player.id] = util.load_and_update(reference,loaded_player)
        
load()
