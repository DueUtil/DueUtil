import collections
import discord
import urllib
from bs4 import BeautifulSoup
from abc import ABC
from botstuff import util, dbconn
import generalconfig as gconf 
import aiohttp

POSTIVE_BOOLS = ('true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh')
auto_replies = []
GLIITER_TEXT_URL = ("http://www.gigaglitters.com/procesing.php?text=%s"
                    +"&size=90&text_color=img/DCdarkness.gif"
                    +"&angle=0&border=0&border_yes_no=4&shadows=1&font='fonts/Super 911.ttf'")

class AutoReply:
  
    """
    Auto reply
    (Not going to be used)
    """
    
    def __init__(self,server_id,message,key,**kwargs):
        self.message = message
        self.key = key
        self.target = kwargs.get('target_user',None)
        self.server_id = server_id
        kwargs.get('channel_id',"all")
        
class DueUtilObject():
  
    """
    Base object for DueUtil items
    """
    
    __slots__ = ["no_save","id","name"]
  
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
        return ('"'+self.name+'"' if " " in self.name else self.name).lower()
        
    @property
    def name_command_clean(self):
        return util.ultra_escape_string(self.name_command)
        
    @staticmethod
    def acceptable_string(string,max_len):
        return len(string) <= max_len and len(string) != 0 and string.strip != ""
        
    def __str__(self):
        # Support objects that might have icons.
        # (Customizations, weapons, possibly more)
        try:
            return "%s | %s" % (self.icon, self.name_clean)
        except AttributeError:
            try:
                return "%s | %s" % (self["icon"], self.name_clean)
            except KeyError:
                return self.name_clean
              
    def save(self):
        if not self.no_save:
            dbconn.insert_object(self.id,self)
            
#### MacDue's wacky data clases (monkey patches)
            
class DueMap(collections.MutableMapping):
  
    """ 
    
    A 2D Mapping for things & items
    E.g. Key "ServerID/Name"
    or Server & Item
    where the key is Server.id/Item.name
    
    or key with addtional data:
      some.id+data/item.name
      (some id can't contain any '/' or '+'s)
      and the data can't contain any '/'s
   
    This mapping will return an empty dict or None
    if the server or item does not exist!
    
    Happens to be quite useful
    
    """
    
    def __init__(self):
        self.collection = dict()

    def __getitem__(self, key):
        key = self._parse_key(key)
        if isinstance(key,list):
            if key[0] in self.collection and key[1] in self.collection[key[0]]:
                return self.collection[key[0]][key[1]]
            return None
        if key in self.collection:
            return self.collection[key]
        return {}
        
    def __contains__(self, key):
        key = self._parse_key(key)
        if isinstance(key,list):
            return key[0] in self.collection and key[1] in self.collection[key[0]]
        return key in self.collection

    def __setitem__(self, key, value):
        key = self._parse_key(key, value)
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
        key = self._parse_key(key)
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
         
    def _parse_key(self, key, value = None):
        if isinstance(key,discord.Server):
            if value != None:
                return [key.id,value.name]
            return key.id
        elif "/" not in key:
            return key
        key = key.split('/',1)
        if '+' in key[0]:
            key[0] = key[0].split('+')[0]
        return key
        
class Ring(list):
    
    """
    Like a list but a fixed number of elements.
    If you try to append past the end it overwrites an
    element at the start of the ring
    """
    
    def __init__(self,size):
        self.clear()
        self += [None] * size
        self.size = size
        self.wrap_index = 0
        
    def __getitem__(self, index):
        return super(Ring,self).__getitem__(index % self.size)

    def __setitem__(self, index, value):
        self._setitem(index,value)
            
    def _setitem(self,index,value,depth=0):
        try:
            super(Ring,self).__setitem__(index % self.size,value)
        except:
            self.__init__(self.size)
            if depth == 0: self._setitem(index,value,depth+1)    
            
    def __delitem__(self, index):
        super(Ring,self).__delitem__(index % self.size)
        
    def append(self,item):
        try:
            next_index = self.index(None)
            self[next_index] = item
        except:
            self[self.wrap_index] = item
            self.wrap_index += 1
            
#### End - MacDue's wacky data clases
        
class Wizzard(ABC):
  
    """
    WIP - Setup wizzard
    """
    
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
     
def paginator(item_add):
    
    """
    Very simple paginator for embeds
    """
    
    def page_getter(item_list,page,title,**extras):
        page_size = 12
        page_embed = discord.Embed(title=title+(" : Page "+str(page+1) if page > 0 else ""),type="rich",color=gconf.EMBED_COLOUR)
        if page * page_size >= len(item_list):
            raise util.DueUtilException(None,"Page not found")
        for item_index in range(page_size*page,page_size*page+page_size):
            if item_index >= len(item_list):
                break
            item_add(page_embed,item_list[item_index],**extras)
        if page_size * page + page_size < len (item_list):
            page_embed.set_footer(text=extras.get('footer_more',"There's more on the next page!"))
        else:
            page_embed.set_footer(text=extras.get('footer_end',"That's all!"))
        return page_embed  
    return page_getter
         
"""    
def random_word():
    response = requests.get("http://randomword.setgetgo.com/get.php")
"""

async def get_glitter_text(gif_text):
  
    """
    Screen scrape glitter text
    """
    
    with aiohttp.Timeout(10):
        async with aiohttp.get(GLIITER_TEXT_URL % urllib.parse.quote(gif_text.strip("'"))) as page_response:
            html = await page_response.text()
            soup = BeautifulSoup(html,"html.parser")
            box = soup.find("textarea", {"id": "dLink"})
            gif_text_area = str(box)
            gif_url = gif_text_area.replace('<textarea class="field" cols="12" id="dLink" onclick="this.focus();this.select()" readonly="">',"",1).replace('</textarea>',"",1)
            return await util.download_file(gif_url)
