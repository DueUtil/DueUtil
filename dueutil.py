import discord
import os
import util_due;
import due_battles_quests;
import sys;
import urllib.request as url3;
import asyncio;
import urllib.parse as url1;
import urllib;
import requests;
from threading import Thread, local
import time;
import json;
import configparser
from concurrent.futures import ProcessPoolExecutor
import traceback

last_backup = 0;
stopped = False;
start_time = 0;
shard_count = 3;
shard_clients = [];
bot_key = "MjEyNzA3MDYzMzY3ODYwMjI1.Cwk-Cg.N98twLnUL6i0VPePyzUsn1bNf-4";

shard_names = []

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
    
async def sudo_command(key,message):
  if message.channel.is_private:
      return;
  if(util_due.is_admin(message.author.id) and message.content.lower().startswith(key+"sudo ")):
    try:
        message.author = message.server.get_member(message.raw_mentions[0]);
        message.content = content = key+message.content.split('>',1)[1].strip();
        del message.raw_mentions[0];
    except:
        await client.send_message(message.channel, ":bangbang: **sudo failed!**");

class DueUtilClient(discord.Client):

    def __init__(self, *args, **kwargs):
        self.shard_id = int(kwargs["shard_id"]);
        super(DueUtilClient,self).__init__(*args,**kwargs);

    @asyncio.coroutine
    async def on_server_join(self,server):
        server_count = 0;
        for self in shard_selfs:
            server_count+= len(self.servers);
        payload = {"key":'macdue0a873a71hjd673o1',"servercount":len(server_count)};
        url = "https://www.carbonitex.net/discord/data/botdata.php";
        reponse = await aiohttp.post(url, data=payload);
        reponse.close();
        print("Joined server");
    
    @asyncio.coroutine
    async def on_error(self,event,ctx):
        error = sys.exc_info()[1];
        if isinstance(error,util_due.DueUtilException):
            await self.send_message(error.channel,":bangbang: **"+error.message+"**");
        elif isinstance(ctx, discord.Message):
            await self.send_message(ctx.channel,(":bangbang: **Something went wrong...**\n"
                                                 "``"+str(error)+"``"));
            traceback.print_exc();
        else:
            traceback.print_exc();
            
    @asyncio.coroutine
    async def on_message(self,message):
        global stopped;
        global last_backup;
        global start_time;
        
        if not util_due.is_admin(message.author.id):
            return;
        command_key = None;
        pri_server = "";
        # if not is_due_loaded():
        #     return;
        if(not message.channel.is_private):
            message.content = util_due.escape_markdown(message.content);
            botme = message.server.get_member(self.user.id);
            bot_perms = message.channel.permissions_for(botme);
            if(not (bot_perms.send_messages and bot_perms.read_messages and bot_perms.attach_files and bot_perms.embed_links)):
                return;
            command_key = util_due.get_server_cmd_key(message.server);
        if not stopped:
            if(time.time() - last_backup > 20000):
                util_due.zipdir("saves/","autobackups/DueBackup"+str(time.time())+".zip");
                print("Auto backup!");
                last_backup = time.time();
            if message.author.bot:
                return;
            await sudo_command(command_key,message);
            if message.author == self.user:
                return
            #old help
            elif message.channel.is_private:
                return;
            elif ((message.author.id == "132315148487622656") or (util_due.is_admin(message.author.id))) and message.content.lower().startswith(command_key+'stop'):
                
                
                stopped = True;
                await self.send_message(message.channel,"Stopping DueUtil!");
                print("DueUtil stopped by admin "+message.author.id);
                self.loop.run_until_complete(self.logout());
                await self.close()
                self.loop._default_executor.shutdown(wait=True);
                sys.exit(0);
           
           
            elif message.content.lower().startswith(command_key+'changeavatar ') and util_due.is_admin(message.author.id):
               
               
                 await change_avatar(message.channel,message.content[13:]);
            
            
            elif(await due_battles_quests.battle_quest_on_message(self,message)):
               return;
            elif message.content.lower().startswith(command_key+'dustats'):
             
             
                stats = discord.Embed(title="DueUtil Stats",type="rich",description="DueUtil's global stats since "+time.strftime("%m/%d/%Y at %H:%M", time.gmtime(start_time))+"!",color=16038978);
                stats.add_field(name="Images Served",value=util_due.number_format_text(due_battles_quests.images_served));
                stats.add_field(name="Awarded",value="$"+util_due.number_format_text(due_battles_quests.money_created));
                stats.add_field(name="Players have transferred",value="$"+util_due.number_format_text(due_battles_quests.money_transferred));
                stats.add_field(name="Quests Given",value=util_due.number_format_text(due_battles_quests.quests_given));
                stats.add_field(name="Quests Attempted",value=util_due.number_format_text(due_battles_quests.quests_attempted));
                stats.add_field(name="Level Ups",value=util_due.number_format_text(due_battles_quests.players_leveled));
                stats.add_field(name="New Players",value=util_due.number_format_text(due_battles_quests.new_players_joined));
                stats.set_footer(text="DueUtil Shard "+str(self.shard_id+1))
                await self.send_message(message.channel,embed=stats);
                return;
            
            
            elif (await util_due.on_util_message(message)):
               
               
                return;
                
                
            elif (message.content == "(╯°□°）╯︵ ┻━┻" and not(message.server.id+"/"+message.channel.id in util_due.mutedchan)):
                
                
                 await self.send_file(message.channel,'images/unflip.png');
                 return;
                 
                 
            elif (message.content == "┬─┬﻿ ノ( ゜-゜ノ)" and not(message.server.id+"/"+message.channel.id in util_due.mutedchan)):
               
               
                 await self.send_file(message.channel,'images/fliptable.png');
                 return;
          
          
            elif "helpme" in message.content.lower():
             
             
                for mentions in message.raw_mentions:
                        if(self.user.id in mentions):
                                await self.start_private_message(message.author);
                                await send_text_as_message(message.author,"help_info.txt",command_key,message)
                                await self.send_message(message.channel,"Hi! I've PM-ed you my help!\nP.S. **"+command_key+"** is the command key on **"+message.server.name+"**!");	                        
                return;					
            else:
               
               
                for mentions in message.raw_mentions:
                    if(self.user.id in mentions):
                        msg = util_due.clearmentions(message.content);
                        if(len(msg) <= 255):
                            f = { 'bot_id' : '6', 'say' : msg,'convo_id' : message.author.id,'format' :'xml'};
                            try:
                                await self.send_typing(message.channel);
                                r = requests.get("http://api.program-o.com/v2/chatbot/?"+url1.urlencode(f),timeout=3);
                                for line in r.content.splitlines():
                                    if("response" in str(line)):
                                        msg = str(line);
                                        msg = msg.split(sep="<response>", maxsplit=1)[1];
                                        msg = msg.split(sep="</response>", maxsplit=1)[0];
                                        await self.send_message(message.channel,":speaking_head: "+msg);
                                        return;
                            except:
                                await self.send_message(message.channel,":speaking_head: I'm a little too busy to talk right now! Sorry!");
                                
                                
    async def change_avatar(self,channel,avatar_name):
        try:
            avatar = open("avatars/"+avatar_name.strip(),"rb");
            avatar_object = avatar.read();
            await self.edit_profile(avatar=avatar_object);
            await self.send_message(channel, ":white_check_mark: Avatar now **"+avatar_name+"**!");
        except:
            await self.send_message(channel, ":bangbang: **Avatar change failed!**");

    @asyncio.coroutine
    async def on_ready(self):
        #global start_time;
        #start_time = time.time();
        shard_number = shard_clients.index(self) +1;
        help_status = discord.Game();
        help_status.name = "dueutil.tech | shard "+str(shard_number)+"/"+str(shard_count);
        await self.change_presence(game=help_status,afk=False);
        print('Logged in shard '+str(shard_number)+' as ')
        print(self.user.name)
        print(self.user.id)
        print('------')

def get_shard_index(server_id):
    return (int(server_id) >> 22) % shard_count;

def is_due_loaded():
    return util_due.loaded and due_battles_quests.loaded;

def load_due():
    load_config();
    #due_battles_quests.load(shard_clients);
    #util_due.load(client);
    
def setup_due_thread(loop,shard_id):
    global shard_clients;
    asyncio.set_event_loop(loop)
    client = DueUtilClient(shard_id=shard_id,shard_count=shard_count);
    shard_clients.append(client);
    try:
        asyncio.run_coroutine_threadsafe(client.run(bot_key),client.loop);
    finally:
        print("A shard died.");

        
def run_due():
    global stopped;
    global shard_clients
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
        for shard_number in range(0,shard_count):
            bot_thread = Thread(target=setup_due_thread,args=(asyncio.new_event_loop(),shard_number,));
            bot_thread.start()

if __name__ == "__main__":
    print("Starting DueUtil!")
    run_due();


