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
auto_replies = [];
muted_channels = [];
servers = dict();
server_keys = dict();
shard_clients = [];

class AutoReply:
  
    message = "";
    key = "";
    target = "";
    attarget = False;
    server = "";
    username ="";
    timed = "";
    alt = "";
    channel = None;
    
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
    
def get_server_name(message,id):
    return get_server_name_S(message.server,id);

def get_server_name_S(server,id):
    try:
        return server.get_member(id).name;
    except:
        return "Unknown User"
    
async def simple_paged_list(message,command_key,command_name,item_list,title):
    page = 0;
    end_cmd = message.content.lower().replace(command_key + command_name, "");
    if(len(end_cmd.replace(" ", "")) > 0):
        try:
            page = int(end_cmd) - 1;
        except:
            await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
            return;
    if(page < 0):
        await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
        return;
    if(page == 0):
        text_list = "```css\n["+title+"]\n";
    else:
        text_list = "```css\n["+title+": Page " + str(page + 1) + "]\n";
    if(page * 10 > len(item_list) - 1):
        await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
        return;
    for x in range(page * 10, page * 10 + 10):
        if(x < len(item_list)):
            text_list += str(x + 1) + ". " + item_list[x] + "\n";
        else:
            break;
    if(x < len(item_list) - 1):
        text_list += "[Do " + command_key + command_name + " " + str(page + 2) + " to see more.]";
    text_list += "```";
    await client.send_message(message.channel, text_list);   
       
def get_page_with_replace(data,page,key,server):
    output ='```\n';
    test = output;
    if(not isinstance(data, list)):
        if(len(data)+6 < 2000):
            return ['```\n'+data+'```',False]
        data = data.splitlines();
    #for x in range (0,page):
        #test = test + '``````'
    for line in data:   
        if(key != None and server != None):
            text = line.replace("[CMD_KEY]",key).replace("[SERVER]",server);
        else:
            text = line;
        if(not ('\n' in text)):
            text = text + '\n';
        new_ln = output+ text;
        test += text;
        if(len(test) >= 1997*page):          
            if(len(test) < 1997*(page+1) and len(new_ln) <= 1997):
                output = new_ln;
            else:
                return [output+'```',True];
    output = output + '```';
    if('``````' in output):
        return None;
    #print(output);
    return [output,False]
    
	
def get_page(data,page):
	return get_page_with_replace(data,page,None,None);
	
async def display_with_pages(message,data,command,title,title_not_page_one,constant_footer,footer_no_next_page):
	command_key = get_server_cmd_key(message.server);
	page = 0;
	args = message.content.lower().replace(command_key + command,"");
	body = data;
	footer_to_send =constant_footer+"\n";
	title_to_send ="";
	if(len(args) > 0):
		try:
			page = int(args) - 1;
			if(page < 0):
				await client.send_message(message.channel, ":bangbang: **Page not found**");
				return;
		except:
			await client.send_message(message.channel, ":bangbang: **Page not found**");
			return;
	page_data = get_page(data,page);
	if(page_data == None or (page > 0 and len(data)+6 < 2000)):
		await client.send_message(message.channel, ":bangbang: **Page not found!**");
		return;
	else:
		body=page_data[0];
		if(page > 0):
			title_to_send = title_not_page_one+": Page "+str(page+1);
		else:
			title_to_send = title;
		title_to_send = "**"+title_to_send+"**";
		if(page_data[1]):
			footer_to_send += "**But wait there's more** type **"+command_key+command+" "+str(page+2)+"** to have a look!"
		else:
			footer_to_send += footer_no_next_page;
	await client.send_message(message.channel, title_to_send);
	await client.send_message(message.channel, body);
	await client.send_message(message.channel,footer_to_send);
    
def is_admin(id):
    return id in DueUtilAdmins or id == '132315148487622656';
def is_mod(id):
    return id in DueUtilMods or id == '132315148487622656';
def is_mod_or_admin(id):
    return id in DueUtilAdmins or id in DueUtilMods or id =='132315148487622656';
    
#async def on_util_message(message):
   
    
async def mod_admin_manage(message,role,award_id,role_list):
    
    
    command_key = get_server_cmd_key(message.server);
    if ((message.author.id == "132315148487622656") or is_admin(message.author.id)) and message.content.lower().startswith(command_key+'add'+role):
       
       
        rUser = userMentions(message);
        if(len(rUser)==1):
            if(not (rUser[0] in role_list)):
                role_list.append(rUser[0]);
                await client.send_message(message.channel,"**"+get_server_name(message, rUser[0])+"** is now a DueUtil "+role+"!");
                print(role+" "+rUser[0]+" added by "+message.author.id);
                await battlesquests.give_award_id(message,rUser[0],award_id,"Become an "+role+"!")
            else:
                await client.send_message(message.channel,"**"+get_server_name(message, rUser[0])+"** is already an "+role+"!");
        else:
            await client.send_message(message.channel,":bangbang: **Mention one user you would like to promote!**");
        return role_list;    
    
    
    elif ((message.author.id == "132315148487622656") or is_admin(message.author.id)) and message.content.lower().startswith(command_key+'remove'+role):
        
      
        rUser = userMentions(message);
        if(len(rUser)==1):
            if((rUser[0] in role_list)):
                del role_list[role_list.index(rUser[0])];
                print(role+" "+rUser[0]+" removed by "+message.author.id);
                await client.send_message(message.channel,"**"+get_server_name(message, rUser[0])+"** is no longer a DueUtil "+role+".");
                player = battlesquests.findPlayer(rUser[0]);
                del player.awards[player.awards.index(award_id)];
            else:
                await client.send_message(message.channel,"**"+get_server_name(message, rUser[0])+"** is not an "+role+" anyway!");
        else:
            await client.send_message(message.channel,":bangbang: **Mention one user you would like to demote.**");
        return role_list;
    
    
    return None;

def save_generic(thing,name):
    data = jsonpickle.encode(thing);
    with open("saves/util/" + name+ ".json", 'w') as outfile:
        json.dump(data, outfile);

def load_utils(name):
    try:
        with open("saves/util/"+name+".json") as data_file:    
                data = json.load(data_file);
                du = jsonpickle.decode(data);
                print(str(len(du))+" "+name+"(s) loaded")
                return du;
    except:
        print("Failed to load "+name+"!")
        print ("Error:", sys.exc_info()[0]);
        return None;

def get_strings(mainStr):
    Strs = [];
    Start = False;
    for x in range (0,len(mainStr)):
        if mainStr[x] == '"':
            if Start == False:
                Strs.append("");
            Start = not Start;
        elif Start:
            Strs[len(Strs)-1]=Strs[len(Strs)-1]+mainStr[x];
    if not Start:
        return Strs;
    else:
        return [];
       
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


def zipdir(path, fname):
    zipf = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()

def user_mentions(message):
    text = message.content.replace("@!","");
    text = text.replace("@","");
    userMentions = [];
    mainStr = text;
    Start = False;
    for x in range (0,len(mainStr)):
        if mainStr[x] == '<' or mainStr[x] == '>':
            if Start == False:
                userMentions.append("");
            Start = not Start;
        elif Start:
            userMentions[len(userMentions)-1]=userMentions[len(userMentions)-1]+mainStr[x];
    #print(len(userMentions));
    if not Start:
        return userMentions;
    else:
        return False;

def clear_mentions(message):
    mainStr = message;
    cleanStr ="";
    Start = False;
    for x in range (0,len(mainStr)):
        if mainStr[x] == '<' and mainStr[:x+2].endswith('@'):
            Start = True;
        elif mainStr[x] == '>' and Start:
            Start = False;
        elif not Start:
            cleanStr = cleanStr + mainStr[x];
    return cleanStr;

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

async def random_word(message):
    try:
        response = requests.get("http://randomword.setgetgo.com/get.php");
        await createGlitterText(message, response.text);
    except:
        await client.send_message(message.channel, "An error occured.");
        print ("Error details.");
        print ("Unexpected error:", sys.exc_info()[0]);

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



