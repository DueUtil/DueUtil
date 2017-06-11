import discord
from botstuff import util ,events, loader, permissions, dbconn
from botstuff.permissions import Permission
import os
import sys
import asyncio
from threading import Thread
import json
import traceback

MAX_RECOVERY_ATTEMPS = 100

stopped = False
start_time = 0
bot_key = ""
shard_count = 0
shard_clients = []
shard_names = []

""" The most 1337 (worst) discord bot ever."""

class DueUtilClient(discord.Client):

    def __init__(self, *args, **kwargs):
        self.shard_id = int(kwargs["shard_id"])
        self.name = shard_names[self.shard_id]
        super(DueUtilClient,self).__init__(*args,**kwargs)

    @asyncio.coroutine
    async def on_server_join(self,server):
        server_count = 0
        for client in shard_clients:
            server_count+= len(client.servers)
        payload = {"key":'macdue0a873a71hjd673o1',"servercount":server_count}
        url = "https://www.carbonitex.net/discord/data/botdata.php"
        #reponse = await aiohttp.post(url, data=payload)
        #reponse.close()
        util.logger.info("Joined server name: %s id: %s",server.name,server.id)

        if not any(role.name == "Due Commander" for role in server.roles):
            await self.create_role(server,name="Due Commander",color=discord.Color(16038978))
    
    @asyncio.coroutine
    async def on_error(self,event,*args):
        ctx = args[0] if len(args) == 1 else None
        ctx_is_message = isinstance(ctx, discord.Message)
        error = sys.exc_info()[1]
        if ctx == None:
            util.logger.error("None message/command error: %s",error)
            return
        if isinstance(error,util.DueUtilException):
            if error.channel != None:
                await self.send_message(error.channel,error.get_message())
            else:
                await self.send_message(ctx.channel,error.get_message())
        elif isinstance(error,util.DueReloadException):
            loader.reload_modules()
            await util.say(error.channel,loader.get_loaded_modules())
        elif isinstance(error,discord.Forbidden):
            if ctx_is_message:
                self.send_message(ctx.channel,("I'm missing my required permissions in this channel!"
                                               +"\n If you don't want me in this channel do ``!shutupdue all``"))
        elif isinstance(error,discord.HTTPException):
            util.logger.error("Discord HTTP error: %s",error)
        elif ctx_is_message:
            await self.send_message(ctx.channel,(":bangbang: **Something went wrong...**\n"
                                                 "``"+str(error)+"``"))
            traceback.print_exc()
        else:
            traceback.print_exc()
            
    @asyncio.coroutine
    async def on_message(self,message):
        if message.author == self.user or message.channel.is_private or message.author.bot:
            return
        await events.on_message_event(message)     
        
    @asyncio.coroutine
    async def on_server_remove(server):
        for collection in dbconn.db.collection_names():
            if collection != "Player":
                dbconn.db[collection].delete_many({'_id':{'$regex':'%s\/.*' % server.id}})
                dbconn.db[collection].delete_many({'_id':server.id})
                                
    async def change_avatar(self,channel,avatar_name):
        try:
            avatar = open("avatars/"+avatar_name.strip(),"rb")
            avatar_object = avatar.read()
            await self.edit_profile(avatar=avatar_object)
            await self.send_message(channel, ":white_check_mark: Avatar now **"+avatar_name+"**!")
        except:
            await self.send_message(channel, ":bangbang: **Avatar change failed!**")

    @asyncio.coroutine
    async def on_ready(self):
        #global start_time
        #start_time = time.time()
        shard_number = shard_clients.index(self) +1
        help_status = discord.Game()
        help_status.name = "dueutil.tech | shard "+str(shard_number)+"/"+str(shard_count)
        await self.change_presence(game=help_status,afk=False)
        util.logger.info("\nLogged in shard %d as\n%s\nWith account @%s ID:%s \n-------",
                          shard_number,self.name,self.user.name,self.user.id)

def is_due_loaded():
    return False

def load_due():
    load_config()
    util.load(shard_clients)
    
def setup_due_thread(loop,shard_id, level = 0):
    global shard_clients
    asyncio.set_event_loop(loop)
    client = DueUtilClient(shard_id=shard_id,shard_count=shard_count)
    shard_clients.append(client)
    try:
        asyncio.run_coroutine_threadsafe(client.run(bot_key),client.loop)
    except:
        if level < MAX_RECOVERY_ATTEMPS:
            util.logger.warning("Bot recovery attempted for shard %d"%shard_id)
            shard_clients.remove(client)
            setup_due_thread(asyncio.new_event_loop(),shard_id,level+1)
        else:
            util.logger.critical("FALTAL ERROR: Shard down! Recovery failed")
    finally:
        util.logger.critical("Shard is down! Bot needs restarting!")
        sys.exit("Bot crashed.")

def load_config():
    global bot_key,shard_count,shard_clients,shard_names
    try:
        with open('dueutil.json') as config_file:  
            config = json.load(config_file)
        bot_key = config["botToken"]
        shard_count = config["shardCount"]
        shard_names = config["shardNames"]
        owner = discord.Member(user={"id":config["owner"]})
        if not permissions.has_permission(owner,Permission.DUEUTIL_ADMIN):
            permissions.give_permission(owner,Permission.DUEUTIL_ADMIN)
    except:
        sys.exit("Config file missing!")

def run_due():
    global stopped,shard_clients
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
    if not stopped:
        if not is_due_loaded():
            load_due()
        for shard_number in range(0,shard_count):
            loaded_clients = len(shard_clients)
            bot_thread = Thread(target=setup_due_thread,args=(asyncio.new_event_loop(),shard_number,))
            bot_thread.start()
            while len(shard_clients) <= loaded_clients:
                pass
            
if __name__ == "__main__":
    util.logger.info("Starting DueUtil!")
    run_due()
