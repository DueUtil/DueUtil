from ..helpers.misc import DueUtilObject
from botstuff import permissions
from botstuff.permissions import Permission
import discord
from PIL import Image
import json

"""

Basic classes to store themes, backgrounds and banners.

"""

# Both Theme & Background used to be an extension of dict and DUObj 
# but had to be changed due to __slots__

class Cutomization(DueUtilObject):
  
    __slots__ = ["_cutomization_info"]
    
    # Use kwargs so maybe I could neatly define cutomizations in code.
    def __init__(self,id,**cutomization_info):
        self._cutomization_info = cutomization_info
        super().__init__(id,self["name"])
    
    def __getattr__(self,name):
        """
        This helps customizations have both a dict & object
        interface
        """
        try:
            return self[name]
        except KeyError as exception:
            #### ULTRA WARNING!!!!!!!
            #### THIS ERROR MAY LIE
            raise AttributeError("%s has no attribute or index named %s" % (type(self).__name__,name)) from exception
            
    # Most cutomizations are read only & don't need to set values
            
    def __contains__(self, key):
        return key in self._cutomization_info
    
    def __getitem__(self,key):
        return self._cutomization_info[key]

class Theme(Cutomization):
  
    """
    Simple class to hold them data and
    be able to access DUObj methods
    
    Needs item setting & copying to support
    overriding theme attributes
    """
    
    __slots__ = []

    def __init__(self,id,**theme_data):
        super().__init__(id,**theme_data)
        
    def __copy__(self):
        return Theme(id,**self._cutomization_info)
        
    def __setitem__(self,key,value):
        self._cutomization_info[key] = value
        
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
 
class Background(Cutomization):
  
    __slots__ = ["image"]

    """
    Unlike Theme copy() & setting background data should
    never beed needed
    """
    
    def __init__(self,id,**background_data):
        super().__init__(id,**background_data)
        self.image = Image.open("backgrounds/"+self["image"])
      
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

class Banner(Cutomization):
    
    """Class to hold details & methods for a profile banner
    This class is based off a legacy class from DueUtil V1
    and hence does not properly Cutomization
    """
    
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
        super().__init__(id,**banner_data)
        
    def banner_restricted(self,player):
        member = discord.Member(user={"id":player.id})
        return ((not self.admin_only or self.admin_only and permissions.has_permission(member,Permission.DUEUTIL_ADMIN)) 
                and (not self.mod_only or self.mod_only and permissions.has_permission(member,Permission.DUEUTIL_MOD)))
        
    def can_use_banner(self,player):
        return (not self.donor or self.donor and player.donor) and self.banner_restricted(player)
