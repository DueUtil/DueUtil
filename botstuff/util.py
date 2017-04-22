import re
import math
import time
import zipfile
import shutil
import jsonpickle
import json
import logging
import emoji #The emoji list in this is outdated.

shard_clients = []
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dueutil')
    
class DueUtilException(ValueError):
  
    def __init__(self, channel,message, *args,**kwargs):
        self.message = message 
        self.channel = channel
        self.addtional_info = kwargs.get('addtional_info',"")
        
    def get_message(self):
        message = ":bangbang: **"+self.message+"**"
        if  self.addtional_info != "":
            message += "```css\n"+self.addtional_info+"```"
        return message
    
class DueReloadException(RuntimeError):
    
    def __init__(self,result_channel):
        self.channel = result_channel

async def say(channel,*args,**kwargs):
      return await get_client(channel.server.id).send_message(channel,*args,**kwargs)
      
async def typing(channel):
      await get_client(channel.server.id).send_typing(channel)

def load_and_update(reference,object):
    for item in dir(reference):
        if item not in dir(object):
            setattr(object,item,getattr(reference,item))
    return object
    
def get_shard_index(server_id):
    return (int(server_id) >> 22) % len(shard_clients)

def get_server_id(source):
    if isinstance(source,str):
        return source
    elif hasattr(source,'server'):
        return source.server.id
    elif isinstance(source,discord.Server):
        return source.id
  
def get_client(source):
    try:
        return shard_clients[get_shard_index(get_server_id(source))]
    except:
        return None
        
def ultra_escape_string(string):
    if not isinstance(string, str):
        return string
    escaped_string = string
    escaped = []
    for character in string:
        if not character.isalnum() and not character.isspace() and character not in escaped:
            escaped.append(character)
            escaped_string = escaped_string.replace(character,'\\'+character)
    return escaped_string
    
def format_number(number,**kwargs):
  
    def small_format():
        nonlocal number
        return '{:,g}'.format(number)

    def really_large_format():
        nonlocal number
        units = ["Million","Billion","Trillion", "Quadrillion","Quintillion","Sextillion","Septillion","Octillion"]
        reg = len(str(math.floor(number/1000)))
        if (reg-1) % 3 != 0:
            reg -= (reg-1) % 3
        number = number/pow(10,reg+2)
        try:
            string = " "+units[math.floor(reg/3) -1]
        except:
            string = " Fucktonillion"
        number = int(number*100)/float(100)
        formatted = '{0:g}'.format(number)
        return formatted + string if len(formatted) < 17 else str(math.trunc(number)) + string
        
    if number >= 1000000 and not kwargs.get('full_precision',False):
        formatted = really_large_format()
    else:
        formatted = small_format()
    return formatted if not kwargs.get('money',False) else '¤'+formatted
 
def char_is_emoji(character):
    if len(character) > 1:
        return False
    emojize = emoji.emojize(character,use_aliases=True)
    demojize = emoji.demojize(emojize)
    return emojize != demojize
  
def is_server_emoji(server,possible_emoji):
    possible_emojis = [str(emoji) for emoji in server.emojis if str(emoji) in possible_emoji]
    return len(possible_emojis) == 1 and possible_emojis[0] == possible_emoji
  
def get_server_name(server,user_id):
    try:
        return server.get_member(user_id).name
    except:
        return "Unknown User"
    
def clamp(number, min_val, max_val):
    return max(min(max_val, number), min_val)    
    
def filter_string(string):
    new = ""
    for i in range(0, len(string)):
        if 32 <= ord(string[i]) <= 126:
            new = new + string[i]
        else:
            new = new + "?"
    return new
    
def load(shards):
    global shard_clients
    shard_clients = shards
