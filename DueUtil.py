import discord
import os
import util_due;
import due_battles_quests;
import sys;
import urllib.request as url3;
import urllib.parse as url1;
import urllib;
import requests;
import time;
import configparser 


last_backup = 0;
client = discord.Client()
stopped = False;
start_time = 0;
bot_key = "MjEyNzA3MDYzMzY3ODYwMjI1.Cwk-Cg.N98twLnUL6i0VPePyzUsn1bNf-4";

def load_config():
    global bot_key;
    config = configparser.RawConfigParser();
    try:
        config.read('dueutil.cfg')
        bot_key = config.get("DueUtil General","bot_key");
    except:
        create_config(config);
		
def create_config(config):
    config.add_section("DueUtil General");
    config.set("DueUtil General","bot_key",bot_key);
    with open('dueutil.cfg', 'w+') as cfg_file:
        config.write(cfg_file)
		
def get_help_page(help_file,page,key,server):
    with open (help_file, "r") as myfile:
        data=myfile.readlines();
    return util_due.get_page_with_replace(data,page,key,server);


async def send_text_as_message(to,txt_name,key,message):
    with open (txt_name, "r") as myfile:
        data=myfile.readlines();
    txt ="";
    for line in data:
        txt = txt+line.replace("[CMD_KEY]",key).replace("[SERVER]",message.server.name);
    await client.send_message(to,txt);   
    
def sudo_command(key,message):
  if(util_due.is_admin(message.author.id) and message.content.lower().startswith(key+"sudo ")):
    message.author = message.server.get_member(message.raw_mentions[0]);
    message.content = content = key+message.content.split('>',1)[1].strip();
    del message.raw_mentions[0];

@client.event
async def on_message(message):
    #print(due_battles_quests.filter_func(message.author.id+"["+util_due.get_server_name(message, message.author.id)+"] ->"+message.content));
    #return;
    #print(await due_battles_quests.battle_quest_on_message(message));
    #message.content = message.content.replace("`","'")
    # we do not want the bot to reply to itself
    global stopped;
    global last_backup;
    global start_time;
    command_key = None;
    pri_server = "";
   
    if not is_due_loaded():
        return;
    if(not message.channel.is_private):
        message.content = util_due.escape_markdown(message.content);
        botme = message.server.get_member(client.user.id);
        bot_perms = message.channel.permissions_for(botme);
        if(not (bot_perms.send_messages and bot_perms.read_messages and bot_perms.attach_files and bot_perms.embed_links)):
            return;
        command_key = util_due.get_server_cmd_key(message.server);
    if not stopped:
        sudo_command(command_key,message);
        if(time.time() - last_backup > 3600):
            util_due.zipdir("saves/","autobackups/DueBackup"+str(time.time())+".zip");
            print("Auto backup!");
            last_backup = time.time();
        if message.author.bot:
            return;
        if message.channel.is_private:
            msg_x = 0;
            for msg in reversed(list(client.messages)):
                if(msg_x == 10):
                    await client.send_file(message.channel,'images/no_mem.png',content = "If you still need help run the command again on a server!");
                    await due_battles_quests.give_award_id(message,message.author.id,15,"Dumbledore!!!")
                    command_key = None;
                    break;
                if(msg.channel == message.channel):
                    if("**run the help command on a server**" in msg.content and msg.author.id == client.user.id):
                        break;
                    msg_x = msg_x +1;
                    if("DueUtil's Help!" in msg.content and msg.author.id == client.user.id):
                        server_info = msg.content.splitlines()[1].split(sep="**");
                        command_key =server_info[3].strip();   
                        pri_server=server_info[1];  
                        break;
        if message.author == client.user:
            return
        elif(command_key != None and message.content.lower().startswith(command_key+'help')):
            if(not message.channel.is_private):
                await client.send_message(message.channel,"I'll PM you the help! :wink:");
                await client.start_private_message(message.author);
                await send_text_as_message(message.author,"help_info.txt",command_key,message);
                return True;
            elif message.content.lower().strip().startswith(command_key+'help '):
                msgArgs = message.content.lower().strip();
                helpfor = '';
                if 'anyone' in msgArgs:
                    helpfor = 'anyone';
                elif 'admins' in msgArgs:
                    helpfor = 'admins';
                else:
                    return;
                args = msgArgs.replace(command_key+'help '+helpfor,'').strip();
                page = 1;
                try:
                    page = int(args);
                except:
                    page = 1;
                if(page <= 0):
                    page = 1;
                help_i = get_help_page('help_'+helpfor+'.txt',page-1,command_key,pri_server);
                if(help_i == None):
                    await client.send_message(message.author,":bangbang: **Page not found!**" );
                    return;
                if(page == 1):
                    await client.send_message(message.author,'**Help for '+helpfor+'**');
                else:
                    await client.send_message(message.author,'**Help for '+helpfor+'**: Page '+str(page));
                await client.send_message(message.author,help_i[0]);
                if(help_i[1]):
                    await client.send_message(message.author,"But wait there's more! Type **"+command_key+"help "+helpfor+" "+str(page+1)+"** for the next page.");
            else:
                await client.send_message(message.author,"Still here! Do **"+command_key+"help anyone** or **"+command_key+"help admins** to see my commands!");
        elif message.channel.is_private and command_key == None:
            await client.send_message(message.channel,"If you're here looking for a chat this isn't the right place.\nIf you're looking for help **run the help command on a server** first so I know where you're coming from.");
            return;
        elif message.channel.is_private:
            return;
        elif ((message.author.id == "132315148487622656") or (util_due.is_admin(message.author.id))) and message.content.lower().startswith(command_key+'stop'):
            stopped = True;
            await client.send_message(message.channel,"Stopping DueUtil!");
            print("DueUtil stopped by admin "+message.author.id);
            client.loop.run_until_complete(client.logout());
            await client.close()
            client.loop._default_executor.shutdown(wait=True);
            sys.exit(0);
        elif(await due_battles_quests.battle_quest_on_message(message)):
           return;
        elif message.content.lower().startswith(command_key+'dustats'):
            stats = "```Since "+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time))+" I have\u2026\n";
            stats += "Served "+util_due.number_format_text(due_battles_quests.images_served)+" image(s).\n";
            stats += "Created $"+util_due.number_format_text(due_battles_quests.money_created)+"\n";
            stats += "Transferred $"+util_due.number_format_text(due_battles_quests.money_transferred)+"\n";
            stats += "Given "+util_due.number_format_text(due_battles_quests.quests_given)+" new quest(s).\n";
            stats += "Seen "+util_due.number_format_text(due_battles_quests.quests_attempted)+" quest(s) attempted.\n";
            stats += "Watched "+util_due.number_format_text(due_battles_quests.players_leveled)+" player(s) level up.\n";
            stats += "Had "+util_due.number_format_text(due_battles_quests.new_players_joined)+" player(s) join.\n```";
            await client.send_message(message.channel,stats);
            return;
        elif (await util_due.on_util_message(message)):
            return;
        elif (message.content == "(╯°□°）╯︵ ┻━┻" and not(message.server.id+"/"+message.channel.id in util_due.mutedchan)):
             await client.send_file(message.channel,'images/unflip.png');
             return;
        elif (message.content == "┬─┬﻿ ノ( ゜-゜ノ)" and not(message.server.id+"/"+message.channel.id in util_due.mutedchan)):
             await client.send_file(message.channel,'images/fliptable.png');
             return;
        elif "helpme" in message.content.lower():
            for mentions in message.raw_mentions:
                    if(client.user.id in mentions):
                            await client.start_private_message(message.author);
                            await send_text_as_message(message.author,"help_info.txt",command_key,message)
                            await client.send_message(message.channel,"Hi! I've PM-ed you my help!\nP.S. **"+command_key+"** is the command key on **"+message.server.name+"**!");	
                            
                            		
            return;					
        else:
            for mentions in message.raw_mentions:
                if(client.user.id in mentions):
                    msg = util_due.clearmentions(message.content);
                    if(len(msg) <= 255):
                        f = { 'bot_id' : '6', 'say' : msg,'convo_id' : message.author.id,'format' :'xml'};
                        try:
                            await client.send_typing(message.channel);
                            r = requests.get("http://api.program-o.com/v2/chatbot/?"+url1.urlencode(f),timeout=3);
                            for line in r.content.splitlines():
                                if("response" in str(line)):
                                    msg = str(line);
                                    msg = msg.split(sep="<response>", maxsplit=1)[1];
                                    msg = msg.split(sep="</response>", maxsplit=1)[0];
                                    await client.send_message(message.channel,":speaking_head: "+msg);
                                    return;
                        except:
                            await client.send_message(message.channel,":speaking_head: I'm a little too busy to talk right now! Sorry!");
def is_due_loaded():
    return util_due.loaded and due_battles_quests.loaded;

@client.event
async def on_ready():
    global start_time;
    start_time = time.time();
    help_status = discord.Game();
    help_status.name = "@DueUtil helpme"
    await client.change_presence(game=help_status,afk=False);
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
def load_due():
    load_config();
    due_battles_quests.load(client);
    util_due.load(client);

def run_due():
    global stopped;
    if not os.path.exists("saves/players"):
        os.makedirs("saves/players")  
    if not os.path.exists("saves/weapons"):
        os.makedirs("saves/weapons")  
    if not os.path.exists("saves/gamequests"):
        os.makedirs("saves/gamequests")  
    if not os.path.exists("saves/util"):
        os.makedirs("saves/util")  
    if not os.path.exists("autobackups/"):
        os.makedirs("autobackups/")  
    if not os.path.exists("imagecache/"):
        os.makedirs("imagecache/")  
    if(not stopped):
        if not is_due_loaded():
            load_due();
        client.run(bot_key);
        run_due();
      
print("Starting DueUtil!")
run_due();
#k=input("press close to exit")
#raw_input()

