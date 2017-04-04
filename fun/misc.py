import os
import collections
import json
import discord
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
    
    def __init__(self,id,*args,**kwargs):
        self.id = id
        self.no_save = kwargs.get("no_save",False)
        if len(args) > 0:
            self.name = args[0]
        
    @property
    def clean_name(self):
        return util.ultra_escape_string(self.name)
        
    @property
    def assii_name(self):
        return util.filter_string(self.name)
        
    def save(self):
        if not self.no_save:
            dbconn.insert_object(self.id,self)
        
class Themes(dict):
  
    def __init__(self):
        self.load_themes()
  
    def load_themes(self):
        with open('fun/configs/themes.json') as themes_file:  
            themes = json.load(themes_file)
        self.update(themes["themes"])
        for theme in self.values():
            theme["background"] = theme["background"]+".png"
            if "rankColours" not in theme:
                theme["rankColours"] = themes["rankColours"]
        
class Backgrounds(dict):
    
    def __init__(self):
        self.load_backgrounds()
      
    def load_backgrounds(self):
        self.clear()
        for background in os.listdir("backgrounds"):
            if background.endswith(".png"):   
                background_name = background.lower().replace("stats_", "").replace(".png", "").replace("_", " ").title()
                self[background_name] = background
                
class DueMap(collections.MutableMapping):
  
    """ 
    
    A 2D Mapping for servers & items
    Key "ServerID/Name"
    or Server & Item
    where the key is Server.id/Item.name
   
    This mapping will return an empty dict or None
    if the server or item does not exist!
    """
    
    def __init__(self):
        self.servers = dict()

    def __getitem__(self, key):
        key = self.__parse_key__(key)
        if isinstance(key,list):
            if key[0] in self.servers and key[1] in self.servers[key[0]]:
                return self.servers[key[0]][key[1]]
            return None
        if key in self.servers:
            return self.servers[key]
        return {}

    def __setitem__(self, key, value):
        key = self.__parse_key__(key, value)
        if key[0] not in self.servers:
            items = dict()
            items[key[1]] = value
            self.servers[key[0]] = items
        else:
            self.servers[key[0]][key[1]] = value

    def __delitem__(self, key):
        del self.servers[self.__parse_key__(key)[0]]

    def __iter__(self):
        return iter(self.servers)

    def __len__(self):
        return len(self.servers)

    def __parse_key__(self, key, value = None):
        if isinstance(key,discord.Server):
            if value != None:
                return [key.id,value.name]
            return key.id
        elif "/" not in key:
            return key
        return key.split('/',1)
        
def valid_image(bg_to_test,dimensions):
    if bg_to_test != None:
        width, height = bg_to_test.size
        if width == dimensions[0] and height == dimensions[1]:
            return True
    return False
    
async def random_word(message):
    response = requests.get("http://randomword.setgetgo.com/get.php")
    await create_glitter_text(message, response.text)
        
async def create_glitter_text(channel,gif_text):
    response = requests.get("http://www.gigaglitters.com/procesing.php?text="+parse.quote_plus(gif_text)
    +"&size=90&text_color=img/DCdarkness.gif&angle=0&border=0&border_yes_no=4&shadows=1&font='fonts/Super 911.ttf'")
    html = response.text
    soup = BeautifulSoup(html,"html.parser")
    box = soup.find("textarea", {"id": "dLink"})
    gif_text_area = str(box)
    gif_url = gif_text_area.replace('<textarea class="field" cols="12" id="dLink" onclick="this.focus();this.select()" readonly="">',"",1).replace('</textarea>',"",1)
    gif = io.BytesIO(requests.get(gif_url).content)
    await client.send_file(message.channel,fp=gif,filename='glittertext.gif')
