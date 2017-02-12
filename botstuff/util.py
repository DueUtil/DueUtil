import discord
import random
import requests
import re
from urllib import request, parse
from bs4 import BeautifulSoup
import os.path
from datetime import datetime
import math
import sys
from html.parser import HTMLParser
import time;
import fun.players;
import zipfile;
import shutil;
import jsonpickle;
import json;

loaded = False;
due_admins=[];
due_mods=[];
muted_channels = [];
servers = dict();
server_keys = dict();
shard_clients = [];
    
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    
class DueUtilException(ValueError):
  
    def __init__(self, channel,message, *args,**kwargs):
        self.message = message 
        self.channel = channel
        self.addtional_info = kwargs.get('addtional_info',"");
        super(DueUtilException, self).__init__(message,channel,*args) 
        
    def get_message(self):
        message = ":bangbang: **"+self.message+"**";
        if  self.addtional_info != "":
            message += "```css\n"+self.addtional_info+"```";
        return message;
    
    
async def say(channel,*args,**kwargs):
      await get_client(channel.server.id).send_message(channel,*args,**kwargs);
      
async def typing(channel):
      await get_client(channel.server.id).send_typing(channel);

def get_shard_index(server_id):
    return (int(server_id) >> 22) % len(shard_clients);

def get_client(source):
    try:
        if isinstance(source,str):
            return shard_clients[get_shard_index(source)];
        elif hasattr(source,'server'):
            return shard_clients[get_shard_index(source.server.id)];
        else:
            return shard_clients[get_shard_index(source.id)];
    except:
        return None;
        
def get_server_cmd_key(server):
    server_key = server_keys.setdefault(server.id,"!");
    return server_key if server_key != '`' else '\`';
    
def format_number(number,**kwargs):
  
    def small_format():
        nonlocal number;
        return '{:,g}'.format(number);

    def really_large_format():
        nonlocal number;
        units = ["Million","Billion","Trillion", "Quadrillion","Quintillion","Sextillion","Septillion","Octillion"];
        reg = len(str(math.floor(number/1000)));
        if (reg-1) % 3 != 0:
            reg -= (reg-1) % 3;
        number = number/pow(10,reg+2)
        try:
            string = units[math.floor(reg/3) -1];
        except:
            string = "Fucktonillion";
        number = int(number*100)/float(100);
        formatted = '{0:g}'.format(number);
        return formatted if len(formatted) < 17 else str(math.trunc(number)) + " " + string;
        
    if number >= 1000000 and not kwargs.get('full_precision',False):
        formatted = really_large_format();
    else:
        formatted = small_format();
    return formatted if not kwargs.get('money',False) else '¤'+formatted;
 
def char_is_emoji(character):
    return emoji_pattern.match(character);
  
def get_server_name(server,user_id):
    try:
        return server.get_member(user_id).name;
    except:
        return "Unknown User"
    
def paginate():
    """ This always was shit. Replace it. """
    
def is_admin(id):
    return id in DueUtilAdmins or id == '132315148487622656';
    
def is_mod(id):
    return id in DueUtilMods or id == '132315148487622656';
    
def is_mod_or_admin(id):
    return id in DueUtilAdmins or id in DueUtilMods or id =='132315148487622656';

def save_json(thing,file_path):
    data = jsonpickle.encode(thing);
    with open(file_path+'.json', 'w') as outfile:
        json.dump(data, outfile);

def load_json(path):
    with open(path) as data_file:    
        data = json.load(data_file);
        unpickled = jsonpickle.decode(data);
        return unpickled;

def filter_string(string):
    new = "";
    for i in range(0, len(string)):
        if(32 <= ord(string[i]) <= 126):
            new = new + string[i];
        else:
            new = new + "?";
    return new;                
        
def load(shards):
    global shard_clients;
    shard_clients = shards;
    '''
    global client;
    global DueUtilAdmins;
    global DueUtilMods;
    global AutoReplys;
    global mutedchan;
    global serverKeys;
    global servers;
    global loaded;
    global stopped;
    client = discord_client;
    test =  load_utils("server_keys");
    if test != None:
        serverKeys = test;
    test =  load_utils("due_admins");
    if test != None:
        DueUtilAdmins = test;
    test =  load_utils("due_mods");
    if test != None:
        DueUtilMods = test;
    test =  load_utils("auto_replys");
    if test != None:
        AutoReplys = test;
    test =  load_utils("mute_channels");
    if test != None:
        muted_channels = test;
    loaded = True;
    '''
