from fun.misc import DueUtilObject
from botstuff import permissions
from botstuff.permissions import Permission
import discord
from PIL import Image
import json

"""

Basic classes to store themes, backgrounds and banners.

"""

class Theme(DueUtilObject,dict):
    
    def __init__(self,id,**theme_data):
        self.update(theme_data)
        self["background"] += ".png"
        super().__init__(id,self["name"])
      
class Themes(dict):
    
    def __init__(self):
        self.load_themes()
    
    def load_themes(self):
        with open('fun/configs/themes.json') as themes_file:  
            themes = json.load(themes_file)
        default_rank_colours = themes["rankColours"]
        for theme_id,theme in themes["themes"].items():
            if "rankColours" not in theme:
                theme["rankColours"] = default_rank_colours
            self[theme_id] = Theme(theme_id,**theme)
 
class Background(DueUtilObject,dict):
    
    def __init__(self,id,**background_data):
        self.update(background_data)
        self.image = Image.open("backgrounds/"+self["image"])
        super().__init__(id,self["name"])
      
class Backgrounds(dict):
    
    def __init__(self):
        self.load_backgrounds()
      
    def load_backgrounds(self):
        self.clear()
        with open('backgrounds/backgrounds.json') as backgrounds_file:
            backgrounds = json.load(backgrounds_file)
        for background_id,background in backgrounds.items():
            self[background_id] = Background(background_id,**background)

class Banners(dict):
    
    def __init__(self):
        self.load_banners()
      
    def load_banners(self):
        self.clear()
        with open('screens/banners/banners.json') as banners_file:
            banners = json.load(banners_file)
        for banner_id,banner in banners.items():
            self[banner_id] = Banner(banner_id,**banner)

class Banner(DueUtilObject):
    
    """Class to hold details & methods for a profile banner"""
    
    def __init__(self,id,**banner_data):
      
        self.price = banner_data["price"]
        self.donor = banner_data.get('donor',False)
        self.admin_only = banner_data.get('admin_only',False)
        self.mod_only = banner_data.get('mod_only',False)
        self.unlock_level = banner_data.get('unlock_level',0)
        self.image = Image.open("screens/banners/"+banner_data["image"])
        self.image_name = banner_data["image"]
        self.icon = banner_data["icon"]
        self.description = banner_data["description"]
        super().__init__(id,banner_data["name"])
                                
    def banner_restricted(self,player):
        member = discord.Member(user={"id":player.id})
        return ((not self.admin_only or self.admin_only and permissions.has_permission(member,Permission.DUEUTIL_ADMIN)) 
                and (not self.mod_only or self.mod_only and permissions.has_permission(member,Permission.DUEUTIL_MOD)))
        
    def can_use_banner(self,player):
        return (not self.donor or self.donor and player.donor) and self.banner_restricted(player)
