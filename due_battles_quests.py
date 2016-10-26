import discord
import random
import math
import sys
import pickle;
import requests;
import util_due
import string
import os;
import jsonpickle;
import hashlib;
from urllib.request import urlopen
import io
import time
import re;
import shutil
from io import BytesIO;
import json;
from PIL import Image, ImageDraw, ImageFont
from io import StringIO

from argparse import Namespace
loaded = False;
Players = dict();
AwardsIcons = [];
AwardsNames = [];
ServersQuests = dict();
Weapons = dict();
Backgrounds = dict();
client = None;
no_weapon_id = "000000000000000000_none";
font = ImageFont.truetype("Due_Robo.ttf", 12);
font_big = ImageFont.truetype("Due_Robo.ttf", 18);
font_med = ImageFont.truetype("Due_Robo.ttf", 14);
font_small = ImageFont.truetype("Due_Robo.ttf", 11);
font_epic = ImageFont.truetype("benfont.ttf", 12);

class weapon_class:
        price = 0;
        server = "all";
        icon = "";
        attack = 0;
        chance = 0;
        message = "";
        useText = "";
        name = "";
        wID = "";
        melee = True;
        image_url = "";
class quest_class:
        qID = "";
        quest = "Battle a"
        monsterName = "";
        baseattack = 1;
        questServer = "all";
        basestrg = 1;
        baseshooting = 1;
        basehp = 10;
        baselevel = 0;
        bwinings = 5;
        blosings = 0;
        wID = no_weapon_id;
        wintext = "";
        losetext = "";
        spawnchance = 8;  # 50
        image_url = "";
        created_by = "";
        made_on = "";
class battleRequest:
        senderID = "";
        wager = 0;
class player:
    userid = "";
    benfont = False;
    level = 1;
    attack = 1;
    strg = 1;
    shooting = 1;
    hp = 10;
    background = "Default.png";
    wep_sum = '"0"01'#price/attack/sum;
    name = "";
    wID = no_weapon_id;
    money = 0;
    last_progress = 0;
    last_quest = 0;
    wagers_won = 0;
    quests_won = 0;
    potatos_given = 0;
    potatos = 0;
    last_image_request = 0;
    def __init__(self):
        self.quests = [];
        self.battlers = [];
        self.awards = [];
        self.owned_weps = [];
   
class activeQuest(player):
        qID = "";

def addQuests(server_id):
    global ServersQuests;
    slime = quest_class();
    slime.monsterName = "Slime";
    slime.qID = '"'+server_id+'""'+slime.monsterName.lower()+'"';
    slime.bwinnings = 2;
    slime.blosings = 1;
    slime.baseattack = 1.8;
    slime.basestrg = 2.1;
    slime.baseshooting = 1.4;
    slime.spawnchance = 25;
    slime.image_url = "http://i.imgur.com/iDzGVIg.jpg";
    slime.created_by = "DueUtil";
    slime.made_on = "Unknown";
    ServersQuests[server_id] = dict();
    ServersQuests[server_id]['slime'] = slime;
    saveQuest(slime);
    open("saves/gamequests/"+server_id, 'w').close()
def defineWeapons():
    global Weapons;
    Default = weapon_class();
    Default.price = 0;
    Default.icon = "";
    Default.name = "None"
    Default.attack = 0;
    Default.chance = 1;
    Default.melee = True;
    Default.image_url = "http://i.imgur.com/TlQsWZ3.png";
    Default.wID = "000000000000000000_none";
    Weapons[Default.wID]=Default;
    Gun = weapon_class();
    Gun.price = 200;
    Gun.icon = "🔫​";
    Gun.name = "Gun"
    Gun.useText = "shoots";
    Gun.attack = 30;
    Gun.chance = 10;
    Gun.melee = False;
    Gun.image_url = "http://i.imgur.com/XWPPWtA.png";
    Gun.wID = "000000000000000000_gun";
    Weapons[Gun.wID]=Gun;
    Frisby = weapon_class();
    Frisby.price = 20;
    Frisby.icon = "🌕";
    Frisby.attack = 7;
    Frisby.useText = "throws their frisby at";
    Frisby.name = "Frisby"
    Frisby.chance = 8;
    Frisby.melee = False;
    Frisby.image_url = "http://i.imgur.com/tv4Kloz.png";
    Frisby.wID = "000000000000000000_frisby";
    Weapons[Frisby.wID] = Frisby;
    LaserGun = weapon_class();
    LaserGun.price = 10000;
    LaserGun.icon = "🔦";
    LaserGun.attack = 1000;
    LaserGun.useText = "FIRES THEIR LAZAH AT";
    LaserGun.name = "Laser Gun"
    LaserGun.chance = 2;
    LaserGun.melee = False;
    LaserGun.image_url = "http://i.imgur.com/6GsD9qd.png";
    LaserGun.wID = "000000000000000000_laser gun";
    Weapons[LaserGun.wID] = LaserGun;
    Stick = weapon_class();
    Stick.price = 10;
    Stick.icon = "📏";
    Stick.attack = 1.1;
    Stick.chance = 2;
    Stick.melee = True;
    Stick.name = "Stick"
    Stick.useText = "wacks";
    Stick.image_url = "http://i.imgur.com/M0IaSSZ.png";
    Stick.wID = "000000000000000000_stick";
    Weapons[Stick.wID]=Stick; 
    
    print("Weapons loaded");
    
def get_weapon_for_server(server_id,weapon_name):
    if(weapon_name.lower() in ["stick","laser gun","gun","none","frisby"]):
        return Weapons["000000000000000000_"+weapon_name.lower()];
    else:
        weapID = server_id+"_"+weapon_name.lower();
        if(weapID in Weapons):
            return Weapons[weapID]
        else:
            return None;
            
def owns_weapon_name(player,wname):
    for weapon in player.owned_weps:
        if(get_weapon_from_id(weapon[0]).name.lower() == wname.lower()):
            return True;
    return False;
    
def remove_weapon_from_store(player,wname):
    #print(wname);
    for weapon in player.owned_weps:
        stored_weapon = get_weapon_from_id(weapon[0]);
        if(stored_weapon != None and stored_weapon.name.lower() == wname.lower()):
            wID = weapon[0];
            sum = weapon[1];
            del player.owned_weps[player.owned_weps.index(weapon)];
            return [wID,sum];
    return None;
        
        
def does_weapon_exist(server_id,weapon_name):   
    if(get_weapon_for_server(server_id,weapon_name) != None):
        return True;
    return False;

def get_weapon_from_id(id):
        if(id in Weapons):
            return Weapons[id]
        else:
            if(id != no_weapon_id):
                return Weapons[no_weapon_id];
        
def get_weapon_sum(id):
        if(id in Weapons):
            weapon  = Weapons[id];
            return '"'+str(weapon.price)+'"'+str(weapon.attack)+str(weapon.chance);
        else:
            return None;
def get_game_quest_from_id(id):
    id  = str(id);
    #print(id);
    args = util_due.get_strings(id);
    #print(args);
    #print(args[1] in ServersQuests[args[0]]);
    if(len(args) == 2 and args[0] in ServersQuests and args[1] in ServersQuests[args[0]]):
        #print(ServersQuests[args[0]][args[1]].quest);
        return ServersQuests[args[0]][args[1]];
    else:
        return None;
        
async def harambe_check(message,weapon,player):
    out=  ["penis","dick","cock","dong"];
    if any([x in weapon.name.lower() for x in out]):
        await give_award(message, player, 12, "For Harambe.");
    
async def battle_quest_on_message(message):
    #await exploit_check(message);
    await playerProgress(message);
    await manageQuests(message);
    found = True;
    command_key = util_due.get_server_cmd_key(message.server);
    if(message.content.lower().startswith(command_key + 'myquests')):
            await showQuests(message);
    elif(message.content.lower().startswith(command_key + 'acceptquest ')):
        try:
            messageArg = message.content.replace(command_key + "acceptquest ", "", 1);
            player = findPlayer(message.author.id);
            q = int(messageArg);
            if (q - 1) >= 0 and (q - 1) <= len(player.quests) - 1:
                if(player.money - int((player.quests[q - 1].money) / 2)) >= 0:
                    await Battle(message, [message.author.id, player.quests[q - 1]], player.quests[q - 1].money, True);
                    del player.quests[q - 1];
                    savePlayer(player);

                else:
                    await client.send_message(message.channel, ":bangbang:  **You can't afford the risk!**");
            else:
                await client.send_message(message.channel, ":bangbang: **Quest not found!**");
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif(message.content.lower().startswith(command_key + 'declinequest ')):
        try:
            messageArg = message.content.replace(command_key + "declinequest ", "", 1);
            player = findPlayer(message.author.id);
            q = int(messageArg);
            if (q - 1) >= 0 and (q - 1) <= len(player.quests) - 1:
                qT = player.quests[q - 1];
                del player.quests[q - 1];
                savePlayer(player);
                try:
                    main_quest = get_game_quest_from_id(qT.qID);
                    if(main_quest != None):
                        questT = main_quest.quest;
                    else:
                        questT = "do a long forgotten quest:";
                except:
                    questT = "do a long forgotten quest:";
                await client.send_message(message.channel, player.name + " declined to " + questT + " " + qT.name + " [Level " + str(qT.level) + "]!");
            else:
                await client.send_message(message.channel, ":bangbang:  **Quest not found!**");
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif(message.content.lower().startswith(command_key + 'questinfo ')):
        try:
            messageArg = message.content.replace(command_key + "questinfo ", "", 1);
            player = findPlayer(message.author.id);
            q = int(messageArg);
            if (q - 1) >= 0 and (q - 1) <= len(player.quests) - 1:
                await displayStatsImage(player.quests[q - 1], True, message);
            else:
                await client.send_message(message.channel, ":bangbang: **Quest not found!**");
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key + 'shop'):
        page = 0;
        args = message.content.lower().replace(command_key + 'shop',"");
        if(len(args) > 0):
            try:
                page = int(args) - 1;
                if(page < 0):
                    await client.send_message(message.channel, ":bangbang: **Page not found**");
                    return True;
            except:
                await client.send_message(message.channel, ":bangbang: **Page not found**");
                return True;
        await shop(message,page);
        return True;
    elif message.content.lower().startswith(command_key + 'benfont'):
        p =findPlayer(message.author.id);
        p.benfont = not p.benfont;
        savePlayer(p);
        if(p.benfont):
            await client.send_file(message.channel,'images/nod.gif');
            await give_award(message, p, 16, "ONE TRUE *type* FONT")
    elif message.content.lower().startswith(command_key + 'createquest') and (message.author.permissions_in(message.channel).manage_server or util_due.is_mod_or_admin(message.author.id)):
         messageArg = message.content.replace(command_key + "createquest ", "", 1);  # DO DO CREAT QUWEST
         Worked = False;
         Strs = util_due.get_strings(messageArg);
         if(len(Strs) == 9):
             try:
                 if(len(Strs[0]) <= 13):
                     if(len(Strs[1]) <= 20):
                         if(message.server.id in ServersQuests):
                             if(Strs[0].strip().lower() in ServersQuests[message.server.id]):
                                 await client.send_message(message.channel, ":bangbang: **A foe with that name already exists on this server!**");
                                 return True;
                         else:
                             addQuests(message.server.id);
                         nquest = quest_class();
                         nquest.monsterName = Strs[0].strip();
                         nquest.quest = Strs[1];
                         nquest.qID = '"'+message.server.id+'""'+nquest.monsterName.lower()+'"';
                         nquest.baseattack = abs(float(Strs[2]));
                         nquest.basestrg = abs(float(Strs[3]));
                         nquest.basehp = abs(int(Strs[4]));
                         nquest.baseshooting = abs(float(Strs[5]));
                         nquest.bwinings = (((nquest.baseattack + nquest.basestrg + nquest.baseshooting) / 20) / 0.0883);
                         nquest.bwinings = nquest.bwinings + (((nquest.bwinings * math.log10(nquest.basehp))) / 20) / 0.75;
                         nquest.bwinings = nquest.bwinings * (nquest.basehp / (abs(nquest.basehp - 0.01)));
                         if(len(Strs[6]) <= 18):
                            if(does_weapon_exist(message.server.id, Strs[6].lower())):
                                weap = get_weapon_for_server(message.server.id,  Strs[6].lower());
                                if(weap.server == message.server.id or weap.server == "all"):
                                    nquest.wID = weap.wID;
                         else:
                            attempt_id = Strs[6].lower();
                            attempt_id = attempt_id[:18]+"_"+attempt_id[19:];
                            nquest.wID = get_weapon_from_id(attempt_id).wID;
                         nquest.questServer = message.server.id;
                         nquest.spawnchance = abs(int(Strs[7]));
                         nquest.image_url = Strs[8];
                         nquest.created_by = findPlayer(message.author.id).name;
                         if(len(message.server.name) >13):
                             nquest.made_on = message.server.name[:10]+"...";
                         else:
                             nquest.made_on = message.server.name;
                         if(nquest.spawnchance == 0):
                             await client.send_message(message.channel, ":bangbang: **Spawn chance cannot be zero!**");
                             return True;
                         ServersQuests[message.server.id][nquest.monsterName.lower()] = nquest;
                             
                         #pickle.dump(GameQuests, open ("saves/quests.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL);
                         saveQuest(nquest);
                         await client.send_message(message.channel, nquest.quest + " **" + nquest.monsterName + "** quest now active!");
                     else:
                         await client.send_message(message.channel,":bangbang: **Quest text too long! Quest text cannot be longer than 20 characters!**");
                 else:
                     await client.send_message(message.channel,":bangbang: **Monster name too long! Monster names cannot be longer than 13 characters!**");

             except:
                 await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
         else:
             print(len(Strs))
             await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
             if(message.content.lower().count('"') % 2 == 1):
                await client.send_message(message.channel, ":information_source: It looks like you might have missed off a double quote!");
         return True;
    elif message.content.lower().startswith(command_key + 'serverquests') and (message.author.permissions_in(message.channel).manage_server or util_due.is_mod_or_admin(message.author.id)):
            text = "```\n" + message.server.name + " Quests\nSquare brackets indicate quest name.\n";
            number = 0;
            if(message.server.id in ServersQuests):
                for quest in ServersQuests[message.server.id].values():
                    number = number + 1;
                    text = text + str(number) + ". " + quest.quest + " [" + quest.monsterName + "] \n";   
            if(number == 0):
                text = text +"There isn't any quests on this server!\n";
            text = text + "```";
            await client.send_message(message.channel, text);
            return True;
    elif message.content.lower().startswith(command_key + 'removequest ') and (message.author.permissions_in(message.channel).manage_server or util_due.is_mod_or_admin(message.author.id)):
        messageArg = message.content.replace(command_key + "removequest ", "", 1);
        try:
            questName = messageArg.strip().lower().strip();
            if(message.server.id in ServersQuests):
                #print(questName);
                if(questName in ServersQuests[message.server.id]):
                    quest_to = ServersQuests[message.server.id][questName];
                else:
                    await client.send_message(message.channel, ":bangbang: **No monster with that name found on your server!**");
                    return True;
            else:
                 await client.send_message(message.channel, ":bangbang: **Looking at my records it appears you don't have any quests anyway...**");
                 True;
                 
            text = quest_to.quest + " **" + quest_to.monsterName + "** quest has been removed. You can rest easy now!"
            del ServersQuests[message.server.id][questName];
            os.remove("saves/gamequests/"+message.server.id+"_"+str(hashlib.md5(questName.encode('utf-8')).hexdigest())+".json");
            await client.send_message(message.channel, text);
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key + 'createweapon') and (message.author.permissions_in(message.channel).manage_server or util_due.is_mod_or_admin(message.author.id)):
         messageArg = message.content.replace(command_key + "createweapon ", "", 1);
         Worked = False;
         Strs = util_due.get_strings(messageArg);
         if(len(Strs) == 7):
             try:
                 if (does_weapon_exist(message.server.id, Strs[1].strip().lower())):
                    await client.send_message(message.channel, ":bangbang: **A weapon with that name already exists on this server!**");
                    return;
                 if(len(Strs[1]) <= 13):
                     wep = weapon_class();
                     wep.name = Strs[1].strip();
                     if(len(Strs[1]) == 1):
                         wep.icon = Strs[0];
                     else:
                         wep.icon = Strs[0][0]
                     wep.useText = Strs[4];
                     wep.price = abs(int(((1 / int(Strs[3])) * int(Strs[2])) / 0.04375));  # Fair price
                     wep.attack = abs(int(Strs[2]));
                     wep.chance = abs(int(Strs[3]));
                     wep.image_url = Strs[6];
                     wep.server = message.server.id;
                     wep.wID = message.server.id+"_"+wep.name.lower();
                     if Strs[5].lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
                         wep.melee = True;
                     else:
                         wep.melee = False;
                     Weapons[wep.wID] = wep;
                     saveWeapon(wep);
                     await client.send_message(message.channel, wep.name + " is now available in the shop for $" + util_due.to_money(wep.price) + "!");
                 else:
                     await client.send_message(message.channel,":bangbang: **Weapon name too long! Weapon names cannot be longer than 13 characters!**");                 
             except:
                 await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
         else:
             await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
             if(message.content.lower().count('"') % 2 == 1):
                await client.send_message(message.channel, ":information_source: It looks like you might have missed off a double quote!");
         return True;
    elif message.content.lower().startswith(command_key + "sendcash"):
        sender = findPlayer(message.author.id);
        mentions = message.raw_mentions;
        if(len(mentions) < 1):
            await client.send_message(message.channel, ":bangbang: **You must mention one player!**");
            return True;
        elif (len(mentions) > 1):
            await client.send_message(message.channel, ":bangbang: **You must mention only one player!**");
            return True;
        try:
            cmd = util_due.clearmentions(message.content);
            args = re.sub("\s\s+" , " ", cmd).split(sep =" ",maxsplit=2);
            amount = int(args[1]);
            other =findPlayer(mentions[0]);
            if(other == None):
                await client.send_message(message.channel, "**"+util_due.get_server_name(message,mentions[0])+"** has not joined!");
                return True;
            if(other.userid == sender.userid):
                await client.send_message(message.channel, ":bangbang: **There is no reason to send money to yourself!**");
                return True;
            if(amount < 0):
                await client.send_message(message.channel, ":bangbang: **You must send at least $1!**");
                return True;
            if(sender.money - amount < 0):
                if(sender.money > 0):
                    await client.send_message(message.channel, "You do not have **$"+ util_due.to_money(amount)+"**! The maximum you can transfer is **$"+ util_due.to_money(sender.money)+"**");
                else:
                     await client.send_message(message.channel, "You do not have any money to transfer!");
                return True
            sender.money = sender.money - amount;
            other.money = other.money + amount;
            savePlayer(sender);
            savePlayer(other);
            msg ="";
            if(amount >= 50):
                await give_award(message, sender, 17, "Sugar daddy!")
            if(len(args) == 3):
                msg = "**Attached note**: ```"+args[2].replace("```","")+"```\n";
            await client.send_message(message.channel, ":money_with_wings: **Transaction complete!**\n**"+sender.name+ "** sent $"+ util_due.to_money(amount)+" to **"+other.name+"**\n"+msg+"ᴾˡᵉᵃˢᵉ ᵏᵉᵉᵖ ᵗʰᶦˢ ʳᵉᶜᵉᶦᵖᵗ ᶠᵒʳ ʸᵒᵘʳ ʳᵉᶜᵒʳᵈˢ");
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key + "givepotato"):
        sender = findPlayer(message.author.id);
        if len(message.raw_mentions) == 1:
            if(sender.userid == message.raw_mentions[0]):
                await client.send_message(message.channel,":potato: **It's already yours enjoy it!**");
                return True;
            n = find_name(message.server,message.raw_mentions[0]);
            o = findPlayer(message.raw_mentions[0]);
            if(o == None):
                await client.send_message(message.channel, "**"+n+"** has not joined! No potatoes for them!");
                return True;
            o.potatos = o.potatos +1;
            sender.potatos_given = sender.potatos_given + 1;
            await give_award(message, sender, 18, "Bringer of potatoes!");
            if(sender.potatos_given == 100):
                await give_award(message, sender, 19, "Potato king!");
            await client.send_message(message.channel,"**"+n+"!** :potato: :heart: **"+sender.name+"**");
            savePlayer(o);
            savePlayer(sender);
        else:
            await client.send_message(message.channel, ":bangbang: **You must mention the potato receiver!**");
        return True;
    elif message.content.lower().startswith(command_key + 'removeweapon ')  and (message.author.permissions_in(message.channel).manage_server or util_due.is_mod_or_admin(message.author.id)):
        messageArg = message.content.replace(command_key + "removeweapon ", "", 1).strip();
        try:
            weapon = get_weapon_for_server(message.server.id, messageArg.lower());
            if(weapon != None):
                if(weapon.server == message.server.id):
                    #weapon.price = -1;
                    #saveWeapon(weapon)
                    if(os.path.isfile("saves/weapons/"+str(hashlib.md5(weapon.wID.encode('utf-8')).hexdigest())+".json")):
                        os.remove("saves/weapons/"+str(hashlib.md5(weapon.wID.encode('utf-8')).hexdigest())+".json");
                    del Weapons[weapon.wID];
                    await client.send_message(message.channel, weapon.name + " has been removed from DueUtil!");
                else:
                     await client.send_message(message.channel, ":bangbang: **You cannot remove that weapon!**");
            else:
                await client.send_message(message.channel, ":bangbang: **I don't no of any weapon with that name!**");
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key + 'buy '):
        messageArg = message.content.replace(command_key + "buy ", "", 1).strip();
        Found = False;
        try:
            weapon = get_weapon_for_server(message.server.id, messageArg.lower());
            if(weapon != None and weapon.name != "None"):
                if ((weapon.server == "all") or (weapon.server == message.server.id)) and weapon.price != -1:
                    Found = True;
                    player = findPlayer(message.author.id);
                    if(player == None):
                        return True;
                    if((player.money - weapon.price) >= 0):
                        if(len(player.owned_weps) < 6 or player.wID == no_weapon_id):
                            if(player.wID == no_weapon_id):
                                player.wID = weapon.wID;
                                await harambe_check(message,weapon,player);
                                await give_award(message, player, 4, "License to kill.");
                                player.wep_sum = get_weapon_sum(weapon.wID)
                                await client.send_message(message.channel, "**"+player.name+"** bought a " + weapon.name + " for $" +  util_due.to_money(weapon.price) + "!");
                            else:
                                if not owns_weapon_name(player,weapon.name.lower()):
                                    player.owned_weps.append([weapon.wID,get_weapon_sum(weapon.wID)]);
                                    await client.send_message(message.channel, "**"+player.name+"** bought a " + weapon.name + " for $" +  util_due.to_money(weapon.price) + "!");
                                    await client.send_message(message.channel, ":warning: You have not yet equiped this weapon yet.\nIf you want to equip this weapon do **"+command_key+"equipweapon "+weapon.name.lower()+"**.");
                                else:
                                    await client.send_message(message.channel, ":bangbang: **You already have a weapon with that name stored!**"); 
                            player.money = player.money - weapon.price;
                            savePlayer(player);             
                        else:
                            await client.send_message(message.channel, "**"+player.name+"** you have no free weapon slots! Sell one of your weapons first!");
                    else:
                        await client.send_message(message.channel, "**"+player.name+"** you can't afford this weapon.");
        except:
            Found = False;
        if(not Found):
            await client.send_message(message.channel, "Weapon not found!");
        return True;
    elif message.content.lower().startswith(command_key + 'sellweapon'):
        weapon_name = message.content.lower().replace(command_key+'sellweapon',"",1).strip();
        if(len(weapon_name)  == 0):
            await sell(message,message.author.id,False);
        else:
            await sell_weapon(message,message.author.id,False,weapon_name);
        return True;
    elif message.content.lower().startswith(command_key + 'resetme'):
        player = findPlayer(message.author.id);
        if(player == None):
            return True;
        player.level = 1;
        player.attack = 1;
        player.strg = 1;
        player.hp = 10;
        player.money = 0;
        player.background = "Default.png";
        player.wep_sum = get_weapon_sum(no_weapon_id)
        player.wID = no_weapon_id;
        player.shooting = 1;
        player.last_progress = 0;
        player.last_quest = 0;
        player.name = message.author.name;
        player.awards = [];
        player.quests = [];
        player.owned_weps = [];
        player.quests_won = 0;
        player.wagers_won = 0;
        savePlayer(player);
        await client.send_message(message.channel, "Your user has been reset.");
        if util_due.is_mod(player.userid):
            await give_award(message,player,22,"Become an mod!")
        if util_due.is_admin(player.userid):
            await give_award(message,player,21,"Become an admin!")
        return True;
    elif message.content.lower().startswith(command_key + 'battlename '):
        messageArg = message.content.replace(command_key + "battlename ", "", 1);
        if((len(messageArg) > 0) and (len(messageArg) <= 13)):
            player = findPlayer(message.author.id);
            if(player == None):
                return True;
            player.name = messageArg;
            savePlayer(player);
            await client.send_message(message.channel, "Your battle name has been set to '" + messageArg + "'!");
        else:
            await client.send_message(message.channel, ":bangbang: **Battle names must be between 0 and 13 characters in length.**");
        return True;
    elif message.content.lower().startswith(command_key + 'myinfo'):
        await printStats(message, message.author.id);
        return True;
    elif message.content.lower().startswith(command_key + 'info'):
        users = message.raw_mentions;
        if(len(users) == 1):
            await printStats(message, users[0]);
        return True;
    elif message.content.lower().startswith(command_key + 'battle '):
        users = util_due.userMentions(message);
        if (len(users) == 2):
            if(users[0] != users[1]):
                await Battle(message, users, None, False);
            else:
                await client.send_message(message.channel, ":bangbang: **You can't battle yourself!**");
        else:
            await client.send_message(message.channel, ":bangbang: **You must mention two players!**");
        return True;
    elif message.content.lower().startswith(command_key + 'battleme '):
        p = util_due.userMentions(message);
        if(len(p) == 1):
            if(message.author.id == p[0]):
                await client.send_message(message.channel, ":bangbang: **You can't battle yourself!**");
                return True;
            await Battle(message, [message.author.id,p[0]], None, False)
        elif len(p) > 1:
            await client.send_message(message.channel, ":bangbang: **You must only mention one player!**");
            return True;
        else:
            await client.send_message(message.channel, ":bangbang: **You must mention who you would like to battle!**");
            return True;
    elif message.content.lower().startswith(command_key + 'qcooldown'):
        player = findPlayer(message.author.id);
        t = 360 - (time.time() - player.last_quest);
        mi, se = divmod(t, 60)
        m = str(int(mi));
        s = str(int(se));
        if(int(mi) == 0 and int(se) == 0):
            await client.send_message(message.channel, ":information_source: You next have the chance of getting a now! Good luck.");
        if( int(se) < 10):
            s = "0"+str(s);
        if( int(mi) < 10):
            m = "0"+str(m);
        if(int(mi) > 0):
            await client.send_message(message.channel, ":information_source: You next have the chance of getting a quest in **"+str(m)+"m "+str(s)+"s**");
        else:
            await client.send_message(message.channel, ":information_source: You next have the chance of getting a quest in **"+str(s)+"s**");
    elif message.content.lower().startswith(command_key + 'wagerbattle'):  # NEW WIP WAGERS
        users = util_due.userMentions(message);
        if(len(users) == 1):
            messageArg = message.content.replace(command_key + "wagerbattle ", "", 1);
            messageArg = util_due.clearmentions(messageArg);
            try:
                Money = int(messageArg);
                if (len(users) == 1):
                    if(users[0] != message.author.id):
                        player = findPlayer(users[0]);
                        if(player != None):
                            if(Money > 0):
                                sender = findPlayer(message.author.id);
                                if(sender.money - Money >= 0):
                                    wagerS = battleRequest();
                                    wagerS.senderID = message.author.id;
                                    wagerS.wager = Money;
                                    sender.money = sender.money - Money;
                                    player.battlers.append(wagerS);
                                    savePlayer(sender);
                                    savePlayer(player);
                                    await client.send_message(message.channel, "**"+sender.name+"** wagers **"+player.name+"** $" + util_due.to_money(Money) + " that they will win in a battle!");
                                else:
                                    await client.send_message(message.channel, ":bangbang: **You can't afford this wager!**");
                            else:
                                await client.send_message(message.channel, ":bangbang: **You must wager at least $1!**");
                        else:
                            await client.send_message(message.channel, "**"+util_due.get_server_name(message,users[0])+"** is not playing!");
                    else:
                        await client.send_message(message.channel, ":bangbang: **You can't wager against yourself!**");
                else:
                    await client.send_message(message.channel, ":bangbang: **You must mention one player!**");
            except:
                await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        else:
             await client.send_message(message.channel, ":bangbang: **You must mention one player!**");
        return True;
    elif message.content.lower().startswith(command_key + 'viewwagers'):
        player = findPlayer(message.author.id);
        WagerT = "```\n" + player.name + "'s received wagers\n";
        if(len(player.battlers) > 0):
            for x in range(0, len(player.battlers)):
                WagerT = WagerT + str(x + 1) + ". $" +  util_due.to_money(player.battlers[x].wager) + " from " + findPlayer(player.battlers[x].senderID).name + ".\n"
        else:
            WagerT = WagerT + "You have no requests!\n";
        WagerT = WagerT + "Do " + command_key + "acceptwager [Wager Num] to accept a wager.\n";
        WagerT = WagerT + "Do " + command_key + "declinewager [Wager Num] to decline a wager.\n```";
        await client.send_message(message.channel, WagerT);
        return True;
        # Loop and show received wagers
    elif message.content.lower().startswith(command_key + 'acceptwager '):
        player = findPlayer(message.author.id);
        messageArg = message.content.replace(command_key + "acceptwager ", "", 1);
        try:
            w = int(messageArg);
            w = w - 1;
            if(w >= 0) and (w <= (len(player.battlers) - 1)):  # check id they can afford it
                if(player.money - player.battlers[w].wager) >= 0:
                    player.money = player.money - player.battlers[w].wager;
                    await Battle(message, None, player.battlers[w], False);
                    del player.battlers[w];
                    savePlayer(player);
                else:
                    await client.send_message(message.channel, ":bangbang: **You can't afford to lose this wager!**");
            else:
                await client.send_message(message.channel, ":bangbang: **Request not found**"); 
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key + 'declinewager '):
        player = findPlayer(message.author.id);
        messageArg = message.content.replace(command_key + "declinewager ", "", 1);
        try:
        #if 1==1:
            w = int(messageArg);
            w = w - 1;
            if(w >= 0) and (w <= (len(player.battlers) - 1)):
                sender = findPlayer(player.battlers[w].senderID);
                sender.money = sender.money + player.battlers[w].wager;
                del player.battlers[w];
                savePlayer(player);
                savePlayer(sender);
                await client.send_message(message.channel, "**"+player.name+"** declined **"+sender.name+"**'s wager.");
            else:
                await client.send_message(message.channel, ":bangbang: **Request not found!**"); 
        except:
            await client.send_message(message.channel, ":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key + 'setbg '):
        player = findPlayer(message.author.id);
        background_name = message.content.lower().replace(command_key + 'setbg ', "").strip().title();
        if(background_name in Backgrounds.keys()):
            player.background = Backgrounds[background_name];
            await client.send_message(message.channel, "Your personal background has been set to **" + background_name + "**!"); 
            savePlayer(player)
        else:
            await client.send_message(message.channel, ":bangbang: **That background does not exist!**\nDo **" + command_key + "listbgs** for a full list of the current backgrounds!"); 
    elif message.content.lower() == command_key + 'listbgs' or  message.content.lower().startswith(command_key + 'listbgs '):
        bglist = list(Backgrounds.keys());
        page = 0;
        end_cmd = message.content.lower().replace(command_key + 'listbgs', "");
        if(len(end_cmd.replace(" ", "")) > 0):
            try:
                page = int(end_cmd) - 1;
            except:
                await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
                return;
        if(page == 0):
            bgs = "```Available Backgrounds\n";
        else:
            bgs = "```Available Backgrounds: Page " + str(page + 1) + "\n";
        if(page * 10 > len(bglist) - 1):
            await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
            return;
        for x in range(page * 10, page * 10 + 10):
            if(x < len(bglist)):
                bgs = bgs + str(x + 1) + ". " + bglist[x] + "\n";
            else:
                break;
        if(x < len(bglist) - 1):
            bgs = bgs + "Do " + command_key + "listbgs " + str(page + 2) + " to see more.";
        bgs = bgs + "```";
        await client.send_message(message.channel, bgs);    
    elif message.content.lower() == command_key + "reloadbgs" and ((message.author.id == "132315148487622656") or (util_due.is_mod_or_admin(message.author.id))):
        loadBackgrounds();
        await client.send_message(message.channel, "Custom backgrounds reloaded.");   
        return True; 
    elif message.content.lower().startswith(command_key + 'myrank'):
        await display_rank(message, None);
    elif message.content.lower().startswith(command_key + 'rank'):
        if(len(message.raw_mentions) == 1):
            gplayer = findPlayer(util_due.userMentions(message)[0]);
            if(gplayer == None):
                await client.send_message(message.channel, "**"+util_due.get_server_name(message,util_due.userMentions(message)[0])+"** has not joined!");
            else:
                await display_rank(message, gplayer);
        else:
            if(len(message.raw_mentions) < 1):
                await client.send_message(message.channel, ":bangbang: **You must mention one player!**");    
            else:
                await client.send_message(message.channel, ":bangbang: **You must mention only one player!**");    
        return True;
    elif message.content.lower().startswith(command_key + 'myawards') or message.content.lower().startswith(command_key + 'awards'):
        if  len(message.raw_mentions) == 1 and message.content.lower().startswith(command_key + 'awards'):
            player = findPlayer(message.raw_mentions[0]);
            if player == None:
                await client.send_message(message.channel, "**"+util_due.get_server_name(message,message.raw_mentions[0])+"** has not joined!");
                return True;
        elif message.content.lower().startswith(command_key + 'awards') and len(message.raw_mentions) == 0:
            await client.send_message(message.channel, ":bangbang: **You must mention one player!**");
            return True;
        elif message.content.lower().startswith(command_key + 'awards') and len(message.raw_mentions) > 1: 
            await client.send_message(message.channel, ":bangbang: **You must mention only one player!**");
            return True; 
        else:
            player = findPlayer(message.author.id);
        if(" " in message.content.lower() and hasNumbers(util_due.clearmentions(message.content))):
            try:
                p = int(util_due.clearmentions(message.content.lower().replace(command_key + 'myawards',"").replace(command_key + 'awards',"")));
                if((p-1)*5 < len(player.awards) and p > 0):
                    await awards_screen(message, player, p-1);
                else:
                    await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
                    return True;
            except:
                await client.send_message(message.channel, ":bangbang: **Page not found!**"); 
                return True;
        else:
            await awards_screen(message,player, 0);
        return True;
    elif message.content.lower().startswith(command_key + 'myweapons'):
        await show_weapons(message,findPlayer(message.author.id),False);
        return True;
    elif message.content.lower().startswith(command_key + 'weapons '):
        users = message.raw_mentions;
        if(len(users) == 1):
            player = findPlayer(users[0]);
            if player == None:
                await client.send_message(message.channel, "**"+util_due.get_server_name(message,users[0])+"** has not joined!");
                return True;
            await show_weapons(message,player,True);
        return True;
    elif message.content.lower().startswith(command_key + 'equipweapon'):
        await equip_weapon(message,findPlayer(message.author.id),message.content.replace(command_key + "equipweapon ", "", 1));
        return True;
    elif message.content.lower().startswith(command_key + 'unequipweapon'):
        await unequip_weapon(message,findPlayer(message.author.id));
        return True;
    elif message.content.lower() == (command_key + 'checkusers') and util_due.is_mod_or_admin(message.author.id):
        await exploit_check(message);
        return True;
    elif message.content.lower() == (command_key + 'clearsus') and util_due.is_mod_or_admin(message.author.id):
        await clear_suspicious(message);
        return True;
    elif (message.content.lower().startswith(command_key + 'takeweapons ') or message.content.lower().startswith(command_key + 'clearcash ') or message.content.lower().startswith(command_key + 'clearstuff ')) and util_due.is_mod_or_admin(message.author.id):
        users = message.raw_mentions;
        if(len(users) > 1):
            await client.send_message(message.channel, ":bangbang: **You must mention only one player!**");
            return True;
        elif (len(users) == 0):
            await client.send_message(message.channel, ":bangbang: **You must mention one player!**");
            return True;
        player = findPlayer(users[0]);
        if player == None:
            await client.send_message(message.channel, "**"+util_due.get_server_name(message,users[0])+"** has not joined!");
            return True;
        if message.content.lower().startswith(command_key + 'takeweapons '):
            await take_weapon(message,player);
        elif message.content.lower().startswith(command_key + 'clearcash '):
            await wipe_cash(message,player);
        elif message.content.lower().startswith(command_key + 'clearstuff '):
            await take_weapon(message,player);
            await wipe_cash(message,player);
        return True;
    else:
        found = False;
    return found;

def hasNumbers(text):
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
        await client.send_message(message.channel, "You're **rank " + str(players_of_higher_level + 1) + "** out of " + str(players) + " players on **" + message.server.name + "**");
    else:
        await client.send_message(message.channel, rplayer.name + " is **rank " + str(players_of_higher_level + 1) + "** out of " + str(players) + " players on **" + message.server.name + "**");

async def unequip_weapon(message,cplayer):
    active_wep = get_weapon_from_id(cplayer.wID);
    if(active_wep.wID != no_weapon_id):
        if(len(cplayer.owned_weps) < 6):
            if not owns_weapon_name(cplayer,active_wep.name.lower()):
                cplayer.owned_weps.append([active_wep.wID,cplayer.wep_sum]);
                cplayer.wID = no_weapon_id;
                cplayer.wep_sum = get_weapon_sum(no_weapon_id);
                await client.send_message(message.channel, ":white_check_mark: **"+active_wep.name+"** unequiped!");
            else:
                await client.send_message(message.channel, ":bangbang: **You already have a weapon with that name stored!**"); 
        else:
            await client.send_message(message.channel, ":bangbang: **No room in your weapon storage!**");
    else:
        await client.send_message(message.channel, "You don't have anything equiped anyway!");
        
async def equip_weapon(message,player,wname):
    storedWeap = remove_weapon_from_store(player,wname);
    if(storedWeap != None):
        if(player.wID != no_weapon_id):
            player.owned_weps.append([player.wID,player.wep_sum]);
        player.wID = storedWeap[0];
        player.wep_sum = storedWeap[1];
        newWeap = get_weapon_from_id(player.wID);
        if(newWeap.wID != no_weapon_id):
            await harambe_check(message,newWeap,player);
            await client.send_message(message.channel, ":white_check_mark: **"+newWeap.name+"** equiped!");
        else:
            await client.send_message(message.channel, ":white_check_mark: equiped!");
        savePlayer(player);
    else:
        await client.send_message(message.channel, ":bangbang: **You do not have that weapon stored!**");
        
async def validate_weapon_store(message,player):
    weapon_sums = [];
    for ws in player.owned_weps:
        if(ws[1] != get_weapon_sum(ws[0])):
            weapon_sums.append(ws[1]);
            del player.owned_weps[player.owned_weps.index(ws)];
    #print(weapon_sums);
    if len(weapon_sums) > 0:
        await mass_recall(message,player,weapon_sums);        

async def sell(message, uID, recall):
    await sell_weapon(message,uID,recall,None); 

async def mass_recall(message, player, weapon_sums):
    refund = 0;
    for sum in weapon_sums:
        refund = refund + int(util_due.get_strings(sum)[0]);
    player.money = player.money + refund;
    await client.send_message(message.channel, "**"+player.name+"** a weapon or weapons you have stored have been recalled by the manufacturer. You get a full $" + util_due.to_money(refund) + " refund.");
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
                await client.send_message(message.channel, ":bangbang: **Weapon not found!**");
                return;
        if(weapon_data != None):
            weapon_id = weapon_data[0];
    if (weapon_id != no_weapon_id):
        weapon = get_weapon_from_id(weapon_id);
        price = int(((1 / weapon.chance) * weapon.attack) / 0.04375);
        sellPrice = int(price - (price / 4));
        if(not recall):
            await client.send_message(message.channel, "**"+player.name+"** sold their trusty " +weapon.name + " for $" +util_due.to_money(sellPrice)+ "!");
        else:
            if(weapon_name == None):
                sellPrice = int(util_due.get_strings(player.wep_sum)[0]);
            else:
                sellPrice = int(util_due.get_strings(weapon_data[1])[0]);
            #print(util_due.get_strings(player.wep_sum));
            await client.send_message(message.channel, "**"+player.name+"** your weapon has been recalled by the manufacturer. You get a full $" + util_due.to_money(sellPrice) + " refund.");
        if(weapon_name == None):
            player.wID = no_weapon_id;
            player.wep_sum = get_weapon_sum(no_weapon_id)
        player.money = player.money + sellPrice;
        savePlayer(player);
    else:
        await client.send_message(message.channel, "**"+player.name+"** nothing does not fetch a good price...");

        
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
            accy = round((1/weap.chance)*100,2);
            output = output+str(num)+". "+weap.icon + " - " + weap.name + " | DMG: " + str(weap.attack) + " | ACCY: " + (str(accy)+"-").replace(".0-","").replace("-","") + "% | Type: " + Type + " |\n";
            num=num+1;
    if(len(player.owned_weps) == 0):
        if(not not_theirs):
            output = output + "You don't have any weapons stored!```";
        else:
            output = output + player.name+" does not have any weapons stored!```";
    else:
        if(not not_theirs):
            cmd = util_due.get_server_cmd_key(message.server);
            output = output+"Use "+cmd+"equipweapon [Weapon Name] to equip a stored weapon!\nUse "+cmd+"unequipweapon to store your equiped weapon.```";
        else:
            output = output + "```";
    await client.send_message(message.channel, output);
     
def load(discord_client):
    global Weapons;
    global Players
    global client;
    global loaded;
    client = discord_client;
    loadPlayers();
    print(str(len(Players)) + " player(s) loaded.")
    defineWeapons();
    loadWeapons();
    loadQuests();
    print(str(len(ServersQuests)) + " server(s) with quests loaded.")
    print(str(len(Weapons)) + " weapon(s) loaded.")
    #quest loading
    loadBackgrounds();
    load_awards();
    loaded = True;
    
def loadBackgrounds():
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
        if  message.channel.is_private or not(message.server.id+"/"+message.channel.id in util_due.mutedchan):
            await client.send_message(message.channel, "**"+player.name+"** :trophy: **Award!** " + text);

async def give_award_id(message, userid, id, text):
    player = findPlayer(userid);
    if player == None:
        return;
    if(id not in player.awards):
        player.awards.append(id);
        savePlayer(player)
        if  message.channel.is_private or not(message.server.id+"/"+message.channel.id in util_due.mutedchan):
            await client.send_message(message.channel, "**"+player.name+"** :trophy: **Award!** " + text);
             
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
    
def load_award(icon_path,name):
    global AwardsIcons;
    global AwardsNames;
    AwardsIcons.append(Image.open(icon_path));
    AwardsNames.append(name);
    
async def shop(message,page):
    global Weapons;
    shop_title = "\n**Welcome to DueUtil's weapon shop!**\n"
    if(page > 0):
        shop_title = "\n**DueUtil's weapon shop: Page "+str(page+1)+"**\n"
    count = 0;
    weapon_listings = "";
    body = "";
    shop_footer = "Type **" + util_due.get_server_cmd_key(message.server) + "buy [Weapon Name]** to purchase a weapon.\n";
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
                accy = round((1/weapon.chance)*100,2);
                weapon_listings = weapon_listings + str((count)) + ". " + weapon.icon + " - " + weapon.name + " | DMG: " + str(weapon.attack) + " | ACCY: " + (str(accy)+"-").replace(".0-","").replace("-","") + "% | Type: " + Type + " | $" +  util_due.to_money(weapon.price)+ " |\n";	
    page_data = util_due.get_page(weapon_listings,page);
    if(page_data == None):
        await client.send_message(message.channel, ":bangbang: **Page not found!**");
        return;
    else:
        body=page_data[0];
        if(page_data[1]):
            shop_footer = shop_footer +"**But wait there's more** type **"+util_due.get_server_cmd_key(message.server)+"shop "+str(page+2)+"** to have a look!"
        else:
            shop_footer = shop_footer +"Want more? Ask a server manager to add stock!"
    await client.send_message(message.channel, shop_title);
    await client.send_message(message.channel, body);
    await client.send_message(message.channel,shop_footer);


async def printStats(message, uID):
    global Players;
    level = 0;
    attk = 0;
    strg = 0;
    player = findPlayer(uID);
    if(player != None):
        await displayStatsImage(player, False, message);
    else:
        await client.send_message(message.channel, "**"+util_due.get_server_name(message,uID)+"** has not joined!");
            
async def displayStats(player, q, message):
        level = math.trunc(player.level);
        attk = round(player.attack, 2);
        strg = round(player.strg, 2);
        shooting = round(player.shooting, 2)
        c = "Cash"
        title = "```\n" + player.name + "'s Info";
        w = "Current Weapon"
        if(q):
            c = "Reward"
            w = "Weapon"
            title = "```\n" + player.name + " Quest Info"
        await client.send_message(message.channel, title + "\nLevel: " + str(level) + " \nAttack: " + str(attk) + "\nStrength: " + str(strg) + "\nShooting: " + str(shooting) + "\n" + c + ": $" +  util_due.to_money(player.money)+ "\n" + w + ": " + Weapons[player.wID].icon + " - " + Weapons[player.wID].name + "```\n");

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

async def level_up_image(message, player, cash):
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
    draw.text((127, 40), "$" + util_due.to_money(cash), (255, 255, 255), font=font_big)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await client.send_file(message.channel, fp=output, filename="level_up.png",content=":point_up_2: **"+player.name+"** Level Up!");
    output.close()


async def new_quest_image(message, quest, player):
    try:
        avatar = resize_avatar(quest, message.server, True, 54, 54);
    except:
        avatar = None;
    img = Image.open("screens/new_quest.png"); 
    if(avatar != None):
        img.paste(avatar, (10, 10));
    draw = ImageDraw.Draw(img)
    g_quest = get_game_quest_from_id(quest.qID);
    draw.text((72, 20), filter_func(g_quest.quest), (255, 255, 255), font=font_med)
    draw.text((71, 39), filter_func(g_quest.monsterName) + " LEVEL " + str(math.trunc(quest.level)), (255, 255, 255), font=font_big)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await client.send_file(message.channel, fp=output, filename="new_quest.png",content=":crossed_swords: **"+player.name+"** New Quest!");
    output.close()

async def awards_screen(message, player,page):
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10):
        await client.send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    sender.last_image_request = time.time();
    player.last_image_request = time.time();
    await client.send_typing(message.channel);
    img = Image.open("screens/awards_screen.png"); 
    a_s = Image.open("screens/award_slot.png"); 
    draw = ImageDraw.Draw(img)
    name = filter_func(player.name);
    t = name+"'s Awards";
    if(page > 0):
        t = t + ": Page "+str(page+1);
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
                 if(message.content.lower().startswith(util_due.get_server_cmd_key(message.server)+"awards")):
                     a = "awards @User";
                 msg = "+ "+str(len(player.awards)-(5*(page+1)))+" More. Do "+filter_func(util_due.get_server_cmd_key(message.server))+a+" "+str(page+2)+" for the next page.";
             break;
    if (x == 0):
        msg = "That's all folks!"
    if (len(player.awards) == 0):
        msg = name+" doesn't have any awards!";
    width, height = draw.textsize(msg, font=font_small)
    draw.text(((256-width)/2, 42 + 44 * c),msg,  (255, 255, 255), font=font_small)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await client.send_file(message.channel, fp=output, filename="awards_list.png",content=":trophy: **"+player.name+"'s** Awards!");
    output.close()


async def battle_image(message, pone, ptwo, btext):
    sender = findPlayer(message.author.id);
    sender.last_image_request = time.time();
    await client.send_typing(message.channel);
    try:
        if(not isinstance(pone, activeQuest)):
            avatar_one = resize_avatar(pone, message.server, False, 54, 54);
        else:
            avatar_one = resize_avatar(pone, message.server, True, 54, 54);
    except:
        avatar_one = None;
    print(not isinstance(ptwo, activeQuest));
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
    if(wep_image_one != None):
        try:
            img.paste(wep_image_one, (6, height - 6 - 30), wep_image_one);
        except:
            img.paste(wep_image_one, (6, height - 6 - 30));
    else:
        wep_image_one = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30);

    wep_image_two = resize_image_url(weapon_two.image_url, 30, 30);
    if(wep_image_two != None):
        try:
            img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30), wep_image_two);
        except:
            img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30));
    else:
        wep_image_two = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30);
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30), wep_image_two);
        
    draw = ImageDraw.Draw(img)
    draw.text((7, 64), "LEVEL " + str(math.trunc(pone.level)), (255, 255, 255), font=font_small)
    draw.text((190, 64), "LEVEL " + str(math.trunc(ptwo.level)), (255, 255, 255), font=font_small)
    width, height = draw.textsize(filter_func(weapon_one.name), font=font)
    draw.text((124 - width, 88), filter_func(weapon_one.name), (255, 255, 255), font=font)
    draw.text((132, 103), filter_func(weapon_two.name), (255, 255, 255), font=font)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await client.send_file(message.channel, fp=output, filename="battle.png");
    await client.send_message(message.channel,btext);
    output.close()

        
def getRankColour(rank):
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
            image_file = io.BytesIO(response.content);
            img = Image.open(image_file);
            img.convert('RGB').save(fname, optimize=True, quality=20);
            return img;
            del response
        except:
            if(os.path.isfile(fname)):
                os.remove(fname);
            return None;
        
def jsonTest(playerT):
    datum = json.dumps(playerT, default=lambda o: o.__dict__);
    print(datum);
    rebuild = json.loads(datum, object_hook=lambda d: Namespace(**d))
    print(rebuild.quests[0].name);
 
def update_player_def(p):
    if not hasattr(p,'owned_weps'):
        setattr(p,'owned_weps',[]);
    return p;
    
def loadPlayers():
    global Players;
    for file in os.listdir("saves/players/"):
        if file.endswith(".json"):
            with open("saves/players/" + str(file)) as data_file:    
                data = json.load(data_file);
                p = jsonpickle.decode(data);
                p = update_player_def(p);
                Players[p.userid] = p;
                
async def exploit_check(message):
    global Players;
    out = "```These players seem suspicious...\n"
    count = 0;
    for player in Players.values():
        weapon =  get_weapon_from_id(player.wID);
        hasOPweapStore = "No";
        for weap in player.owned_weps:
            if(get_weapon_from_id(weap[0]).price >= 50000):
                hasOPweapStore = "Yes";
                break;
        if(player.money >= 50000 or weapon.price >= 50000 or hasOPweapStore == "Yes"):
            count = count +1;
            out = out + str(count)+". "+player.name + " ("+player.userid+") | Cash $"+util_due.to_money(player.money)+" | Weapon Value $"+util_due.to_money(weapon.price)+" | Suspicious Stored Weapons - "+hasOPweapStore+" \n"
    if(count > 0):
        out = out + "```";
    else:
        out =  'All looks good.';
    await client.send_message(message.channel,out);
        
async def take_weapon(message,player):
    player.owned_weps = [];
    player.wID = no_weapon_id;
    player.wep_sum = get_weapon_sum(no_weapon_id);
    await client.send_message(message.channel,"All weapons taken from **"+player.name+"**!");
    savePlayer(player);
    
async def wipe_cash(message,player):
    player.money = 0;
    await client.send_message(message.channel,"Reset **"+player.name+"**'s cash!");
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
        if player.money >= 50000 or weapon.price >= 50000 or hasOPweapStore:
            if(not util_due.is_mod_or_admin(player.userid)):
                count = count + 1;
                player.money = 0;
                player.wID = no_weapon_id;
                player.wep_sum = get_weapon_sum(no_weapon_id);
                player.owned_weps = [];
                savePlayer(player);
            else:
                admins = admins +1;
    if(count > 0):
        await client.send_message(message.channel,":white_check_mark: **Suspicious money and weapons confiscated from "+str(count)+" user(s)!**");
        if(admins > 0):
            await client.send_message(message.channel,str(admins)+" admin(s) or mod(s) omitted.");
    else:
        await client.send_message(message.channel,"No suspicious users!");
            
def  loadWeapons():
    global Weaponse;
    for file in os.listdir("saves/weapons/"):
        if file.endswith(".json"):
            with open("saves/weapons/" + str(file)) as data_file:    
                data = json.load(data_file);
                w = jsonpickle.decode(data);
                Weapons[w.wID] = w;   

def savePlayer(player):
    # data = json.dumps(player, default=lambda o: o.__dict__);
    data = jsonpickle.encode(player);
    with open("saves/players/" + player.userid + ".json", 'w') as outfile:
        json.dump(data, outfile);
        
def saveQuest(quest):
    # data = json.dumps(player, default=lambda o: o.__dict__);
    data = jsonpickle.encode(quest);
    args = util_due.get_strings(quest.qID);
    with open("saves/gamequests/" + args[0] + "_"+str(hashlib.md5(quest.monsterName.lower().encode('utf-8')).hexdigest())+".json", 'w') as outfile:
        json.dump(data, outfile);
        
def loadQuests():
    global ServersQuests;
    for file in os.listdir("saves/gamequests/"):
        if file.endswith(".json"):
            with open("saves/gamequests/" + str(file)) as data_file:    
                data = json.load(data_file);
                q = jsonpickle.decode(data);
                args = util_due.get_strings(q.qID);
                if(len(args) == 2):
                    if(args[0] in ServersQuests):
                        ServersQuests[args[0]][args[1]] = q;
                    else:
                        ServersQuests[args[0]]=dict();
                        ServersQuests[args[0]][args[1]] = q;
                else:
                    print("Failed to load quest!")  
        
def find_name(server,uID):
    p = findPlayer(uID);
    if(p != None):
        return p.name;
    else:
        return util_due.get_server_name_S(server,uID);
    
def saveWeapon(weapon):
    data = jsonpickle.encode(weapon);
    with open("saves/weapons/" + str(hashlib.md5(weapon.wID.encode('utf-8')).hexdigest()) + ".json", 'w') as outfile:
        json.dump(data, outfile);
        
async def displayStatsImage(player, q, message):
    # jsonTest(player);
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10):
        await client.send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    sender.last_image_request = time.time();
    # savePlayer(player);
    await client.send_typing(message.channel);
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
    shooting = round(player.shooting, 2)
    name = filter_func(player.name);

    img = Image.open("backgrounds/" + player.background);
    screen = Image.open("screens/stats_page.png");    
    draw = ImageDraw.Draw(img);
    img.paste(screen,(0,0),screen)
    if(player.benfont):
        for x in range(0, len(name)):
            width, height = draw.textsize(name, font=font_epic);
            if(width > 149):
                name = name[:len(name)-1];
            else:
                break;
        draw.text((96, 42),name, getRankColour(int(level / 10) + 1), font=font_epic)
    else:
        draw.text((96, 42), name, getRankColour(int(level / 10) + 1), font=font)
    draw.text((142, 62), " " + str(level), (255, 255, 255), font=font_big)
    # Fill data
    width, height = draw.textsize(str(attk), font=font)
    draw.text((241 - width, 122), str(attk), (255, 255, 255), font=font)

    width, height = draw.textsize(str(strg), font=font)
    draw.text((241 - width, 150), str(strg), (255, 255, 255), font=font)

    width, height = draw.textsize(str(shooting), font=font)
    draw.text((241 - width, 178), str(shooting), (255, 255, 255), font=font)

    width, height = draw.textsize("$" + util_due.to_money(player.money) , font=font)
    draw.text((241 - width, 204), "$" + util_due.to_money(player.money) , (255, 255, 255), font=font)
    
    width, height = draw.textsize(str(player.quests_won), font=font)
    draw.text((241 - width, 253), str(player.quests_won), (255, 255, 255), font=font)
    
    width, height = draw.textsize(str(player.wagers_won), font=font)
    draw.text((241 - width, 267), str(player.wagers_won), (255, 255, 255), font=font)
    wep = filter_func(get_weapon_from_id(player.wID).name);
    width, height = draw.textsize(str(wep), font=font)
    draw.text((241 - width, 232), str(wep), (255, 255, 255), font=font)
    # here
    if(avatar != None):
        img.paste(avatar, (9, 12));
    c = 0;
    l = 0;
    first_even = True;
    for x in range(len(player.awards) - 1, -1, -1):
         if (c % 2 == 0):
             img.paste(AwardsIcons[player.awards[x]], (18, 121 + 35 * l));
         else:
             img.paste(AwardsIcons[player.awards[x]], (53, 121 + 35 * l));
             l = l + 1;
         c = c + 1;
         if(c == 8):
             break;
    if(len(player.awards) > 8):
        draw.text((18, 267), "+ " + str(len(player.awards) - 8) + " More", (48, 48, 48), font=font);
    if(len(player.awards) == 0):
        draw.text((38, 183), "None", (48, 48, 48), font=font);
    #img.save(fname + '.png')
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await client.send_file(message.channel, fp=output, filename="myinfo.png",content=":pen_fountain: **"+player.name+"'s** information.");
    output.close()


   # os.remove(fname + '.png')
    
async def displayQuestImage(quest, message):
    await client.send_typing(message.channel);
    try:
        avatar = resize_avatar(quest, message.server, True, 72, 72);
    except:
        avatar = None;
    level = math.trunc(quest.level);
    attk = round(quest.attack, 2);
    strg = round(quest.strg, 2);
    shooting = round(quest.shooting, 2)
    name = filter_func(quest.name);
    img = Image.open("screens/stats_page_quest.png");
    draw = ImageDraw.Draw(img)
    g_quest = get_game_quest_from_id(quest.qID);
    draw.text((88, 38), name, getRankColour(int(level / 10) + 1), font=font)
    draw.text((134, 58), " " + str(level), (255, 255, 255), font=font_big)
    # Fill data
    width, height = draw.textsize(str(attk), font=font)
    draw.text((203 - width, 123), str(attk), (255, 255, 255), font=font)

    width, height = draw.textsize(str(strg), font=font)
    draw.text((203 - width, 151), str(strg), (255, 255, 255), font=font)

    width, height = draw.textsize(str(shooting), font=font)
    draw.text((203 - width, 178), str(shooting), (255, 255, 255), font=font)

    wep = filter_func(get_weapon_from_id(quest.wID).name);
    width, height = draw.textsize(str(wep), font=font)
    draw.text((203 - width, 207), str(wep), (255, 255, 255), font=font)
    
    if(g_quest != None):
        creator = filter_func(g_quest.created_by);
        home = filter_func(g_quest.made_on);
    else:
        creator = "Unknown";
        home = "Unknown";
    
    width, height = draw.textsize(creator, font=font)
    draw.text((203 - width, 228), creator, (255, 255, 255), font=font)
    
    width, height = draw.textsize(home, font=font)
    draw.text((203 - width, 242), home, (255, 255, 255), font=font)
    
    width, height = draw.textsize("$" + util_due.to_money(quest.money), font=font_med)
    draw.text((203 - width, 266), "$" + util_due.to_money(quest.money), (48, 48, 48), font=font_med)

    if(avatar != None):
        img.paste(avatar, (9, 12));
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await client.send_file(message.channel, fp=output, filename="questinfo.png",content=":pen_fountain: Here you go.");
    output.close()

    
async def playerProgress(message):
    global Players;
    Found = False;
    gplayer = findPlayer(message.author.id);
    if(gplayer != None):
        if(gplayer.wID != no_weapon_id):
            if(gplayer.wep_sum != get_weapon_sum(gplayer.wID)):
                await sell(message,gplayer.userid,True);
        await validate_weapon_store(message,gplayer);
        Found = True;
        if((time.time() - gplayer.last_progress) >= 60):
            #print(gplayer.name.encode('ascii','replace').decode() + " Progressed!");
            gplayer.last_progress = time.time();
            startLevel = gplayer.level;
            addAttack = (len(message.content) / 600);
            if(addAttack < 0.02):
                addAttack = addAttack + 0.02;
            addstrg = (util_due.capsCount(message) / 400);
            if(addstrg < 0.03):
                addstrg = addstrg + 0.03;
            addshoot = (((message.content.count(' ') + message.content.count('.') + message.content.count("'") / 3) / 200));
            if(addshoot < 0.01):
                addshoot = addshoot + 0.01;
            gplayer.attack = gplayer.attack + addAttack;
            gplayer.strg = gplayer.strg + addstrg;
            gplayer.shooting = gplayer.shooting + addshoot;
            gplayer.level = gplayer.level + ((((gplayer.attack - 1) + (gplayer.strg - 1) + (gplayer.shooting - 1)) / 3) / math.pow(gplayer.level, 3));                                          
            gplayer.hp = 10 * gplayer.level;
            if math.trunc(gplayer.level) > math.trunc(startLevel):
                MONEY = math.trunc(gplayer.level) * 10;
                gplayer.money = gplayer.money + MONEY;
                if(not(message.server.id+"/"+message.channel.id in util_due.mutedchan)):
                    await level_up_image(message, gplayer, MONEY);
                else:
                    print("Won't send level up image - channel blocked.")
                rank = int(gplayer.level / 10) + 1;
                if(rank == 2):
                    await give_award(message, gplayer, 2, "Attain rank 2.");
                elif (rank > 2 and rank <=9):
                    await give_award(message, gplayer, rank+2, "Attain rank "+str(rank)+".");         
            savePlayer(gplayer);
    if not Found:
        p = player();
        p.userid = message.author.id;
        if(len(message.author.name) <= 13):
            p.name = message.author.name;
        else:
            p.name = message.author.name[:10] + "...";
        p.wID = no_weapon_id;
        Players[str(message.author.id)] = p;
        savePlayer(p);

async def Battle(message, players, wager, quest):  # Quest like wager with diff win text
    global Players;
    global Weapons;
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10 and (wager == None and quest == False) ):
        await client.send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    if(wager == None and quest == False):
        PlayerO = findPlayer(players[0]);
        PlayerT = findPlayer(players[1]);
    elif (quest == True):
        PlayerO = findPlayer(players[0]);
        PlayerT = players[1];
    else:
        PlayerO = findPlayer(message.author.id);
        PlayerT = findPlayer(wager.senderID);
    turns = 0;
    hpO = 0;
    hpT = 0;
    battle_lines = 0;
    if (PlayerO != None) and (PlayerT != None):
        WeaponO = get_weapon_from_id(PlayerO.wID);
        WeaponT = get_weapon_from_id(PlayerT.wID);
        hpO = PlayerO.hp;
        hpT = PlayerT.hp;
        bText = "```(" + PlayerO.name + " Vs " + PlayerT.name + ")\n";
        while (hpO > 0) and (hpT > 0):
            aT = PlayerT.attack;
            aO = PlayerO.attack;
            if(PlayerT.wID != no_weapon_id):
                if((random.randint(1, WeaponT.chance) == 1)):
                    if(WeaponT.melee == False):
                        aT = WeaponT.attack * PlayerT.shooting;
                    else:
                        aT = (WeaponT.attack * (PlayerT.attack));
                    if not quest:
                        bText = bText + PlayerT.name + " " + WeaponT.useText + " " + PlayerO.name + "!\n";
                    else:
                        bText = bText + "The " + PlayerT.name + " " + WeaponT.useText + " " + PlayerO.name + "!\n";
                    battle_lines = battle_lines +1;
            damO = (aT - (PlayerO.strg / 3));
            if damO < 0:
                damO = 0.01;
            hpO = hpO - damO;
            if(PlayerO.wID != no_weapon_id):
                if((random.randint(1, WeaponO.chance) == 1)):
                    if(WeaponO.melee == False):
                        aO = WeaponO.attack * PlayerO.shooting;
                    else:
                        aO = (WeaponO.attack) * PlayerO.attack;
                    if not quest:
                        bText = bText + PlayerO.name + " " + WeaponO.useText + " " + PlayerT.name + "!\n";
                    else:
                        bText = bText + PlayerO.name + " " + WeaponO.useText + " the " + PlayerT.name + "!\n";
                    battle_lines = battle_lines +1;
            damT = (aO - (PlayerT.strg / 3));
            if damT < 0:
                damT = 0.01;
            hpT = hpT - damT;
            turns = turns + 1;
        txt = "turns";
        if(turns == 1):
            txt = "turn"
        if(battle_lines > 25):
            bText = "```(" + PlayerO.name + " Vs " + PlayerT.name + ")\nThe battle was too long to display!\n";
        if(hpO > hpT):
            if(wager == None):
                await battle_image(message, PlayerO, PlayerT, bText + PlayerO.name + " Wins in " + str(turns) + " " + txt + "!\n```\n");
            else:
                bText = bText +PlayerO.name + " Wins in " + str(turns) + " " + txt + "!\n";
                if not quest:
                    bText = bText + PlayerO.name + " receives $" + util_due.to_money(wager.wager)+ " in winnings from " + PlayerT.name + "!\n```\n";
                    PlayerO.money = PlayerO.money + (wager.wager * 2);
                    PlayerO.wagers_won = PlayerO.wagers_won + 1;
                    await give_award(message, PlayerO, 13, "Win a wager!");
                    await give_award(message, PlayerT, 14, "Lose a wager!");
                    savePlayer(PlayerO);
                    savePlayer(PlayerT);
                else:
                    PlayerO.money = PlayerO.money + wager;
                    bText = bText +PlayerO.name + " completed a quest and earned $" +  util_due.to_money(wager)+ "!\n```\n";
                    PlayerO.quests_won = PlayerO.quests_won + 1;
                    await give_award(message, PlayerO, 1, "*Saved* the server.");
                    savePlayer(PlayerO);
                await battle_image(message, PlayerO, PlayerT, bText);
        elif (hpT > hpO):
            if(wager == None):
                await battle_image(message, PlayerO, PlayerT, bText +PlayerT.name + " Wins in " + str(turns) + " " + txt + "!\n```\n");
            else:
                if not quest:
                    bText = bText +PlayerT.name + " Wins in " + str(turns) + " " + txt + "!\n";
                    bText = bText + PlayerT.name + " receives $" + util_due.to_money(wager.wager) + " in winnings from " + PlayerO.name + "!\n```\n";
                    PlayerT.money = PlayerT.money + (wager.wager * 2);
                    PlayerT.wagers_won = PlayerT.wagers_won + 1;
                    await give_award(message, PlayerT, 13, "Win a wager!");
                    await give_award(message, PlayerO, 14, "Lose a wager!");
                    savePlayer(PlayerO);
                    savePlayer(PlayerT);
                else:
                    bText = bText + "The " + PlayerT.name + " Wins in " + str(turns) + " " + txt + "!\n";
                    bText = bText + ""+PlayerO.name + " failed a quest and lost $" + util_due.to_money(int((wager) / 2))+ "!\n```\n";
                    PlayerO.money = PlayerO.money - int((wager) / 2);
                    await give_award(message, PlayerO, 3, "Red mist.");
                    savePlayer(PlayerO);
                await battle_image(message, PlayerO, PlayerT, bText);
        else:
            if(wager == None):
                await battle_image(message, PlayerO, PlayerT, bText + "Draw in " + str(turns) + " " + txt + "!\n```\n");
            else:
                if not quest:
                    PlayerT.money = PlayerT.money + wager.wager;
                    PlayerO.money = PlayerO.money + wager.wager;
                    await battle_image(message, PlayerO, PlayerT, bText + "Draw in " + str(turns) + " " + txt + " wagered money has been returned.\n```\n");
                    savePlayer(PlayerO);
                    savePlayer(PlayerT);
                else:
                    await battle_image(message, PlayerO, PlayerT, bText + "Quest ended in draw no money has been lost or won.\n```\n");
                    savePlayer(PlayerO);
                    savePlayer(PlayerT);

    else:
        if(PlayerO == None):
            await client.send_message(message.channel, "**"+util_due.get_server_name(message,players[0])+"** Has not joined!");
        if(PlayerT == None):
            await client.send_message(message.channel, "**"+util_due.get_server_name(message,players[1])+"** Has not joined!");
            
async def manageQuests(message):
    player = findPlayer(message.author.id);
    if(message.server.id not in ServersQuests and not os.path.isfile("saves/gamequests/"+message.server.id)):
        addQuests(message.server.id);
    if((time.time() - player.last_quest) >= 360):
        player.last_quest = time.time();
        if(message.server.id in ServersQuests and len(ServersQuests[message.server.id]) >= 1):
            n_q = ServersQuests[message.server.id][random.choice(list(ServersQuests[message.server.id].keys()))];
            if (random.randint(1, n_q.spawnchance) == 1) and len(player.quests) <= 6:
                await addQuest(message, player, n_q);

async def addQuest(message, player, n_q):
    aQ = createQuest(n_q, player);
    savePlayer(player);
    if(not(message.server.id+"/"+message.channel.id in util_due.mutedchan)):
        await new_quest_image(message, aQ, player);
    else:
        print("Won't send new quest image - channel blocked.")

def createQuest(n_q, player):
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

async def showQuests(message):
      #global GameQuests;
      player = findPlayer(message.author.id);
      command_key = util_due.get_server_cmd_key(message.server);
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
      await client.send_message(message.channel, QuestsT);
      
def findPlayer(pID):
    global Players;
    if(pID in Players):
        return Players[str(pID)]
    else:
        return None;
    


