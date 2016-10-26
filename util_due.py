import discord
import random
import requests
import re
import urllib.request
from bs4 import BeautifulSoup
import os.path
from datetime import datetime
import math
import sys
from html.parser import HTMLParser
import time;
import due_battles_quests
import zipfile;
import shutil;
import jsonpickle;
import json;
loaded = False;
DueUtilAdmins=[];
DueUtilMods=[];
AutoReplys = [];
mutedchan = [];
basicMode = False;
servers = dict();
serverKeys = dict();
client = None;

class autoReply:
    message = "";
    key = "";
    target = "";
    attarget = False;
    server = "";
    username ="";
    timed = "";
    alt = "";
    channel = None;

def get_server_cmd_key(server):
    return serverKeys.setdefault(server.id,"!");

def to_money(amount):
    return '{:20,.0f}'.format(amount).strip();

def random_ident():
    ident ="";
    identChars = "0123456789@#$%&QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm=";
    for x in range(0,6):
        ident= ident + identChars[(random.randint(0,len(identChars)-1))];
    return ident;

def get_server_name(message,id):
    return message.server.get_member(id).name;

def get_server_name_S(server,id):
    return server.get_member(id).name;
    
def get_page_with_replace(data,page,key,server):
    output ='```';
    test = output;
    if(not isinstance(data, list)):
        if(len(data)+6 < 2000):
            return ['```'+data+'```',False]
        data = data.splitlines();
    for x in range (0,page):
        test = test + '``````'
    for line in data:   
        if(key != None and server != None):
            text = line.replace("[CMD_KEY]",key).replace("[SERVER]",server);
        else:
            text = line;
        if(not ('\n' in text)):
            text = text + '\n';
        new_ln = output+ text;
        test = test + text;
        if(len(test) >= 1997*page):          
            if(len(test ) < 1997*(page+1) and len(new_ln) <= 1997):
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
    
def is_admin(id):
    return id in DueUtilAdmins or id == '132315148487622656';
def is_mod(id):
    return id in DueUtilMods or id == '132315148487622656';
def is_mod_or_admin(id):
    return id in DueUtilAdmins or id in DueUtilMods or id =='132315148487622656';
    
async def on_util_message(message):
    global servers;
    global serverKeys;
    global mutedchan;
    global basicMode;
    global AutoReplys;
    global DueUtilAdmins
    global DueUtilMods
    found = True;
    command_key = get_server_cmd_key(message.server);
    basicMode = servers.setdefault(message.server,False);
    if (message.content.lower().startswith(command_key+'addadmin') or message.content.lower().startswith(command_key+'removeadmin')) and is_admin(message.author.id):
        temp = await mod_admin_manage(message,'admin',21,DueUtilAdmins);
        if(temp != None):
            DueUtilAdmins = temp;
            saveGeneric(DueUtilAdmins, "due_admins");
        return True;
    elif (message.content.lower().startswith(command_key+'addmod') or message.content.lower().startswith(command_key+'removemod')) and is_admin(message.author.id):
        temp = await mod_admin_manage(message,'mod',22,DueUtilMods);
        if(temp != None):
            DueUtilMods = temp;
            saveGeneric(DueUtilMods, "due_mods");
        return True;
    elif ((message.author.id == "132315148487622656") or is_admin(message.author.id)) and message.content.lower().startswith(command_key+'givecash'):
        arg = message.content.replace(command_key+"givecash ","");
        arg = clearmentions(arg);
        r=userMentions(message);
        try:
        #if(1==1):
            if(len(r) == 1):
                p=due_battles_quests.findPlayer(r[0]);
                if(p != None):
                    p.money = p.money + int(arg);
                    await client.send_message(message.channel,"$"+to_money(int(arg))+" has been given to **"+p.name+"**.");
                else:
                    await client.send_message(message.channel,"**"+get_server_name(message, r[0])+"** is not playing.");
        except:
            await client.send_message(message.channel,":bangbang: **I don't understand your arguments**");
        return True;  
    elif ((message.author.id == "132315148487622656") or is_mod_or_admin(message.author.id)) and message.content.lower().startswith(command_key+'backup'):
        print("DueUtil backedup by admin "+message.author.id);
        zipdir("saves/","DueBackup.zip");
        await client.send_file(message.channel,'DueBackup.zip',filename=None,content =":white_check_mark: **DueUtil has been backed up!**");
        return True;
    elif message.content.lower().startswith(command_key+'shutupdue') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        if(not (message.server.id+"/"+message.channel.id in mutedchan)):
            mutedchan.append(message.server.id+"/"+message.channel.id);
            #pickle.dump(mutedchan,open ("saves/muted.p","wb"),protocol=pickle.HIGHEST_PROTOCOL);
            saveGeneric(mutedchan, "mute_channels")
            await client.send_message(message.channel,"Ok! I won't give any level up or other alerts in this channel.\nType **"+command_key+"unshutupdue** to enable my alerts again!");
        else:
            await client.send_message(message.channel,"I've already shut up in this channel! Use **"+command_key+"unshutupdue** to enable my alerts again.");
        return True;
    elif message.content.lower().startswith(command_key+'setcmdkey') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        cmdKey = message.content.lower().replace(command_key+'setcmdkey','');
        cmdKey = cmdKey.replace(' ','');
        if(len(cmdKey) >= 1 and len(cmdKey) <= 2):
            serverKeys.setdefault(message.server.id,"!");
            serverKeys[message.server.id]=cmdKey;
            #pickle.dump(serverKeys,open ("saves/server_cmd_keys.p","wb"),protocol=pickle.HIGHEST_PROTOCOL);
            saveGeneric(serverKeys, "server_keys")
            await client.send_message(message.channel,"Ok! I'll only respond to commands starting with **"+cmdKey+"** on **"+message.server.name+"**.");
        else:
            await client.send_message(message.channel,":bangbang: **Your command key can only be one or two characters long!**");
        return True;
    elif message.content.lower().startswith(command_key+'unshutupdue') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        if((message.server.id+"/"+message.channel.id in mutedchan)):
            del mutedchan[mutedchan.index(message.server.id+"/"+message.channel.id)];
            #pickle.dump(mutedchan,open ("saves/muted.p","wb"),protocol=pickle.HIGHEST_PROTOCOL);
            saveGeneric(mutedchan, "mute_channels");
            await client.send_message(message.channel,"I shall once more speak freely in this channel!");
        else:
            await client.send_message(message.channel,"I have not yet shut up in this channel!");
        return True;
    elif message.content.lower().startswith(command_key+'dujoin'):
        await client.send_message(message.channel, ":bangbang: **I can no longer accept invites to servers!**\nIf you want to add me to a server use this link :point_down:\nhttps://discordapp.com/oauth2/authorize?access_type=online&client_id=173391673634717696&scope=bot&permissions=52224");
        return True;
    elif message.content.lower().startswith(command_key+'gtrandom'):
        await randomWord(message);
        return True;
    elif message.content.lower().startswith(command_key+'glittertext'):
            strToGif = message.content.replace(command_key+"glittertext","",1);
            await createGlitterText(message,strToGif);
            return True;
    elif message.content.lower().startswith(command_key+'gt '):
        strToGif = message.content.replace(command_key+"gt ","",1);
        await createGlitterText(message,strToGif);
        return True;
    elif message.content.lower().startswith(command_key+'timedreply') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        Worked = False;
        messageArg = message.content.replace(command_key+"timedreply ","",1);
        Strs = get_strings(messageArg);
        if(len(Strs) == 4):
            ar = autoReply();
            ar.timed = Strs[0];
            ar.key = Strs[1].lower();
            ar.message = Strs[2];
            ar.alt = Strs[3];
            ar.channel = message.channel;
            ar.server = message.server.id;
            try:
                date_object = datetime.strptime(ar.timed,"%H:%M");
                AutoReplys.append(ar);
                worked = True;
            except:
                worked = False;
        if worked:
            #pickle.dump(AutoReplys,open ("saves/replys.p","wb"),protocol=pickle.HIGHEST_PROTOCOL);
            saveGeneric(AutoReplys, "auto_replys");
            await client.send_message(message.channel,":white_check_mark: **Timed reply created!**");
        else:
            await client.send_message(message.channel,":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key+'autoreply') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        target = message.raw_mentions;
        worked = False;
        messageArg = message.content.replace(command_key+"autoreply ","",1);
        if(len(target)==1):
            messageArg = clearmentions(message.content);
        Strs = get_strings(messageArg);
        print(Strs);
        if(len(target) == 1):
            #print(Strs[0]);
            #print(Strs[1]);
            if(len(Strs) == 2):
                ar = autoReply();
                ar.key = Strs[0].lower();
                ar.message = Strs[1];
                ar.server = message.server.id;
                ar.target = target[0];
                ar.attarget = True;
                AutoReplys.append(ar);
                worked = True;
                print("TEST WOOP");
        elif (len(Strs) == 2) and (len(target) == 0):
                ar = autoReply();
                ar.key = Strs[0].lower();
                ar.message = Strs[1];
                ar.server = message.server.id;
                ar.target = 0;
                ar.attarget = False;
                AutoReplys.append(ar);
                worked = True;
                
        elif (len(Strs) == 3) and (len(target) == 0):
                ar = autoReply();
                ar.key = Strs[1].lower();
                ar.message = Strs[2];
                ar.server = message.server.id;
                ar.target = 0;
                ar.username = Strs[0]
                ar.attarget = False;
                AutoReplys.append(ar);
                worked = True;
        if worked:
            saveGeneric(AutoReplys, "auto_replys");
            await client.send_message(message.channel,":white_check_mark: **Auto reply created!**");
        else:
            await client.send_message(message.channel,":bangbang: **I don't understand your arguments**");
        return True;
    elif message.content.lower().startswith(command_key+'removereply ') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        messageArg = message.content.replace(command_key+"removereply ","",1);
        args = messageArg.split();
        if(args[0].lower() == 'all'):
            for reply in AutoReplys:
                if(message.server.id == reply.server):
                    print(AutoReplys[AutoReplys.index(reply)]);
                    del AutoReplys[AutoReplys.index(reply)];
            saveGeneric(AutoReplys, "auto_replys");
            await client.send_message(message.channel,":wastebasket:  **All replys cleared.**");
        else:
            try:
                if(AutoReplys[int(args[0])].server == message.server.id):
                    del AutoReplys[int(args[0])];
                    await client.send_message(message.channel,":wastebasket: **Reply cleared.**");
                else:
                    await client.send_message(message.channel,":bangbang: **Reply does not exist.**");
            except:
                await client.send_message(message.channel,":bangbang: **Reply does not exist.**");
            saveGeneric(AutoReplys, "auto_replys");
        return True;
    elif message.content.lower().startswith(command_key+'listreplys') and (message.author.permissions_in(message.channel).manage_server or is_mod_or_admin(message.author.id)):
        Found = False;
        list_out = "```Auto replys on "+message.server.name+"\n";
        for x in range(0,len(AutoReplys)):
            if(message.server.id == AutoReplys[x].server):
                Found = True;
                Reply = "ID: "+str(x)+" - Message: '"+AutoReplys[x].message+"' - Key: '"+AutoReplys[x].key+"' - For: ";
                if(AutoReplys[x].username == "") and (AutoReplys[x].target == 0) and (AutoReplys[x].timed == ""):
                    Reply = Reply+" everyone";
                elif (len(AutoReplys[x].username) > 0) and (AutoReplys[x].timed == ""):
                    Reply = Reply+"(username) "+AutoReplys[x].username;
                elif  (len(AutoReplys[x].timed)> 0):
                    Reply = "ID: "+str(x)+" - AfterTimeMessage: '"+AutoReplys[x].message+"' - BeforeTimeMessage: '"+AutoReplys[x].alt+"' - Key: '"+AutoReplys[x].key+"' - Time: '"+AutoReplys[x].timed+"'";
                else:
                    Reply = Reply+"@"+get_server_name(message,AutoReplys[x].target)+" ";
                list_out = list_out + Reply+"\n";
        if not Found:
            await client.send_message(message.channel,":bangbang: **There are no auto replys on this server.**");
        else:
            await client.send_message(message.channel,list_out+"```");
        return True;
    elif message.content.lower().startswith(command_key+'gtbasic'):
        if basicMode:
            servers.setdefault(message.server,False);
            servers[message.server]=False;
            await client.send_message(message.channel, "Returned to normal mode for **"+message.server.name+"**.");
            return True;
        else:
            servers.setdefault(message.server,False);
            servers[message.server]=True;
            await client.send_message(message.channel, "Set to basic mode in **"+message.server.name+"**!");
            await client.send_message(message.channel, "Type **"+command_key+"gtbasic** again or **"+command_key+"gtnormal** to return to normal.");
            return
        return True;
    elif message.content.lower().startswith(command_key+'gtnormal'):
        servers.setdefault(message.server,False);
        servers[message.server]=False;
        await client.send_message(message.channel, "Returned to normal mode for **"+message.server.name+"**.");
        return True;
    elif message.content.lower().startswith(command_key+'duservers'):
        await client.send_message(message.channel, "DueUtil is currently active on **"+str(len(servers))+" servers**.");
        return True;
    else:
        found = False;
        for x in range(0,len(AutoReplys)):
            if(AutoReplys[x].timed == ""):
                if ((message.author.id == AutoReplys[x].target) or (AutoReplys[x].target == 0) or (message.author.name == AutoReplys[x].username)) and message.server.id == AutoReplys[x].server:
                    if(AutoReplys[x].key in message.content.lower()):
                        if AutoReplys[x].attarget == False:
                            await client.send_message(message.channel,AutoReplys[x].message);
                        else:
                            await client.send_message(message.channel,"<@"+AutoReplys[x].target+"> "+AutoReplys[x].message);
            else:
                if(message.server.id == AutoReplys[x].server):
                    if(message.channel == AutoReplys[x].channel) and AutoReplys[x].key in message.content.lower():
                        curStrTime = time.strftime("%H:%M");
                        date_object = datetime.strptime(curStrTime,"%H:%M");
                        date_object2 = datetime.strptime(AutoReplys[x].timed,"%H:%M");
                        if(date_object >= date_object2):
                             await client.send_message(message.channel,AutoReplys[x].message);
                        else:
                             await client.send_message(message.channel,AutoReplys[x].alt);
    return found;
    
async def mod_admin_manage(message,role,award_id,role_list):
    command_key = get_server_cmd_key(message.server);
    if ((message.author.id == "132315148487622656") or is_admin(message.author.id)) and message.content.lower().startswith(command_key+'add'+role):
        rUser = userMentions(message);
        if(len(rUser)==1):
            if(not (rUser[0] in role_list)):
                role_list.append(rUser[0]);
                await client.send_message(message.channel,"**"+get_server_name(message, rUser[0])+"** is now a DueUtil "+role+"!");
                print(role+" "+rUser[0]+" added by "+message.author.id);
                await due_battles_quests.give_award_id(message,rUser[0],award_id,"Become an "+role+"!")
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
                player = due_battles_quests.findPlayer(rUser[0]);
                del player.awards[player.awards.index(award_id)];
            else:
                await client.send_message(message.channel,"**"+get_server_name(message, rUser[0])+"** is not an "+role+" anyway!");
        else:
            await client.send_message(message.channel,":bangbang: **Mention one user you would like to demote.**");
        return role_list;
    return None;

def capsCount(message):
    shoutCount = 0;
    for x in range(0,len(message.content)):
        if(message.content[x].isupper()):
            shoutCount=shoutCount+1;
    return shoutCount;

def saveGeneric(thing,name):
    data = jsonpickle.encode(thing);
    with open("saves/util/" + name+ ".json", 'w') as outfile:
        json.dump(data, outfile);

def loadUtils(name):
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
def load(discord_client):
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
    for server in client.servers:
        servers.setdefault(server,False);
    test =  loadUtils("server_keys");
    if test != None:
        serverKeys = test;
    test =  loadUtils("due_admins");
    if test != None:
        DueUtilAdmins = test;
    test =  loadUtils("due_mods");
    if test != None:
        DueUtilMods = test;
    test =  loadUtils("auto_replys");
    if test != None:
        AutoReplys = test;
    test =  loadUtils("mute_channels");
    if test != None:
        mutedchan = test;
    loaded = True;


def zipdir(path, fname):
    zipf = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()

def userMentions(message):
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

def clearmentions(message):
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

def clearmentions_eh(message):
    clean = message.content;
    for mention in message.raw_mentions:
        clean = clean.replace("<@"+mention+">","").replace("<@!"+mention+">","");
    return clean;

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
            
def copydirectorykut(src, dst):
    os.chdir(dst)
    list=os.listdir(src)
    nom= src+'.txt'
    fitx= open(nom, 'w')

    for item in list:
        fitx.write("%s\n" % item)
    fitx.close()

    f = open(nom,'r')
    for line in f.readlines():
        if "." in line:
            shutil.copy(src+'/'+line[:-1],dst+'/'+line[:-1])
        else:
            if not os.path.exists(dst+'/'+line[:-1]):
                os.makedirs(dst+'/'+line[:-1])
                copydirectorykut(src+'/'+line[:-1],dst+'/'+line[:-1])
            copydirectorykut(src+'/'+line[:-1],dst+'/'+line[:-1])
    f.close()
    os.remove(nom)
    os.chdir('..')


async def randomWord(message):
    try:
        response = requests.get("http://randomword.setgetgo.com/get.php");
        await createGlitterText(message, response.text);
    except:
        await client.send_message(message.channel, "An error occured.");
        print ("Error details.");
        print ("Unexpected error:", sys.exc_info()[0]);

async def createGlitterText(message,strToGif):
    basicMode = servers.get(message.server,False);
    try:
        response = requests.get("http://www.gigaglitters.com/procesing.php?text="+strToGif+"&size=90&text_color=img/DCdarkness.gif&angle=0&border=0&border_yes_no=4&shadows=1&font='fonts/Super 911.ttf'");
        html = response.text;
        soup = BeautifulSoup(html,"html.parser");
        box = soup.find("textarea", {"id": "dLink"});
        text = str(box);
        text = text.replace('<textarea class="field" cols="12" id="dLink" onclick="this.focus();this.select()" readonly="">',"",1);
        text = text.replace('</textarea>',"",1);
        if(not basicMode):
            f = open('temp.gif','wb');
            f.write(requests.get(text).content);
            f.close();
            await client.send_file(message.channel,'temp.gif',filename=None);
        else:
            await client.send_message(message.channel, text);
    except discord.errors.Forbidden:
        await client.send_message(message.channel, "I require the permission to upload files.");
        await client.send_message(message.channel, "If you cannot do this type "+get_server_cmd_key(message.server)+"gtbasic to only use links in this channel.");
    except:
        await client.send_message(message.channel, "An error occured.");
        print ("Error details.");
        print ("Unexpected error:", sys.exc_info()[0]);
