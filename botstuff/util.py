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
import fun.battlesquests;
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

def get_shard_index(server_id):
    return (int(server_id) >> 22) % len(shard_clients);

def get_client(server_id):
    return shard_clients[get_shard_index(server_id)];

def get_server_cmd_key(server):
    server_key = server_keys.setdefault(server.id,"!");
    return server_key if server_key != '`' else '\`';
    
def clear_markdown_escapes(text):
    return text.replace("\`","`");

def to_money(amount,short):
    if(short):
      return number_format(amount);
    else:
      return number_format_text(amount);
    
def number_format_text(number):
    return '{:20,.0f}'.format(number).strip();
    
def number_format(number):
    if(number < 1000000):
        return number_format_text(number);
    else:
        return really_large_number_format(number);

def really_large_number_format(number):
    units = ["Million","Billion","Trillion", "Quadrillion","Quintillion","Sextillion","Septillion","Octillion"];
    if(number >= 1000000):
      reg = len(str(math.floor(number/1000)));
      if ((reg-1) % 3 != 0):
        reg -= (reg-1) % 3;
      num = number/pow(10,reg+2)
      try:
          string = units[math.floor(reg/3) -1];
      except:
          string = "Fucktonillion";
      num = (int(num*100)/float(100));
      formatted = format_float_drop_zeros_drop(num,False) + " " + string;
      return formatted if len(formatted) < 17 else format_float_drop_zeros_drop(num,True) + " " + string;
    else:
      return number_format(number);
      
def format_float_drop_zeros(number):
    return format_float_drop_zeros_drop(number,False);
    
def format_float_drop_zeros_drop(number,drop):
    num = str(number);
    if(len(num) > 3 and drop):
        num = str(math.trunc(number));
    return (num+"-").replace(".0-","").replace("-","")

def escape_markdown(text):
    return text.translate(str.maketrans({"`":  r"\`"})).replace("\n","");
    
def get_server_name(server,id):
    try:
        return server.get_member(id).name;
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

async def random_word(message):
    response = requests.get("http://randomword.setgetgo.com/get.php");
    await create_glitter_text(message, response.text);
        

async def create_glitter_text(channel,gif_text):
    response = requests.get("http://www.gigaglitters.com/procesing.php?text="+parse.quote_plus(gif_text)
    +"&size=90&text_color=img/DCdarkness.gif&angle=0&border=0&border_yes_no=4&shadows=1&font='fonts/Super 911.ttf'");
    html = response.text;
    soup = BeautifulSoup(html,"html.parser");
    box = soup.find("textarea", {"id": "dLink"});
    gif_text_area = str(box);
    gif_url = gif_text_area.replace('<textarea class="field" cols="12" id="dLink" onclick="this.focus();this.select()" readonly="">',"",1).replace('</textarea>',"",1);
    gif = io.BytesIO(requests.get(gif_url).content);
    await client.send_file(message.channel,fp=gif,filename='glittertext.gif');



