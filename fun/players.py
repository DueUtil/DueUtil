import discord
import random
import math
import sys
import pickle;
import requests;
import botstuff.util;
import botstuff.imagehelper;
import string
import os;
import jsonpickle;
import hashlib;
from urllib.request import urlopen
import io
import time
import re;
import os;
import shutil
import dueutil;
import json;
from io import StringIO
import numpy
from argparse import Namespace
from PIL import Image

POSTIVE_BOOLS = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'];

loaded = False;

shard_clients = None;

""" DueUtil battles & quests. The main meat of the bot. """

def add_default_banner():
    global banners
    discord_blue_banner = player_info_banner("Discord Blue","info_banner.png");
    banners["discord blue"] = discord_blue_banner;
        
async def on_message(message): 
    await player_progress(message);

async def create_banner(message):
    global Banners;
    args = util.get_strings(message.content);
    try:
        name = args[0];
        url = args[1];
        donor = args[2] in postive_bools;
        admin = args[3] in postive_bools;
        mod = args[4] in postive_bools;
        banner = player_info_banner();
        image_name = upload_banner(url,name);
        if(image_name == None):
            await get_client(message.server.id).send_message(message.channel, ":interrobang: **Banner creation failed!**");
            return;
        banner.donor = donor;
        banner.banner_image_name = image_name;
        banner.name = name;
        banner.admin_only = admin;
        banner.mod_only = mod;
        Banners[re.sub(' +',' ',name.lower().strip()).lower().strip()] = banner;
        saveBanner(banner);
        reload_banners();
        await get_client(message.server.id).send_message(message.channel, ":white_check_mark: **"+name+"** is now a DueUtil banner!");
    except:
        await get_client(message.server.id).send_message(message.channel, ":interrobang: **Banner creation failed!**");
        
async def remove_banner(channel,name):
    if(delete_banner(name)):
        await get_client(message.server.id).send_message(channel, ":wastebasket: **Banner deleted!**");
        reload_banners();
    else:
        await get_client(message.server.id).send_message(channel, ":interrobang: **Banner not deleted!**\nAre you sure that you used the right name?");

def has_numbers(text):
   return any(char.isdigit() for char in text)

async def display_rank(message, find):
    players_of_higher_level = 0;
    players = 0;
    if(find == None):
        rplayer = findPlayer(message.author.id);
    else:
        rplayer = find;
    if(rplayer == None):
        return True;
    for member in message.server.members:
        player = findPlayer(member.id);
        if(player != None):
            players = players + 1;
            if(player.level > rplayer.level):
                players_of_higher_level = players_of_higher_level + 1;
    if(find == None):
        await get_client(message.server.id).send_message(message.channel, "You're **rank " + str(players_of_higher_level + 1) + "** out of " + str(players) + " players on **" + message.server.name + "**");
    else:
        await get_client(message.server.id).send_message(message.channel, rplayer.name + " is **rank " + str(players_of_higher_level + 1) + "** out of " + str(players) + " players on **" + message.server.name + "**");
        
async def show_banners_for_player(message,player):
    await util.simple_paged_list(message,util.get_server_cmd_key(message.server),"mybanners",get_banner_list_for_player(player).splitlines(),player.name+"'s banners");

def get_banner_list_for_player(player):
    banner_list ="";
    for key, banner in Banners.items():
        if can_use_banner(banner,player):
            banner_list += banner.name + "\n"; 
    return banner_list;
        
async def set_banner(channel,command_key,player,banner_name):
    banner_name = banner_name.lower().strip();
    if(banner_name in Banners.keys() and can_use_banner(Banners[banner_name],player)):
        player.banner_id = banner_name;
        await get_client(message.server.id).send_message(channel, "Your personal banner has been set to **" + Banners[banner_name].name + "**!"); 
        savePlayer(player)
    else:
        await get_client(message.server.id).send_message(channel, ":bangbang: **That's not a banner you have access to! **\nDo **" + command_key + "mybanners** to see the banners you have!"); 
    
def reload_banners():
    add_default_banner();
    loadBanners();
    load_banner_images();
     
def load(clients):
    global shard_clients;
    """
    shard_clients = clients;
    loadWeapons();
    loadPlayers();
    print(str(len(Players)) + " player(s) loaded.")
    defineWeapons();  
    add_default_banner();
    loadBanners();
    load_banner_images();
    print(str(len(Banners)) + " banners(s) loaded.")
    loadQuests();
    print(str(len(ServersQuests)) + " server(s) with quests loaded.")
    print(str(len(Weapons)) + " weapon(s) loaded.")
    #quest loading
    loadBackgrounds();
    load_awards();
    loaded = True;
    """
    
def load_backgrounds():
     Backgrounds.clear();
     for file in os.listdir("backgrounds"):
         if file.endswith(".png"):
             filename = str(file);
             background_name = filename.lower().replace("stats_", "").replace(".png", "").replace("_", " ").title();
             Backgrounds[background_name] = filename;
             
async def give_award(message, player, id, text):
    if(id not in player.awards):
        player.awards.append(id);
        savePlayer(player)
        if  message.channel.is_private or not(message.server.id+"/"+message.channel.id in util.mutedchan):
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** :trophy: **Award!** " + text);

async def give_award_id(message, userid, id, text):
    player = findPlayer(userid);
    if player == None:
        return;
    if(id not in player.awards):
        player.awards.append(id);
        savePlayer(player)
        if  message.channel.is_private or not(message.server.id+"/"+message.channel.id in util.mutedchan):
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** :trophy: **Award!** " + text);
  
def get_rank_colour(rank):
    if(rank == 1):
        return (255, 255, 255);
    elif (rank == 2):
        return (235, 196, 42);
    elif (rank == 3):
        return (235, 145, 42);
    elif (rank == 4):
        return (42, 235, 68);
    elif (rank == 5):
        return (174, 42, 235);
    elif (rank == 6):
        return (42, 103, 235);
    elif (rank == 7):
        return (163, 102, 90);
    elif (rank == 8):
        return (224, 33, 11);
    elif (rank > 8):
        return (15, 15, 15);
    return (255, 255, 255); 

async def does_bg_pass(channel,url):
    bg_to_test = loadImageFromURL(url);
    if(valid_image(bg_to_test,(256,299))):
        await get_client(message.server.id).send_message(channel,":thumbsup: **That looks good to me!**\nP.s. I can't check for low quality images!");
    elif (bg_to_test != None):
        width, height = bg_to_test.size;
        await get_client(message.server.id).send_message(channel,":thumbsdown: **That does not meet the requirements!**\nThe tested image had the dimensions ``"+str(width)+"*"+str(height)+"``!\nIt should be ``256*299``!");
    else:
        await get_client(message.server.id).send_message(channel,":thinking: Are you sure that 'background' is an image?");
        
async def upload_bg(channel,url,name):
    bg = loadImageFromURL_raw(url);
    if bg == None:
        await get_client(message.server.id).send_message(channel,":interrobang: **I can't resolve that url to an image!**");
        return;
    if not all(char.isalpha() or char.isspace() for char in name):
        await get_client(message.server.id).send_message(channel,":interrobang: **Background names can't have any special characters!**");
        return;
    name = re.sub(' +','_',name.lower().strip());
    if(valid_image(bg,(256,299))):
        if not os.path.isfile('backgrounds/'+name+".png"):
            bg.save('backgrounds/'+name+".png");
            loadBackgrounds();
            await get_client(message.server.id).send_message(channel,":sparkles: **"+name.strip().title().replace('_',' ')+"** is now a DueUtil background!");
        else:
            await get_client(message.server.id).send_message(channel,":interrobang: **A background of that name already exists!**");
    else:
        await get_client(message.server.id).send_message(channel,":interrobang: **That background is not vaild!**\nPlease test the background before accepting!");
        
def upload_banner(url,name):
    banner = loadImageFromURL_raw(url);
    if banner == None:
        return None;
    if not all(char.isalpha() or char.isspace() for char in name):
        return None;
    name = re.sub(' +','_',name.lower().strip());
    if os.path.isfile('screens/info_banners/'+name+".png"):
        return None;
    if(valid_image(banner,(155,51))):
        banner.save('screens/info_banners/'+name+".png");
        return name+".png";
    return None;
    
def delete_banner(name):
     global Banners;
     banner_name = name.strip().lower();
     if(banner_name == 'discord blue'):
        return False;
     if(banner_name in Banners.keys()):
        os.remove('screens/info_banners/'+Banners[banner_name].banner_image_name);
        os.remove('screens/info_banners/'+banner_name.replace(" ","_")+".json");
        del Banners[banner_name];
        return True;
     else:
        return False;
    
async def delete_bg(channel,name):
     background_name = name.strip().title();
     if(background_name == 'Default'):
        await get_client(message.server.id).send_message(channel,":interrobang: **Don't delete the default!**\n...It'd break me & my heart.");
        return;
     if(background_name in Backgrounds.keys()):
        os.remove("backgrounds/"+Backgrounds[background_name]);
        loadBackgrounds();
        await get_client(message.server.id).send_message(channel,":white_check_mark: **"+background_name+"** background deleted :wave:.\nIf this background was not one you accepted there will be questions.");
     else:
        await get_client(message.server.id).send_message(channel,":interrobang: **I can't find a background with that name to delete!**");

async def view_bg(channel,name):
    background_name = name.strip().title();
    if(background_name in Backgrounds.keys()):
        await get_client(message.server.id).send_typing(channel);
        img = rescale_image('backgrounds/'+Backgrounds[background_name],0.4);
        output = BytesIO()
        img.save(output,format="PNG")
        output.seek(0);
        await get_client(message.server.id).send_file(channel,fp=output,filename=Backgrounds[background_name],content=":frame_photo: Here is the background: **"+background_name+"**!");
    else:
        await get_client(message.server.id).send_message(channel,":bangbang: **I can't find a background with that name!**");   
        
async def view_banner(channel,name):
    banner_name = name.strip().lower();
    if(banner_name in Banners.keys()):
        await get_client(message.server.id).send_typing(channel);
        img = rescale_image("screens/info_banners/"+Banners[banner_name].banner_image_name,0.7);
        output = BytesIO()
        img.save(output,format="PNG")
        output.seek(0);
        await get_client(message.server.id).send_file(channel,fp=output,filename="banner.png",content=":frame_photo: Here is the banner: **"+Banners[banner_name].name+"**!");
    else:
        await get_client(message.server.id).send_message(channel,":bangbang: **I can't find a banner with that name!**"); 

def valid_image(bg_to_test,dimensions):
    if(bg_to_test != None):
        width, height = bg_to_test.size; 
        if(width == dimensions[0] and height == dimensions[1]):
            return True;
    return False;
                

        
async def player_progress(message):
    global money_created,new_players_joined,players_leveled,players;

    player = Player.find_player(message.author.id);
    if(player != None):
        if(player.w_id != NO_WEAPON_ID):
            if(player.weapon_sum != player.weapon.weapon_sum):
                await sell(message,player.user_id,True);
        await validate_weapon_store(message,player);
        
        if  time.time() - player.last_progress >= 60:
            player.last_progress = time.time();
            start_level = player.level;
            add_attack = len(message.content) / 600;
            if add_attack < 0.02:
                add_attack += 0.02;
                
            add_strg = sum(1 for char in message.content if char.isupper()) / 400;
            if add_strg < 0.03:
                add_strg += 0.03;
                
            add_accy = (message.content.count(' ') + message.content.count('.') + message.content.count("'")) / 3 / 200;
            if add_accy < 0.01:
                add_accy += 0.01;
                
            player.attack += add_attack;
            player.strg += add_strg;
            player.accy += add_accy;
            player.level += (player.attack + player.strg + player.accy -3) / 3 / math.pow(player.level, 3);                                          
            player.hp = 10 * player.level;
            
            if math.trunc(player.level) > math.trunc(start_level):
                level_up_reward = math.trunc(gplayer.level) * 10;
                player.money += level_up_reward;
                money_created += level_up_reward;
                players_leveled += 1;
                
                if not(message.server.id+"/"+message.channel.id in util.muted_channels):
                    await level_up_image(message,player, level_up_reward);
                else:
                    print("Won't send level up image - channel blocked.");
                    
                rank = int(player.level / 10) + 1;
                if(rank == 2):
                    await give_award(message, player, 2, "Attain rank 2.");
                elif (rank > 2 and rank <=9):
                    await give_award(message, player, rank+2, "Attain rank "+str(rank)+".");  
                print(filter_func(player.name)+" ("+player.userid+") has leveled up!");
                
            player.save();
    if player == None:
        new_player = Player(message.author);
        new_players_joined += 1;
        
async def show_limits_for_player(channel,player):
    limit = "You can use any weapon with a value up to **$"+util.to_money(max_value_for_player(player),False)+"**!";
    await get_client(message.server.id).send_message(channel, limit);
