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
players = dict();         #Players
awards = [];
banners = dict();         #Banners
backgrounds = dict();     #Backgrounds
shard_clients = None;

#DueUtil stats
money_created = 0;
money_transferred =0;
players_leveled=0;
new_players_joined=0;

""" DueUtil battles & quests. The main meat of the bot. """

class Award:

    def __init__(self,icon_path,name,description):
        self.name = name;
        self.description = description;
        self.icon = Image.open(icon_path);
        
    def register(icon_path,text):
        global awards;
        info = text.split('\n');
        awards.append(Award(icon_path,info[0],info[1]));
        
    @staticmethod
    def get_award(award_id):
        return awards[award_id]; 

    @staticmethod          
    def load():
        load_award("awards/Duseless.png","Duseless\nIgnore DueUtil");  # 0
        load_award("awards/questDone.png","Save The Server\nComplete a quest");  # 1
        load_award("awards/rank2.png","Attain Rank 2\nGet to level 10");  # 2
        load_award("awards/redmist.png","Red Mist\nFail a quest");  # 3
        load_award("awards/spender.png","Licence To Kill\nBuy a weapon");  # 4
        load_award("awards/rank3.png","Attain Rank 3\nGet to level 20");  # 5
        load_award("awards/rank4.png","Attain Rank 4\nGet to level 30");  # 6
        load_award("awards/rank5.png","Attain Rank 5\nGet to level 40");  # 7
        load_award("awards/rank6.png","Attain Rank 6\nGet to level 50");  # 8
        load_award("awards/rank7.png","Attain Rank 7\nGet to level 60");  # 9
        load_award("awards/rank8.png","Attain Rank 8\nGet to level 70");  # 10
        load_award("awards/rank9.png","Attain Rank 9\nGet to level 80");  # 11
        load_award("awards/forharambe.png","For Harambe\n???");  # 12
        load_award("awards/youwin.png","Win A Wager\nDon't not win a wager");  # 13
        load_award("awards/beat.png","Lose A Wager\nDon't win a wager");  # 14
        load_award("awards/daddy.png","Dumbledore\n???"); # 15
        load_award("awards/benfont.png","One True Type Font\n???"); # 16
        load_award("awards/givecash.png","Sugar Daddy\nGive another player over or $50"); # 17
        load_award("awards/potato.png","Bringer Of Potatoes\nGive a potato"); # 18
        load_award("awards/kingtat.png","Potato King\nGive out 100 potatoes"); # 19
        load_award("awards/kingtat.png","Potato King\nGive out 100 potatoes"); # 20
        load_award("awards/admin.png","DueUtil Admin\nOnly DueUtil admins can have this."); # 21
        load_award("awards/mod.png","DueUtil Mod\nOnly DueUtil mods can have this."); # 22
        load_award("awards/bg_accepted.png","Background Accepted!\nGet a background submission accepted");#23
        load_award("awards/top_dog.png","TOP DOG\nWhile you have this award you're undefeated"); #24
        load_award("awards/donor_award.png","All MacDue Ever Wanted!\nDonate to DueUtil"); #25


class PlayerInfoBanner:
    
    """Class to hold details & methods for a profile banner"""
    
    def __init__(self,name,image_name,**kwargs):
      
        self.price = kwargs.get('price',0);
        self.donor = kwargs.get('donor',False);
        self.admin_only = kwargs.get('admin_only',False);
        self.mod_only = kwargs.get('mod_only',False);
        self.unlock_level = kwargs.get('unlock_level',0);
        
        self.image_name = image_name;
        self.name = name;
        self.load_image();
        
    def banner_restricted(self,player):
        return ((not banner.admin_only or banner.admin_only == util.is_admin(player.userid)) 
                and (not banner.mod_only or banner.mod_only == util.is_mod_or_admin(player.userid)));
        
        
    def can_use_banner(self,player):
        return (not banner.donor or banner.donor == player.donor) and self.banner_restricted(player);
        
    def load_image(self):
        self.image = imagehelper.set_opacity(Image.open('screens/info_banners/'+image_name),0.9);
        
    @staticmethod
    def load():
        global banners;
        banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png");
      
class Player:
  
    """The DueUtil player!"""
  
    def __init__(self,*args):
        global players;
        self.user_id = args[0].id if len(args) > 0 and isinstance(args[0],discord.Member) else "";
        self.reset();
        players[self.user_id] = self;

    def reset(self):
        self.benfont = False;
        self.level = 1;
        self.attack = 1;
        self.strg = 1;
        self.accy = 1;
        self.banner_id = "discord blue";
        self.hp = 10;
        self.donor = False;
        self.background = "default.png";
        self.weapon_sum = '"0"01'     #price/attack/sum;
        self.name = "Put name here";
        self.w_id = NO_WEAPON_ID;
        self.money = 0;
        self.last_progress = 0;
        self.last_quest = 0;
        self.wagers_won = 0;
        self.quests_won = 0;
        self.potatos_given = 0;
        self.quest_day_start = 0;
        self.potatos = 0;
        self.quests_completed_today = 0;
        self.last_image_request = 0;
        self.quests = [];
        self.battlers = [];
        self.awards = [];
        self.owned_weps = [];
        self.save();
        
    def owns_weapon(self,weapon_name):
        for weapon_slot in self.owned_weps:
            if(Weapon.get_weapon_from_id(weapon_slot[0]).name.lower() == weapon_name.lower()):
                return True;
        return False;
        
    @property    
    def weapon_accy(self):
        max_value = self.max_value_for_player();
        price = self.weapon.price if self.weapon.price > 0 else 1;
        new_accy = numpy.clip(max_value/price * 100,1,86);
        new_accy = weapon.chance if new_accy > weapon.chance else new_accy;
        return new_accy if price > max_value else self.weapon.chance;
    
    def max_value_for_player(self):
        if not util.is_admin(self.user_id):
            return 10 * (math.pow(self.level,2)/3 + 0.5 * math.pow(self.level+1,2) * self.level);
        else:
            return math.inf;  #Best new feature!
            
    async def unequip_weapon(self,channel):
        if weapon.w_id != no_weapon_id:
            if len(self.owned_weps) < 6:
                if not self.owns_weapon(self.weapon.name):
                    self.owned_weps.append([active_wep.wID,self.weapon_sum]);
                    self.wID = no_weapon_id;
                    self.weapon_sum = weapons(no_weapon_id).weapon_sum;
                    await util.say(channel, ":white_check_mark: **"+active_wep.name+"** unequiped!");
                else:
                    raise util.DueUtilException(channel,"You already have a weapon with that name stored!"); 
            else:
                raise util.DueUtilException(channel, "No room in your weapon storage!");
        else:
            raise util.DueUtilException(channel,"You don't have anything equiped anyway!");
            
    def save(self):
        data = jsonpickle.encode(self);
        with open("saves/players/" + self.user_id + ".json", 'w') as outfile:
            json.dump(data, outfile);
            
    @property
    def weapon(self):
        return weapons[self.w_id];
        
    @property
    def banner(self):
        banner = banners.get(self.banner_id,banners["discord blue"]);
        if not banner.can_use_banner(player):
            player.banner_id = "discord blue";
            return banners["discord blue"];
        return banner;
        
    def get_avatar_url(self,*args):
        server = args[0];
        member = server.get_member(self.user_id);
        if member.avatar_url != "":
           return member.avatar_url;
        else:
           return member.default_avatar_url;
        
    @staticmethod
    def find_player(user_id):
        global players;
        
        if(user_id in players):
            return players[user_id]
        else:
            return None;

def add_default_banner():
    global banners
    discord_blue_banner = player_info_banner("Discord Blue","info_banner.png");
    banners["discord blue"] = discord_blue_banner;
    
def add_quest(quest):
    global server_quests;
    
    server_quests[quest.server_id][quest.monster_name.lower()] = quest;
    save_quest(quest);
    
def add_weapon(weapon):
    global weapons;
    weapons[weapon.w_id] = weapon;
    save_weapon(weapon);
        
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
    
def filter_func(string):
    new = "";
    for i in range(0, len(string)):
        if(32 <= ord(string[i]) <= 126):
            new = new + string[i];
        else:
            new = new + "?";
    return new;
  
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
                
def save_banner(banner):
    data = jsonpickle.encode(banner);
    with open("screens/info_banners/" + banner.name.lower().replace(" ","_")+ ".json", 'w') as outfile:
        json.dump(data, outfile);
        
def load_banner_images():
    global banners;
    for key, banner in banners.items():
        banner.image = load_image_and_set_opacity("screens/info_banners/"+banner.banner_image_name,0.9);
        
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
