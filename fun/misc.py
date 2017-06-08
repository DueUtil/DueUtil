import collections
import json
import discord
import urllib
from bs4 import BeautifulSoup
import requests
import io
from abc import ABC
from botstuff import util, dbconn

POSTIVE_BOOLS = ('true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh')
auto_replies = []

class AutoReply:
  
    def __init__(self,server_id,message,key,**kwargs):
        self.message = message
        self.key = key
        self.target = kwargs.get('target_user',None)
        self.server_id = server_id
        kwargs.get('channel_id',"all")
        
class DueUtilObject():
  
    NAME_LENGTH_RANGE = range(1,33)
    
    def __init__(self,id,*args,**kwargs):
        self.id = id
        self.no_save = kwargs.get("no_save",False)
        if len(args) > 0:
            self.name = args[0]
        
    @property
    def name_clean(self):
        return util.ultra_escape_string(self.name)
        
    @property
    def name_assii(self):
        return util.filter_string(self.name)
        
    @property
    def name_command(self):
        return '"'+self.name+'"' if " " in self.name else self.name
        
    @property
    def name_command_clean(self):
        return util.ultra_escape_string(self.name_command)
        
    @staticmethod
    def acceptable_string(string,max_len):
        return len(string) <= max_len and len(string) != 0 and string.strip != ""
        
    def save(self):
        if not self.no_save:
            dbconn.insert_object(self.id,self)
            
class DueUtilTheme(DueUtilObject,dict):
    
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
            self[theme_id] = DueUtilTheme(theme_id,**theme)
 
class DueUtilBackground(DueUtilObject,dict):
    
    def __init__(self,id,**background_data):
        self.update(background_data)
        super().__init__(id,self["name"])
                    
class Backgrounds(dict):
    
    def __init__(self):
        self.load_backgrounds()
      
    def load_backgrounds(self):
        self.clear()
        with open('backgrounds/backgrounds.json') as background_file:
            backgrounds = json.load(background_file)
        for background_id,background in backgrounds.items():
            self[background_id] = DueUtilBackground(background_id,**background)
                
class DueMap(collections.MutableMapping):
  
    """ 
    
    A 2D Mapping for things & items
    E.g. Key "ServerID/Name"
    or Server & Item
    where the key is Server.id/Item.name
   
    This mapping will return an empty dict or None
    if the server or item does not exist!
    
    Happens to be quite useful
    """
    
    def __init__(self):
        self.collection = dict()

    def __getitem__(self, key):
        key = self.__parse_key__(key)
        if isinstance(key,list):
            if key[0] in self.collection and key[1] in self.collection[key[0]]:
                return self.collection[key[0]][key[1]]
            return None
        if key in self.collection:
            return self.collection[key]
        return {}
        
    def __contains__(self, key):
        key = self.__parse_key__(key)
        if isinstance(key,list):
            return key[0] in self.collection and key[1] in self.collection[key[0]]
        return key in self.collection

    def __setitem__(self, key, value):
        key = self.__parse_key__(key, value)
        if isinstance(key,list):
            if key[0] not in self.collection:
                items = dict()
                items[key[1]] = value
                self.collection[key[0]] = items
            else:
                self.collection[key[0]][key[1]] = value
        else:
            self.collection[key] = value

    def __delitem__(self, key):
        key = self.__parse_key__(key)
        if isinstance(key,list):
            del self.collection[key[0]][key[1]]
        else:
            del self.collection[key]

    def __iter__(self):
        return iter(self.collection)

    def __len__(self):
        return len(self.collection)
        
    def __str__(self):
         return "DueMap(%s)" % str(self.collection)
         
    def __parse_key__(self, key, value = None):
        if isinstance(key,discord.Server):
            if value != None:
                return [key.id,value.name]
            return key.id
        elif "/" not in key:
            return key
        return key.split('/',1)
        
class Ring(list):
    
    def __init__(self,size):
        self += [None] * size
        self.size = size
        self.wrap_index = 0
        
    def __getitem__(self, index):
        return super(Ring,self).__getitem__(index % self.size)

    def __setitem__(self, index, value):
        try:
            super(Ring,self).__setitem__(index % self.size,value)
        except:
            self.__init__(self.size)
            self[index] = value
            
    def __delitem__(self, index):
        super(Ring,self).__delitem__(index % self.size)
        
    def append(self,item):
        try:
            next_index = self.index(None)
            self[next_index] = item
        except:
            self[self.wrap_index] = item
            self.wrap_index += 1
        
class Wizzard(ABC):
    
    def __init__(self,name,question_count):
        self.name = name
        self.complete = 0
        self.question_count = 0
        #self.message = util.say("Wizzard")
        
    def progress_bar():
        bar_width = 20
        progress = self.complete/self.question_count 
        bar_complete_len = progress* bar_width
        bar_incomplete_len = bar_width - bar_complete_len
        return '['+('"'*bar_complete_len)+(' '*bar_incomplete_len)+']'
         
def valid_image(bg_to_test,dimensions):
    if bg_to_test != None:
        width, height = bg_to_test.size
        if width == dimensions[0] and height == dimensions[1]:
            return True
    return False
    
def random_word():
    response = requests.get("http://randomword.setgetgo.com/get.php")
        
def get_glitter_text(gif_text):
    response = requests.get("http://www.gigaglitters.com/procesing.php?text="+urllib.parse.quote_plus(gif_text,safe='')
    +"&size=90&text_color=img/DCdarkness.gif&angle=0&border=0&border_yes_no=4&shadows=1&font='fonts/Super 911.ttf'")
    html = response.text
    soup = BeautifulSoup(html,"html.parser")
    box = soup.find("textarea", {"id": "dLink"})
    gif_text_area = str(box)
    gif_url = gif_text_area.replace('<textarea class="field" cols="12" id="dLink" onclick="this.focus();this.select()" readonly="">',"",1).replace('</textarea>',"",1)
    return io.BytesIO(requests.get(gif_url).content)
