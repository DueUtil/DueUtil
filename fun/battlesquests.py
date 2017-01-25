import discord
import random
import math
import sys
import pickle;
import requests;
import util_due as util;
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
from io import BytesIO;
import json;
from PIL import Image, ImageDraw, ImageFont
from io import StringIO
import numpy
from argparse import Namespace

POSTIVE_BOOLS = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'];
NO_WEAPON_ID = "000000000000000000_none";
STOCK_WEAPONS = ["stick","laser gun","gun","none","frisbee"];

loaded = False;
players = dict();         #Players
award_icons = [];         #AwardIcons
awards_names = [];        #AwardNames
banners = dict();         #Banners
servers_quests = dict();  #ServerQuests
weapons = dict();         #Weapons
backgrounds = dict();     #Backgrounds
shard_clients = None;

#DueUtil fonts
font = ImageFont.truetype("fonts/Due_Robo.ttf", 12);
font_big = ImageFont.truetype("fonts/Due_Robo.ttf", 18);
font_med = ImageFont.truetype("fonts/Due_Robo.ttf", 14);
font_small = ImageFont.truetype("fonts/Due_Robo.ttf", 11);
font_epic = ImageFont.truetype("fonts/benfont.ttf", 12);
info_avatar = Image.open("screens/info_avatar.png");

#DueUtil stats
images_served =0;
money_created = 0;
money_transferred =0;
quests_attempted=0;
players_leveled=0;
new_players_joined=0;
quests_given=0;

""" DueUtil battles & quests. The main meat of the bot. """

class PlayerInfoBanner:
    
    """Class to hold details & methods for a profile banner"""
    
    def __init__(self,name,image_name,**kwargs):
      
        self.price = kwargs.get('price',0);
        self.donor = kwargs.get('donor',False);
        self.admin_only = kwargs.get('admin_only',False);
        self.mod_only = kwargs.get('mod_only',False);
        self.unlock_level = kwargs.get('unlock_level',0);
        
        self.banner_image_name = image_name;
        self.name = name;
        self.image = None;
        
    def can_use_banner(self,player):
        return (not banner.donor or banner.donor == player.donor) and self.banner_restricted(player);
        
        
class Weapon:
  
    """A simple weapon that can be used by a monster or player in DueUtil"""
    
    def __init__(self,message,name,accy,damage,**kwargs):
      
        if does_weapon_exist(server,name):
            raise util.DueUtilException(message.channel,"A weapon with that name already exists on this server!");
            
        if len(name) > 30 or len(name) == 0 or name.strip == "":
            raise util.DueUtilException(message.channel,"Weapon names must be between 1 and 30 characters!");
            
        if accy == 0 or damage == 0:
            raise util.DueUtilException(message.channel,"No weapon stats can be zero!");
        
        if accy > 86 or accy < 1:
            raise util.DueUtilException(message.channel,"Accuracy must be between 1% and 86%!");
        
        self.server_id = message.server_id;
        self.icon = kwargs.get('icon',"!")
        self.hit_text = kwargs.get('hit_text',"hits");
        self.melee = kwargs.get('melee',True);
        self.image_url = kwargs.get('image_url',"");
  
        self.name = name;
        self.damage = damage;
        self.accy = accy;
        self.price = self.__price();
        self.w_id = self.__weapon_id();
        self.weapon_sum = self.__weapon_sum();
        
        add_weapon(self);
            
    def __weapon_id(self):
        return self.server_id+"_"+self.name.lower();
        
    def __weapon_sum(self):
        return '"'+str(self.price)+'"'+str(self.damage)+str(weapon.accy);
      
    def __price(self):
        return (self.accy/100 * self.damage) / 0.04375; 
      
    @staticmethod
    def get_weapon_from_id(id):
        if(id in Weapons):
            return Weapons[id]
        else:
            if(id != no_weapon_id):
                return Weapons[no_weapon_id];
    @staticmethod
    def does_weapon_exist(server_id,weapon_name):   
        if(get_weapon_for_server(server_id,weapon_name) != None):
            return True;
        return False;
    
    @staticmethod
    def get_weapon_for_server(server_id,weapon_name):
        if(weapon_name.lower() in stock_weapons):
            return Weapons["000000000000000000_"+weapon_name.lower()];
        else:
            weapon_id = server_id+"_"+weapon_name.lower();
            if(weapon_id in Weapons):
                return Weapons[weapID]
            else:
                return None;
                
    @staticmethod
    def remove_weapon_from_shop(player,wname):
        for weapon in player.owned_weps:
            stored_weapon = get_weapon_from_id(weapon[0]);
            if(stored_weapon != None and stored_weapon.name.lower() == wname.lower()):
                wID = weapon[0];
                sum = weapon[1];
                del player.owned_weps[player.owned_weps.index(weapon)];
                return [wID,sum];
        return None;
        
    @staticmethod
    def save_weapon(weapon):
        data = jsonpickle.encode(weapon);
        with open("saves/weapons/" + str(hashlib.md5(weapon.wID.encode('utf-8')).hexdigest()) + ".json", 'w') as outfile:
            json.dump(data, outfile);   
      
        
class Quest:
  
    """A class to hold info about a server quest"""
  
    def __init__(self,message,name,base_attack,base_strg,base_accy,base_hp,**kwargs):
      
        if message.server.id in server_quests:
            if name.strip().lower() in server_quests[message.server.id]:
                raise util.DueUtilException(message.channel,"A foe with that name already exists on this server!");
      
        if base_accy < 1 or base_attack < 1 or base_strg < 1:
            raise util.DueUtilException(message.channel,"No quest stats can be less than 1!");

        if base_hp < 30:
            raise util.DueUtilException(message.channel,"Base HP must be at least 30!");

        if len(name) > 30 or len(name) == 0 or name.strip == "":
            raise util.DueUtilException(message.channel,"Quest names must be between 1 and 30 characters!");
      
        self.task = kwargs.get('task',"Battle a");
        self.w_id = kwargs.get('weapon_id',no_weapon_id);
        self.spawnchance = kwargs.get('spawn_chance',4);
        self.image_url = kwargs.get('image_url',"");
        
        self.monster_name = name;
        self.base_attack = base_attack;
        self.server_id = message.server_id;
        self.base_strg = base_strg;
        self.base_accy = base_accy;
        self.base_hp = base_hp;
        
        created_by = message.author.id;
        
        base_reward = self__reward();
        self.q_id = self.__quest_id();
        
        add_quest(self);
        
    def __quest_id(self):
        return '"'+self.server_id+'""'+self.monster_name.lower()+'"';
      
    def __reward(self):
        if(Weapon.get_weapon_from_id(self.w_id).melee):
            base_reward = (self.base_attack + self.base_strg) / 10 / 0.0883;
        else:
            base_reward = (self.base_accy + self.base_strg) / 10 / 0.0883;
    
        base_reward += base_reward * math.log10(self.base_hp) / 20 / 0.75;
        base_reward *= self.base_hp / abs(self.base_hp - 0.01);
        
        return base_reward;
                        
    @property
    def made_on():
        return self.server_id;
        
    @staticmethod
    def get_game_quest_from_id(id):
        id  = str(id);
        args = util.get_strings(id);
        if(len(args) == 2 and args[0] in ServersQuests and args[1] in ServersQuests[args[0]]):
            return ServersQuests[args[0]][args[1]];
        else:
            return None;
        
class BattleRequest:
  
    """A class to hold a wager"""
  
    def __init__(self,message,wager_amount):
        self.sender_id = message.author.id;
        self.wager_amount = wagers_amount;
    
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
        
    def limit_weapon_accy(self):
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
        
    @staticmethod
    def find_player(user_id):
        global players;
        
        if(user_id in players):
            return players[user_id]
        else:
            return None;
   
class ActiveQuest(Player):
  
    def __init__(self,q_id):
        self.q_id = q_id;
        super(ActiveQuest,self).__init__();
        
def add_default_banner():
    global banners
    
    discord_blue_banner = player_info_banner();
    discord_blue_banner.name = "Discord Blue";
    Banners["discord blue"] = discord_blue_banner;
    
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


async def buy_weapon(message,command_key):
    messageArg = message.content.lower().replace(command_key + "buy ", "", 1);
    Found = False;
    try:
        weapon = get_weapon_for_server(message.server.id, messageArg.strip());
        if(weapon != None and weapon.name != "None"):
            if ((weapon.server == "all") or (weapon.server == message.server.id)) and weapon.price != -1:
                Found = True;
                player = findPlayer(message.author.id);
                if(player == None):
                    return True;
                if((player.money - weapon.price) >= 0):
                    if(weapon.price <= max_value_for_player(player)):
                        if(len(player.owned_weps) < 6 or player.wID == no_weapon_id):
                            if(player.wID == no_weapon_id):
                                player.wID = weapon.wID;
                                await harambe_check(message,weapon,player);
                                await give_award(message, player, 4, "License to kill.");
                                player.wep_sum = get_weapon_sum(weapon.wID)
                                await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** bought a " + weapon.name + " for $" +  util.to_money(weapon.price,False) + "!");
                            else:
                                if not owns_weapon_name(player,weapon.name.lower()):
                                    player.owned_weps.append([weapon.wID,get_weapon_sum(weapon.wID)]);
                                    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** bought a " + weapon.name + " for $" +  util.to_money(weapon.price,False) + "!");
                                    await get_client(message.server.id).send_message(message.channel, ":warning: You have not yet equiped this weapon yet.\nIf you want to equip this weapon do **"+command_key+"equipweapon "+weapon.name.lower()+"**.");
                                else:
                                    await get_client(message.server.id).send_message(message.channel, ":bangbang: **You already have a weapon with that name stored!**"); 
                            player.money = player.money - weapon.price;
                            savePlayer(player);             
                        else:
                            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** you have no free weapon slots! Sell one of your weapons first!");
                    else:
                        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You're currently too weak to wield that weapon!**\nFind a weapon that better suits your limits with **"+command_key+"mylimit**");
                        
                else:
                    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** you can't afford this weapon.\nYou need **$"+util.to_money(weapon.price-player.money,False)+"** more.");
    except:
        Found = False;
    if(not Found):
        await get_client(message.server.id).send_message(message.channel, "Weapon not found!"); 

   
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
        
async def equip_weapon(message,player,wname):
    storedWeap = remove_weapon_from_store(player,wname);
    if(storedWeap != None):
        if owns_weapon_name(player,get_weapon_from_id(player.wID).name):
            player.owned_weps.append(storedWeap);
            await get_client(message.server.id).send_message(message.channel, ":bangbang: **Cannot put your current equiped weapon in your weapon storage as a weapon with the same name is already being stored!**"); 
            return;
        if(player.wID != no_weapon_id):
            player.owned_weps.append([player.wID,player.wep_sum]);
        player.wID = storedWeap[0];
        player.wep_sum = storedWeap[1];
        newWeap = get_weapon_from_id(player.wID);
        if(newWeap.wID != no_weapon_id):
            await harambe_check(message,newWeap,player);
            await get_client(message.server.id).send_message(message.channel, ":white_check_mark: **"+newWeap.name+"** equiped!");
        else:
            await get_client(message.server.id).send_message(message.channel, ":white_check_mark: equiped!");
        savePlayer(player);
    else:
        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You do not have that weapon stored!**");
        
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
  
    
def banner_restricted(banner,player):
    return (not banner.admin_only or banner.admin_only == util.is_admin(player.userid)) and (not banner.mod_only or banner.mod_only == util.is_mod_or_admin(player.userid));
    
async def validate_weapon_store(message,player):
    weapon_sums = [];
    for ws in player.owned_weps:
        if(ws[1] != get_weapon_sum(ws[0])):
            weapon_sums.append(ws[1]);
            del player.owned_weps[player.owned_weps.index(ws)];
    if len(weapon_sums) > 0:
        await mass_recall(message,player,weapon_sums);        

async def sell(message, uID, recall):
    await sell_weapon(message,uID,recall,None); 

async def mass_recall(message, player, weapon_sums):
    refund = 0;
    for sum in weapon_sums:
        refund = refund + int(util.get_strings(sum)[0]);
    player.money = player.money + refund;
    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** a weapon or weapons you have stored have been recalled by the manufacturer. You get a full $" + util.to_money(refund,False) + " refund.");
    savePlayer(player);
    
async def sell_weapon(message, uID, recall,weapon_name):
    global Players;
    global Weapons;
    player = findPlayer(uID);
    if (player == None):
        return True;
    weapon_id= no_weapon_id;
    if(weapon_name == None):
        weapon_id = player.wID;
    else:
        weapon_data = remove_weapon_from_store(player,weapon_name);
        if(weapon_data == None):
            if(get_weapon_from_id(player.wID).name.lower() == weapon_name):
                weapon_name = None;
                weapon_id = player.wID;
            if(weapon_name != None):
                await get_client(message.server.id).send_message(message.channel, ":bangbang: **Weapon not found!**");
                return;
        if(weapon_data != None):
            weapon_id = weapon_data[0];
    if (weapon_id != no_weapon_id):
        weapon = get_weapon_from_id(weapon_id);
        price = int(((weapon.chance/100) * weapon.attack) / 0.04375);
        sellPrice = int(price - (price / 4));
        if(not recall):
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** sold their trusty " +weapon.name + " for $" +util.to_money(sellPrice,False)+ "!");
        else:
            if(weapon_name == None):
                sellPrice = int(util.get_strings(player.wep_sum)[0]);
            else:
                sellPrice = int(util.get_strings(weapon_data[1])[0]);
            #print(util.get_strings(player.wep_sum));
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** your weapon has been recalled by the manufacturer. You get a full $" + util.to_money(sellPrice,False) + " refund.");
        if(weapon_name == None):
            player.wID = no_weapon_id;
            player.wep_sum = get_weapon_sum(no_weapon_id)
        player.money = player.money + sellPrice;
        savePlayer(player);
    else:
        await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** nothing does not fetch a good price...");

def get_server_quest_list(server):
    number = 0;
    text = "";
    if(server.id in ServersQuests):
        for quest in ServersQuests[server.id].values():
            number = number + 1;
            text = text + str(number) + ". " + quest.quest + " [" + quest.monsterName + "] \n";  
    if(number == 0):
        text =  "There isn't any quests on this server!\n";
    return text;
    
async def show_quest_list(message):
    title = message.server.name + " Quests**\n**Square brackets indicate quest name.";
    title_not_first_page = message.server.name + " Quests";
    last_page_footer ="That's it!"
    await util.display_with_pages(message,get_server_quest_list(message.server),"serverquests",title,title_not_first_page,"",last_page_footer);
        
async def show_weapons(message,player,not_theirs):
    eweap = get_weapon_from_id(player.wID);
    output = "```"+player.name+"'s stored weapons\nEquipped: "+eweap.icon+" - "+eweap.name+"\n";
    #check wep not removed/replaced
    num = 1;
    for ws in player.owned_weps:
        weap = get_weapon_from_id(ws[0]);
        if(weap != None):
            if(weap.melee == True):
                Type = "Melee";
            else:
                Type = "Ranged";
            accy = round(weap.chance,2);
            output = output+str(num)+". "+weap.icon + " - " + weap.name + " | DMG: " + util.number_format_text(weap.attack) + " | ACCY: " + (str(accy)+"-").replace(".0-","").replace("-","") + "% | Type: " + Type + " |\n";
            num=num+1;
    if(len(player.owned_weps) == 0):
        if(not not_theirs):
            output = output + "You don't have any weapons stored!```";
        else:
            output = output + player.name+" does not have any weapons stored!```";
    else:
        if(not not_theirs):
            cmd = util.get_server_cmd_key(message.server);
            output = output+"Use "+cmd+"equipweapon [Weapon Name] to equip a stored weapon!\nUse "+cmd+"unequipweapon to store your equiped weapon.```";
        else:
            output = output + "```";
    await get_client(message.server.id).send_message(message.channel, output);
    
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
             
def load_awards():
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
    
def load_award(icon_path,name):
    global AwardsIcons;
    global AwardsNames;
    AwardsIcons.append(Image.open(icon_path));
    AwardsNames.append(name);
    
async def shop(message):
    normal_title = "Welcome to DueUtil's weapon shop!";
    #past_page_one_title = "DueUtil's weapon shop";
    #constant_footer = "Type **" + util.get_server_cmd_key(message.server) + "buy [Weapon Name]** to purchase a weapon.";
    #final_page_footer = "Want more? Ask a server manager to add stock!";
    #await util.display_with_pages(message,get_server_weapon_list(message),"shop",normal_title,past_page_one_title,constant_footer,final_page_footer);

    
def get_server_weapon_list(message):
    global Weapons;
    weapon_listings = "";
    count = 0;
    for key in Weapons.keys():
        if key.startswith(message.server.id) or key.startswith("000000000000000000"):
            weapon = Weapons[key];
            if(weapon.price != -1 and weapon.wID != no_weapon_id):
                count = count + 1;
                Type = "";
                if(weapon.melee == True):
                    Type = "Melee";
                else:
                    Type = "Ranged";
                accy = round(weapon.chance,2);
                weapon_listings = weapon_listings + str((count)) + ". " + weapon.icon + " - " + weapon.name + " | DMG: " + util.number_format_text(weapon.attack) + " | ACCY: " + util.format_float_drop_zeros(accy) + "% | Type: " + Type + " | $" +  util.to_money(weapon.price,False)+ " |\n";	
    return weapon_listings;     
            
def filter_func(string):
    new = "";
    for i in range(0, len(string)):
        if(32 <= ord(string[i]) <= 126):
            new = new + string[i];
        else:
            new = new + "?";
    return new;
    
def resize_avatar(player, server, q, w, h):    
    if(not q):
        u = server.get_member(player.userid);
        if(u.avatar_url != ""):
            img = loadImageFromURL(u.avatar_url);
        else:
            img = loadImageFromURL(u.default_avatar_url);
    else:
        img = loadImageFromURL(get_game_quest_from_id(player.qID).image_url);
        if(img == None):
            return None;
    img = img.resize((w, h), Image.ANTIALIAS);
    return img;

def resize_image_url(url, w, h):    
    img = loadImageFromURL(url);
    if(img == None):
        return None;
    img = img.resize((w, h), Image.ANTIALIAS);
    return img;
    
def rescale_image(path, scale):    
    img = Image.open(path);
    width, height = img.size;
    if(img == None):
        return None;
    img = img.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS);
    return img;

async def level_up_image(message, player, cash):
    global images_served;
    images_served = images_served +1;
    level = math.trunc(player.level);
    try:
        avatar = resize_avatar(player, message.server, False, 54, 54);
    except:
        avatar = None;
    img = Image.open("screens/level_up.png");
    if(avatar != None):
        img.paste(avatar, (10, 10));
    draw = ImageDraw.Draw(img)
    draw.text((159, 18), str(level), (255, 255, 255), font=font_big)
    draw.text((127, 40), "$" + util.to_money(cash,True), (255, 255, 255), font=font_big)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="level_up.png",content=":point_up_2: **"+player.name+"** Level Up!");
    output.close()


async def new_quest_image(message, quest, player):
    global images_served;
    images_served = images_served +1;
    try:
        avatar = resize_avatar(quest, message.server, True, 54, 54);
    except:
        avatar = None;
    img = Image.open("screens/new_quest.png"); 
    if(avatar != None):
        img.paste(avatar, (10, 10));
    draw = ImageDraw.Draw(img)
    g_quest = get_game_quest_from_id(quest.qID);
    draw.text((72, 20), get_text_limit_len(draw,util.clear_markdown_escapes(g_quest.quest),font_med,167), (255, 255, 255), font=font_med)
    level_text = " LEVEL " + str(math.trunc(quest.level));
    width = draw.textsize(level_text, font=font_big)[0]
    draw.text((71, 39), get_text_limit_len(draw,util.clear_markdown_escapes(g_quest.monsterName),font_big,168-width) + level_text, (255, 255, 255), font=font_big)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="new_quest.png",content=":crossed_swords: **"+player.name+"** New Quest!");
    output.close()

async def awards_screen(message, player,page):
    global images_served;
    images_served = images_served +1;
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10):
        await get_client(message.server.id).send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    sender.last_image_request = time.time();
    #player.last_image_request = time.time();
    await get_client(message.server.id).send_typing(message.channel);
    img = Image.open("screens/awards_screen.png"); 
    a_s = Image.open("screens/award_slot.png"); 
    draw = ImageDraw.Draw(img)
    t = "'s Awards";
    pageInfoLen = 0;
    if(page > 0):
        pageInfo = ": Page "+str(page+1);
        t += pageInfo;
        pageInfoLen = draw.textsize(pageInfo, font=font)[0]
    name = get_text_limit_len(draw,util.clear_markdown_escapes(player.name),font,175-pageInfoLen); 
    t=name+t;
        
    draw.text((15, 17), t,(255,255,255), font=font)
    c = 0;
    l = 0;
    x = 0;
    for x in range(len(player.awards) - 1 - (5*page), -1, -1):
         img.paste(a_s, (14, 40 + 44 * c));
         draw.text((52, 47 + 44 * c), AwardsNames[player.awards[x]].split("\n")[0],  (48, 48, 48), font=font_med)
         draw.text((52, 61 + 44 * c), AwardsNames[player.awards[x]].split("\n")[1],  (48, 48, 48), font=font_small)
         img.paste(AwardsIcons[player.awards[x]], (19, 45 + 44 * c));
         c = c + 1;
         msg = "";
         if(c == 5):
             if(x != 0):
                 a = "myawards";
                 if(message.content.lower().startswith(util.get_server_cmd_key(message.server)+"awards")):
                     a = "awards @User";
                 msg = "+ "+str(len(player.awards)-(5*(page+1)))+" More. Do "+filter_func(util.get_server_cmd_key(message.server))+a+" "+str(page+2)+" for the next page.";
             break;
    if (x == 0):
        msg = "That's all folks!"
    if (len(player.awards) == 0):
        name = get_text_limit_len(draw,util.clear_markdown_escapes(player.name),font,100);
        msg = name+" doesn't have any awards!";
    width = draw.textsize(msg, font=font_small)[0]
    draw.text(((256-width)/2, 42 + 44 * c),msg,  (255, 255, 255), font=font_small)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="awards_list.png",content=":trophy: **"+player.name+"'s** Awards!");
    output.close()


async def battle_image(message, pone, ptwo, btext):
    global images_served;
    images_served = images_served +1;
    sender = findPlayer(message.author.id);
    sender.last_image_request = time.time();
    await get_client(message.server.id).send_typing(message.channel);
    try:
        if(not isinstance(pone, activeQuest)):
            avatar_one = resize_avatar(pone, message.server, False, 54, 54);
        else:
            avatar_one = resize_avatar(pone, message.server, True, 54, 54);
    except:
        avatar_one = None;
    #print(not isinstance(ptwo, activeQuest));
    try:
        if(not isinstance(ptwo, activeQuest)):
            avatar_two = resize_avatar(ptwo, message.server, False, 54, 54);
        else:
            avatar_two = resize_avatar(ptwo, message.server, True, 54, 54);
    except:
        avatar_two = None;
    weapon_one = get_weapon_from_id(pone.wID);
    weapon_two = get_weapon_from_id(ptwo.wID);
    img = Image.open("screens/battle_screen.png");   
    width, height = img.size;
    if(avatar_one != None):
        img.paste(avatar_one, (9, 9));
    if(avatar_two != None):
        img.paste(avatar_two, (width - 9 - 55, 9));
        
    wep_image_one = resize_image_url(weapon_one.image_url, 30, 30);
    
    if(wep_image_one == None):
        wep_image_one = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30);
		
    try:
        img.paste(wep_image_one, (6, height - 6 - 30), wep_image_one);
    except:
        img.paste(wep_image_one, (6, height - 6 - 30));
        
    wep_image_two = resize_image_url(weapon_two.image_url, 30, 30);
    
    if(wep_image_two == None):
        wep_image_two = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30);
    try:
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30), wep_image_two);
    except:
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30));
        
    draw = ImageDraw.Draw(img)
    draw.text((7, 64), "LEVEL " + str(math.trunc(pone.level)), (255, 255, 255), font=font_small)
    draw.text((190, 64), "LEVEL " + str(math.trunc(ptwo.level)), (255, 255, 255), font=font_small)
    weap_one_name = get_text_limit_len(draw,util.clear_markdown_escapes(weapon_one.name),font,85)
    width = draw.textsize(weap_one_name, font=font)[0]
    draw.text((124 - width, 88), weap_one_name, (255, 255, 255), font=font)
    draw.text((132, 103), get_text_limit_len(draw,util.clear_markdown_escapes(weapon_two.name),font,85), (255, 255, 255), font=font)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="battle.png");
    await get_client(message.server.id).send_message(message.channel,btext);
    output.close()

        
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


def loadImageFromURL(url):
    # Image cache!
    fname = 'imagecache/' + re.sub(r'\W+', '', (url));
    if (len(fname) > 128):
        fname = fname[:128];
    fname = fname + '.jpg';
    if(os.path.isfile(fname)):
        return Image.open(fname);    
    else:
        try:
            response = requests.get(url, timeout=10)
            if 'image' not in response.headers.get('content-type'):
                return None;
            image_file = io.BytesIO(response.content);
            img = Image.open(image_file);
            img.convert('RGB').save(fname, optimize=True, quality=20);
            return img;
            del response
        except:
            if(os.path.isfile(fname)):
                os.remove(fname);
            return None;

def loadImageFromURL_raw(url):
    try:
        response = requests.get(url, timeout=10)
        if 'image' not in response.headers.get('content-type'):
            return None;
        image_file = io.BytesIO(response.content);
        img = Image.open(image_file);
        return img;
        del response
    except:
        if(os.path.isfile(fname)):
            os.remove(fname);
        return None;
            
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
                    
def json_test(playerT):
    datum = json.dumps(playerT, default=lambda o: o.__dict__);
    print(datum);
    rebuild = json.loads(datum, object_hook=lambda d: Namespace(**d))
    print(rebuild.quests[0].name);
 
def update_player_def(p):
    if not hasattr(p,'owned_weps'):
        setattr(p,'owned_weps',[]);
    if not hasattr(p,'quests_completed_today'):
        setattr(p,'quests_completed_today',0);
    if not hasattr(p,'quest_day_start'):
        setattr(p,'quest_day_start',0);
    if('@here' in p.name or '@everyone' in p.name):
        p.name ='DueUtil Player';
    return p;
    
def load_players():
    global Players;
    for file in os.listdir("saves/players/"):
        if file.endswith(".json"):
            with open("saves/players/" + str(file)) as data_file:    
                try:
                    data = json.load(data_file);
                    p = jsonpickle.decode(data);
                    p = update_player_def(p);
                    Players[p.userid] = p;
                except:
                    print("Failed to load player data!");
  
def load_banners():
    global Banners;
    for file in os.listdir("screens/info_banners/"):
        if file.endswith(".json"):
            with open("screens/info_banners/" + str(file)) as data_file:    
                try:
                    data = json.load(data_file);
                    banner = jsonpickle.decode(data);
                    Banners[banner.name.lower()] = banner;
                except:
                    print("Failed to load banner data!");
                
def get_sus_list():
    global Players;
    count = 0;
    out = "";
    for player in Players.values():
        weapon =  get_weapon_from_id(player.wID);
        hasOPweapStore = "No";
        for weap in player.owned_weps:
            if(get_weapon_from_id(weap[0]).price >= 50000):
                hasOPweapStore = "Yes";
                break;
        if(player.money >= 1000000000000 or weapon.price >= 50000 or hasOPweapStore == "Yes"):
            count = count +1;
            out = out + str(count)+". "+player.name + " ("+player.userid+") | Cash $"+util.to_money(player.money,False)+" | Weapon Value $"+util.to_money(weapon.price,False)+" | Suspicious Stored Weapons - "+hasOPweapStore+" \n"
    if (count == 0):
        return  'All looks good.';
    return out;
    
async def exploit_check(message):
    normal_title = "These players seem suspicious...";
    past_page_one_title = "Suspicious players";
    final_page_footer = "That's all who've found out how broken DueUtil is!";
    await util.display_with_pages(message,get_sus_list(),"checkusers",normal_title,past_page_one_title,"",final_page_footer);

    
        
async def take_weapon(message,player):
    player.owned_weps = [];
    player.wID = no_weapon_id;
    player.wep_sum = get_weapon_sum(no_weapon_id);
    await get_client(message.server.id).send_message(message.channel,"All weapons taken from **"+player.name+"**!");
    savePlayer(player);
    
async def wipe_cash(message,player):
    player.money = 0;
    await get_client(message.server.id).send_message(message.channel,"Reset **"+player.name+"**'s cash!");
    savePlayer(player);

async def clear_suspicious(message):
    global Players;
    count = 0;
    admins = 0;
    for player in Players.values():
        weapon =  get_weapon_from_id(player.wID);
        hasOPweapStore = False;
        for weap in player.owned_weps:
            if(get_weapon_from_id(weap[0]).price >= 50000):
                hasOPweapStore = True;
                break;
        if player.money >= 1000000000000 or weapon.price >= 50000 or hasOPweapStore:
            if(not util.is_mod_or_admin(player.userid)):
                count = count + 1;
                player.money = 0;
                player.wID = no_weapon_id;
                player.wep_sum = get_weapon_sum(no_weapon_id);
                player.owned_weps = [];
                savePlayer(player);
            else:
                admins = admins +1;
    if(count > 0):
        await get_client(message.server.id).send_message(message.channel,":white_check_mark: **Suspicious money and weapons confiscated from "+str(count)+" user(s)!**");
        if(admins > 0):
            await get_client(message.server.id).send_message(message.channel,str(admins)+" admin(s) or mod(s) omitted.");
    else:
        await get_client(message.server.id).send_message(message.channel,"No suspicious users!");
            
def load_weapons():
    global Weaponse;
    for file in os.listdir("saves/weapons/"):
        if file.endswith(".json"):
            with open("saves/weapons/" + str(file)) as data_file:    
                try:
                    data = json.load(data_file);
                    w = jsonpickle.decode(data);
                    if(w.update):
                        w.chance = update_chance(True,w.chance);
                        w.update = False;
                        saveWeapon(w);
                    Weapons[w.wID] = w;
                except:
                    print("Weapon data corrupt!");
                
def update_chance(is_weapon,chance):
    if(not is_weapon):
        return 25 if chance > 25 else chance;
    else:
        return 86 if chance > 86 else chance;

def save_banner(banner):
    # data = ba.dumps(player, default=lambda o: o.__dict__);
    data = jsonpickle.encode(banner);
    with open("screens/info_banners/" + banner.name.lower().replace(" ","_")+ ".json", 'w') as outfile:
        json.dump(data, outfile);
        
def save_quest(quest):
    # data = json.dumps(player, default=lambda o: o.__dict__);
    data = jsonpickle.encode(quest);
    args = util.get_strings(quest.qID);
    with open("saves/gamequests/" + args[0] + "_"+str(hashlib.md5(quest.monsterName.lower().encode('utf-8')).hexdigest())+".json", 'w') as outfile:
        json.dump(data, outfile);
        
def load_quests():
    global ServersQuests;
    for file in os.listdir("saves/gamequests/"):
        if file.endswith(".json"):
            with open("saves/gamequests/" + str(file)) as data_file:    
                try:
                    data = json.load(data_file);
                    q = jsonpickle.decode(data);
                    if(q.baseattack < 1 or q.basestrg < 1 or q.basehp < 30 or q.baseshooting < 1):
                        os.remove("saves/gamequests/" + str(file));
                        print("Quest removed! - Invalid stats!");
                        continue;
                    if(q.update):
                        q.spawnchance = update_chance(False,q.spawnchance);
                        q.update = False;
                        saveQuest(q);
                    args = util.get_strings(q.qID);
                    if(len(args) == 2):
                        if(args[0] in ServersQuests):
                            ServersQuests[args[0]][args[1]] = q;
                        else:
                            ServersQuests[args[0]]=dict();
                            ServersQuests[args[0]][args[1]] = q;
                    else:
                        print("Failed to load quest!")
                except:
                    print("Quest data corrupt!");  
        
def find_name(server,uID):
    p = findPlayer(uID);
    if(p != None):
        return p.name;
    else:
        return util.get_server_name_S(server,uID);
    

        
def get_text_limit_len(draw,text,given_font,length):
    removed_chars = False;
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    for x in range(0, len(text)):
        width = draw.textsize(text, font=given_font)[0];
        if(width > length):
            text = text[:len(text)-1];
            removed_chars = True;
        else:
            if removed_chars:
                if (given_font != font_epic):
                    return text[:-1] + u"\u2026"
                else:
                    return text[:-3] + "..."
            return text;

def load_image_and_set_opacity(image_path,opacity_level):
    opacity_level = int(255*opacity_level) # Opaque is 255, input between 0-255
    image = Image.open(image_path).convert('RGBA')
    pixeldata = list(image.getdata())
    for i,pixel in enumerate(pixeldata):
        pixeldata[i] = pixel[:3] +(opacity_level,);
    image.putdata(pixeldata)
    return image
        
def load_banner_images():
    global banners;
    for key, banner in banners.items():
        banner.image = load_image_and_set_opacity("screens/info_banners/"+banner.banner_image_name,0.9);
        
def get_player_banner(player):
    banner = banners.get(player.banner_id,banners["discord blue"]);
    if(not can_use_banner(banner,player)):
        player.banner_id = "discord blue";
        return Banners["discord blue"].image;
    return banner.image;
            
async def display_stats_image(player, q, message):
    global images_served;
    images_served = images_served +1;
    sender = Player.find_player(message.author.id);
    print(players);
    if(time.time() - sender.last_image_request < 10):
        await util.say(message.channel,":cold_sweat: Please don't break me!");
        return;
    sender.last_image_request = time.time();
    
    await util.get_client(message.server.id).send_typing(message.channel);
    if(q):
        await displayQuestImage(player, message);
        return;
    try:
        avatar = resize_avatar(player, message.server, q, 80, 80);
    except:
        avatar = None;
    
    level = math.trunc(player.level);
    attk = round(player.attack, 2);
    strg = round(player.strg, 2);
    shooting = round(player.accy, 2)
    name = util.clear_markdown_escapes(player.name);
    try:
        img = Image.open("backgrounds/" + player.background);
    except:
        img = Image.open("backgrounds/default.png");
        
    screen = Image.open("screens/info_screen.png");   
    
    draw = ImageDraw.Draw(img);
    img.paste(screen,(0,0),screen)
    
    #draw_banner
    #player_banner = get_player_banner(player);
    
    #img.paste(player_banner,(91,34),player_banner);
    
    #draw_avatar slot
    img.paste(info_avatar,(3,6),info_avatar);
     
    if(player.benfont):
        name=get_text_limit_len(draw,filter_func(name.replace(u"\u2026","...")),font_epic,149)
        draw.text((96, 42),name, get_rank_colour(int(level / 10) + 1), font=font_epic)
    else:
        name=get_text_limit_len(draw,name,font,149)
        draw.text((96, 42), name, get_rank_colour(int(level / 10) + 1), font=font)
    draw.text((96, 62), "LEVEL " + str(level), (255, 255, 255), font=font_big)
    # Fill data
    width = draw.textsize(str(attk), font=font)[0]
    draw.text((241 - width, 122), str(attk), (255, 255, 255), font=font)

    width = draw.textsize(str(strg), font=font)[0]
    draw.text((241 - width, 150), str(strg), (255, 255, 255), font=font)

    width = draw.textsize(str(shooting), font=font)[0]
    draw.text((241 - width, 178), str(shooting), (255, 255, 255), font=font)

    width = draw.textsize("$" + util.to_money(player.money,True) , font=font)[0]
    draw.text((241 - width, 204), "$" + util.to_money(player.money,True) , (255, 255, 255), font=font)
    
    width= draw.textsize(str(player.quests_won), font=font)[0]
    draw.text((241 - width, 253), str(player.quests_won), (255, 255, 255), font=font)
    
    width = draw.textsize(str(player.wagers_won), font=font)[0]
    draw.text((241 - width, 267), str(player.wagers_won), (255, 255, 255), font=font)
    
    wep = get_text_limit_len(draw,util.clear_markdown_escapes(player.weapon.name),font,95);
    width = draw.textsize(wep, font=font)[0]
    draw.text((241 - width, 232), wep, (255, 255, 255), font=font)
    # here
    if(avatar != None):
        img.paste(avatar, (9, 12));
    c = 0;
    l = 0;
    first_even = True;
    for x in range(len(player.awards) - 1, -1, -1):
         if (c % 2 == 0):
             img.paste(award_icons[player.awards[x]], (18, 121 + 35 * l));
         else:
             img.paste(award_icons[player.awards[x]], (53, 121 + 35 * l));
             l = l + 1;
         c = c + 1;
         if(c == 8):
             break;
    if(len(player.awards) > 8):
        draw.text((18, 267), "+ " + str(len(player.awards) - 8) + " More", (48, 48, 48), font=font);
    if(len(player.awards) == 0):
        draw.text((38, 183), "None", (48, 48, 48), font=font);
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await util.get_client(message.server.id).send_file(message.channel, fp=output, filename="myinfo.png",content=":pen_fountain: **"+player.name+"'s** information.");
    output.close()


   # os.remove(fname + '.png')
    
async def displayQuestImage(quest, message):
    global images_served;
    images_served = images_served +1;
    await get_client(message.server.id).send_typing(message.channel);
    try:
        avatar = resize_avatar(quest, message.server, True, 72, 72);
    except:
        avatar = None;
    level = math.trunc(quest.level);
    attk = round(quest.attack, 2);
    strg = round(quest.strg, 2);
    shooting = round(quest.shooting, 2)
    img = Image.open("screens/stats_page_quest.png");
    draw = ImageDraw.Draw(img)
    name = get_text_limit_len(draw,util.clear_markdown_escapes(quest.name),font,114);
    g_quest = get_game_quest_from_id(quest.qID);
    draw.text((88, 38), name, getRankColour(int(level / 10) + 1), font=font)
    draw.text((134, 58), " " + str(level), (255, 255, 255), font=font_big)
    # Fill data
    width = draw.textsize(str(attk), font=font)[0]
    draw.text((203 - width, 123), str(attk), (255, 255, 255), font=font)

    width= draw.textsize(str(strg), font=font)[0]
    draw.text((203 - width, 151), str(strg), (255, 255, 255), font=font)

    width = draw.textsize(str(shooting), font=font)[0]
    draw.text((203 - width, 178), str(shooting), (255, 255, 255), font=font)

    wep = get_text_limit_len(draw,util.clear_markdown_escapes(get_weapon_from_id(quest.wID).name),font,136);
    width = draw.textsize(str(wep), font=font)[0]
    draw.text((203 - width, 207), str(wep), (255, 255, 255), font=font)
    
    if(g_quest != None):
        creator = get_text_limit_len(draw,g_quest.created_by,font,119);
        home = get_text_limit_len(draw,g_quest.made_on,font,146);
    else:
        creator = "Unknown";
        home = "Unknown";
    
    width = draw.textsize(creator, font=font)[0]
    draw.text((203 - width, 228), creator, (255, 255, 255), font=font)
    
    width = draw.textsize(home, font=font)[0]
    draw.text((203 - width, 242), home, (255, 255, 255), font=font)
    
    width = draw.textsize("$" + util.to_money(quest.money,True), font=font_med)[0]
    draw.text((203 - width, 266), "$" + util.to_money(quest.money,True), (48, 48, 48), font=font_med)

    if(avatar != None):
        img.paste(avatar, (9, 12));
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="questinfo.png",content=":pen_fountain: Here you go.");
    output.close()

    
async def player_progress(message):
    global money_created;
    global new_players_joined;
    global players_leveled;
    global players;
    print(players);
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
    
def weapon_hit(player,weapon):
    return random.random()<(limit_weapon_accy(player,weapon)/100);
    
def battle_turn(player,other_player,weapon):
    battle_line = None;
    player_hit_damage = player.attack;
    other_name = "the "+other_player.name if isinstance(other_player,activeQuest) else other_player.name;
    player_name = "The "+player.name if isinstance(player,activeQuest) else player.name;
    if(player.wID != no_weapon_id):
        if(weapon_hit(player,weapon)):
            if(not weapon.melee):
                player_hit_damage = weapon.attack * player.shooting;
            else:
                player_hit_damage = weapon.attack * player.attack;
            battle_line = player_name + " " + weapon.useText + " " + other_name + "!\n";
    damage_dealt = (player_hit_damage / (other_player.strg / 3 +1));
    if damage_dealt < 0.01:
        damage_dealt = 0.01;
    return [battle_line,damage_dealt];

async def battle(message, players, wager, quest):  # Quest like wager with diff win text
    global Players;
    global Weapons;
    global money_created;
    global money_transferred;
    global quests_attempted;
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10 and (wager == None and quest == False) ):
        await get_client(message.server.id).send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    if(wager == None and quest == False):
        player_one = findPlayer(players[0]);
        player_two = findPlayer(players[1]);
    elif (quest == True):
        player_one = findPlayer(players[0]);
        player_two = players[1];
        quests_attempted = quests_attempted + 1;
    else:
        player_one = findPlayer(message.author.id);
        player_two = findPlayer(wager.senderID);
        money_transferred = money_transferred + wager.wager;
    turns = 0;
    hp_player_one = 0;
    hp_player_two = 0;
    battle_lines = 0;
    if (player_one != None) and (player_two != None):
        hp_player_one = player_one.hp;
        hp_player_two = player_two.hp;
        weapon_player_one= get_weapon_from_id(player_one.wID);
        weapon_player_two = get_weapon_from_id(player_two.wID);
        bText = "```(" + player_one.name + " Vs " + player_two.name + ")\n";
        while (hp_player_one > 0) and (hp_player_two > 0):
            player_two_turn = battle_turn(player_two,player_one,weapon_player_two);
            hp_player_one += -player_two_turn[1];
            if player_two_turn[0] != None:
                bText += player_two_turn[0];
                battle_lines+=1;
            player_one_turn = battle_turn(player_one,player_two,weapon_player_one);
            hp_player_two += -player_one_turn[1];
            if player_one_turn[0] != None:
                bText += player_one_turn[0];
                battle_lines+=1;
            turns = turns + 1;
        txt = "turns";
        if(turns == 1):
            txt = "turn"
        if(battle_lines > 25):
            bText = "```(" + player_one.name + " Vs " + player_two.name + ")\nThe battle was too long to display!\n";
        if(hp_player_one > hp_player_two):
            if(wager == None):
                await battle_image(message, player_one, player_two, bText + player_one.name + " Wins in " + str(turns) + " " + txt + "!\n```\n");
            else:
                bText = bText +player_one.name + " Wins in " + str(turns) + " " + txt + "!\n";
                if not quest:
                    bText = bText + player_one.name + " receives $" + util.to_money(wager.wager,False)+ " in winnings from " + player_two.name + "!\n```\n";
                    player_one.money = player_one.money + (wager.wager * 2);
                    player_one.wagers_won = player_one.wagers_won + 1;
                    await give_award(message, player_one, 13, "Win a wager!");
                    await give_award(message, player_two, 14, "Lose a wager!");
                    savePlayer(player_one);
                    savePlayer(player_two);
                else:
                    player_one.money = player_one.money + wager;
                    money_created = money_created + wager;
                    bText = bText +player_one.name + " completed a quest and earned $" +  util.to_money(wager,False)+ "!\n```\n";
                    player_one.quests_won = player_one.quests_won + 1;
                    if(player_one.quests_completed_today == 0):
                        player_one.quest_day_start = time.time();
                    player_one.quests_completed_today  = player_one.quests_completed_today + 1;
                    await give_award(message, player_one, 1, "*Saved* the server.");
                    print(filter_func(player_one.name)+" ("+player_one.userid+") has received $"+util.to_money(wager,False)+" from a quest.");
                    savePlayer(player_one);
                await battle_image(message, player_one, player_two, bText);
        elif (hp_player_two > hp_player_one):
            if(wager == None):
                await battle_image(message, player_one, player_two, bText +player_two.name + " Wins in " + str(turns) + " " + txt + "!\n```\n");
            else:
                if not quest:
                    bText = bText +player_two.name + " Wins in " + str(turns) + " " + txt + "!\n";
                    bText = bText + player_two.name + " receives $" + util.to_money(wager.wager,False) + " in winnings from " + player_one.name + "!\n```\n";
                    player_two.money = player_two.money + (wager.wager * 2);
                    player_two.wagers_won = player_two.wagers_won + 1;
                    await give_award(message, player_two, 13, "Win a wager!");
                    await give_award(message, player_one, 14, "Lose a wager!");
                    savePlayer(player_one);
                    savePlayer(player_two);
                else:
                    bText = bText + "The " + player_two.name + " Wins in " + str(turns) + " " + txt + "!\n";
                    bText = bText + ""+player_one.name + " failed a quest and lost $" + util.to_money(int((wager) / 2),False)+ "!\n```\n";
                    player_one.money = player_one.money - int((wager) / 2);
                    await give_award(message, player_one, 3, "Red mist.");
                    savePlayer(player_one);
                await battle_image(message, player_one, player_two, bText);
        else:
            if(wager == None):
                await battle_image(message, player_one, player_two, bText + "Draw in " + str(turns) + " " + txt + "!\n```\n");
            else:
                if not quest:
                    player_two.money = player_two.money + wager.wager;
                    player_one.money = player_one.money + wager.wager;
                    await battle_image(message, player_one, player_two, bText + "Draw in " + str(turns) + " " + txt + " wagered money has been returned.\n```\n");
                    savePlayer(player_one);
                    savePlayer(player_two);
                else:
                    await battle_image(message, player_one, player_two, bText + "Quest ended in draw no money has been lost or won.\n```\n");
                    savePlayer(player_one);
                    savePlayer(player_two);

    else:
        if(player_one == None):
            await get_client(message.server.id).send_message(message.channel, "**"+util.get_server_name(message,players[0])+"** has not joined!");
        if(player_two == None):
            await get_client(message.server.id).send_message(message.channel, "**"+util.get_server_name(message,players[1])+"** has not joined!");
            
async def manage_quests(message):
    global quests_given;
    player = findPlayer(message.author.id);  
    if(time.time() - player.quest_day_start > 86400 and player.quest_day_start != 0):
        player.quests_completed_today = 0;
        player.quest_day_start = 0;
        print(filter_func(player.name)+" ("+player.userid+") daily completed quests reset");
    if(message.server.id not in ServersQuests and not os.path.isfile("saves/gamequests/"+message.server.id)):
        addQuests(message.server.id);
    if((time.time() - player.last_quest) >= 360):
        player.last_quest = time.time();
        if(message.server.id in ServersQuests and len(ServersQuests[message.server.id]) >= 1):
            n_q = ServersQuests[message.server.id][random.choice(list(ServersQuests[message.server.id].keys()))];
            if (random.random()<(n_q.spawnchance*(5/((player.quests_completed_today+5)*30))) and len(player.quests) <= 6):
                await addQuest(message, player, n_q);
                quests_given += 1;
                print(filter_func(player.name)+" ("+player.userid+") has received a quest ["+filter_func(n_q.qID)+"]");

async def add_quest(message, player, n_q):
    aQ = createQuest(n_q, player);
    savePlayer(player);
    if(not(message.server.id+"/"+message.channel.id in util.mutedchan)):
        await new_quest_image(message, aQ, player);
    else:
        print("Won't send new quest image - channel blocked.")

def create_quest(n_q, player):
    aQ = activeQuest();
    aQ.qID = n_q.qID;
    aQ.level = random.randint(int(player.level), int((player.level * 2)))
    hpMtp = random.randint(int(aQ.level / 2), int(aQ.level));
    shootMtp = random.randint(int(aQ.level / 2), int(aQ.level)) / random.uniform(1.5, 1.9);
    strgMtp = random.randint(int(aQ.level / 2), int(aQ.level)) / random.uniform(1.5, 1.9);
    attackMtp = random.randint(int(aQ.level / 2), int(aQ.level)) / random.uniform(1.5, 1.9);
    aQ.name = n_q.monsterName;
    aQ.hp = n_q.basehp * hpMtp;
    aQ.attack = n_q.baseattack * attackMtp;
    aQ.strg = n_q.basestrg * strgMtp;
    aQ.shooting = n_q.baseshooting * shootMtp;
    aQ.money = abs(int(n_q.bwinings) * int((hpMtp + shootMtp + strgMtp + attackMtp) / 4));
    if (aQ.money == 0):
        aQ.money = 1;
    aQ.wID =n_q.wID;
    player.quests.append(aQ);
    return aQ;

async def show_quests(message):
      #global GameQuests;
      player = findPlayer(message.author.id);
      command_key = util.get_server_cmd_key(message.server);
      QuestsT = "```\n" + player.name + "'s Quests!\n"
      if len(player.quests) > 0:
          for x in range(0, len(player.quests)):
              try:
                  real_quest = get_game_quest_from_id(player.quests[x].qID);
                  if(real_quest != None):
                      questT = real_quest.quest;
                  else:
                      questT = "Long forgotten quest:";
              except:
                  questT = "Long forgotten quest:";
              QuestsT = QuestsT + str(x + 1) + ". " + questT + " " + player.quests[x].name + " [Level " + str(player.quests[x].level) + "]!\n";
          QuestsT = QuestsT + "Use " + command_key + "declinequest [Quest Number] to remove a quest.\n";
          QuestsT = QuestsT + "Use " + command_key + "acceptquest [Quest Number] to accept!\n";
          QuestsT = QuestsT + "Use " + command_key + "questinfo [Quest Number] for more information!\n```";
      else:
          QuestsT = QuestsT + "You don't have any quests!```";
      await get_client(message.server.id).send_message(message.channel, QuestsT);
      


