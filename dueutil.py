import discord
import os
import botstuff.util;
from fun import battlesquests;
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
from botstuff import events,loader,util;

last_backup = 0;
stopped = False;
start_time = 0;
shard_count = 3;
shard_clients = [];
bot_key = "MjEyNzA3MDYzMzY3ODYwMjI1.Cwk-Cg.N98twLnUL6i0VPePyzUsn1bNf-4";
shard_names = []

""" The most 1337 (worst) discord bot ever."""

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
        if isinstance(error,util.DueUtilException):
            await self.send_message(error.channel,error.get_message());
        elif isinstance(ctx, discord.Message):
            await self.send_message(ctx.channel,(":bangbang: **Something went wrong...**\n"
                                                 "``"+str(error)+"``"));
            traceback.print_exc();
        else:
            traceback.print_exc();
            
    @asyncio.coroutine
    async def on_message(self,message):
        if message.author == self.user:
            return
        await battlesquests.on_message(message);
        await events.on_command_event(message);
        #HACKER MAN 
                                
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

def is_due_loaded():
    return battlesquests.loaded and util.loaded;

def load_due():
    load_config();
    #Testing
    battlesquests.load(shard_clients);
    util.load(shard_clients);
    
def setup_due_thread(loop,shard_id):
    global shard_clients;
    asyncio.set_event_loop(loop)
    client = DueUtilClient(shard_id=shard_id,shard_count=shard_count);
    shard_clients.append(client);
    try:
        asyncio.run_coroutine_threadsafe(client.run(bot_key),client.loop);
    finally:
        print("A shard died.");

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
    return util.get_page_with_replace(data,page,key,server);


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
  if(util.is_admin(message.author.id) and message.content.lower().startswith(key+"sudo ")):
    try:
        message.author = message.server.get_member(message.raw_mentions[0]);
        message.content = content = key+message.content.split('>',1)[1].strip();
        del message.raw_mentions[0];
    except:
        await client.send_message(message.channel, ":bangbang: **sudo failed!**");
        
def run_due():
    global stopped,shard_clients;
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
        print(shard_clients);

if __name__ == "__main__":
    print("Starting DueUtil!")
    run_due();


