import discord
import generalconfig as gconf
from botstuff import util, loader, events, permissions, dbconn
from botstuff.permissions import Permission
import os
import sys
import asyncio
from threading import Thread
import queue
import json
import traceback
import inspect
import re
from fun.configs import dueserverconfig

MAX_RECOVERY_ATTEMPS = 100

stopped = False
start_time = 0
bot_key = ""
shard_count = 0
shard_clients = []
shard_names = []

""" 
DueUtil: The most 1337 (worst) discord bot ever.     
This bot is not well structured...
"""

class DueUtilClient(discord.Client):
  
    """
    DueUtil shard client
    """

    def __init__(self, *args, **kwargs):
        self.shard_id = kwargs["shard_id"]
        self.queue_tasks = queue.Queue()
        self.name = shard_names[self.shard_id]
        self.loaded = False
        super(DueUtilClient,self).__init__(*args,**kwargs)
        asyncio.ensure_future(self.__check_task_queue(), loop=self.loop)
        
    async def __check_task_queue(self):
        
        while True:
            try:
                task_details = self.queue_tasks.get(False)
                task = task_details["task"]
                args = task_details.get('args',())
                kwargs = task_details.get('kwargs',{})
                if inspect.iscoroutinefunction(task):
                    await task(*args,**kwargs)
                else:
                    task(args,kwargs)
            except queue.Empty:
                pass
            await asyncio.sleep(0.1)
            
    def run_task(self,task,*args,**kwargs):
        
        """
        Runs a task from within this clients thread
        """
        self.queue_tasks.put({"task":task,"args":args,"kwargs":kwargs})

    @asyncio.coroutine
    async def on_server_join(self,server):
        server_count = util.get_server_count()
        if server_count % 100 == 0:
            # Announce every 100 servers (for now)
            await util.say(gconf.announcement_channel,":confetti_ball: I'm on __**%d SERVERS**__ now!!!1111" % server_count)
      
        payload = {"key":'macdue0a873a71hjd673o1',"servercount":server_count}
        url = "https://www.carbonitex.net/discord/data/botdata.php"
        #reponse = await aiohttp.post(url, data=payload)
        #reponse.close()
        util.logger.info("Joined server name: %s id: %s",server.name,server.id)

        if not any(role.name == "Due Commander" for role in server.roles):
            await self.create_role(server,name="Due Commander",color=discord.Color(16038978))
            
        server_stats = self.server_stats(server)
        await util.duelogger.info(("DueUtil has joined the server **" + util.ultra_escape_string(server.name)+"**!\n"
                                  +"``Member count →`` "+str(server_stats["member_count"])+"\n"
                                  +"``Bot members →``" +str(server_stats["bot_count"])+"\n"
                                  +("**BOT SERVER**" if server_stats["bot_server"] else "")))
                                  
    def server_stats(self,server):
        member_count = len(server.members)
        bot_count = sum(member.bot for member in server.members)
        bot_percent = int((bot_count/member_count)*100)
        bot_server = bot_percent > 70
        return {"member_count":member_count,"bot_count":bot_count
                ,"bot_percent":bot_percent,"bot_server":bot_server}
    
    @asyncio.coroutine
    async def on_error(self,event,*args):
        ctx = args[0] if len(args) == 1 else None
        ctx_is_message = isinstance(ctx, discord.Message)
        error = sys.exc_info()[1]
        if ctx == None:
            await util.duelogger.error(("**DueUtil experienced an error!**\n"
                                        +"__Stack trace:__ ```"+traceback.format_exc()+"```"))
            util.logger.error("None message/command error: %s",error)
        elif isinstance(error,util.DueUtilException):
            if error.channel != None:
                await self.send_message(error.channel,error.get_message())
            else:
                await self.send_message(ctx.channel,error.get_message())
            return
        elif isinstance(error,util.DueReloadException):
            loader.reload_modules()
            await util.say(error.channel,loader.get_loaded_modules())
            return
        elif isinstance(error,discord.Forbidden):
            if ctx_is_message:
                self.send_message(ctx.channel,("I'm missing my required permissions in this channel!"
                                               +"\n If you don't want me in this channel do ``!shutupdue all``"))
        elif isinstance(error,discord.HTTPException):
            util.logger.error("Discord HTTP error: %s",error)
        elif ctx_is_message:
            await self.send_message(ctx.channel,(":bangbang: **Something went wrong...**"))
            trigger_message = discord.Embed(title="Trigger",type="rich",color=gconf.EMBED_COLOUR)
            trigger_message.add_field(name="Message",value=ctx.author.mention+":\n"+ctx.content)
            await util.duelogger.error(("**Message/command triggred error!**\n"
                                        +"__Stack trace:__ ```"+traceback.format_exc()[-1500:]+"```"),embed=trigger_message)
        traceback.print_exc()

    @asyncio.coroutine
    async def on_message(self,message):
        if (message.author == self.user 
            or message.channel.is_private 
            or message.author.bot
            or not loaded()):
            return
       
        if message.content.startswith(self.user.mention):
            message.content = re.sub(self.user.mention+"\s*",
                                     dueserverconfig.server_cmd_key(message.server),
                                     message.content)
        await events.on_message_event(message) 
        
    @asyncio.coroutine
    async def on_server_remove(self,server):
        for collection in dbconn.db.collection_names():
            if collection != "Player":
                dbconn.db[collection].delete_many({'_id':{'$regex':'%s\/.*' % server.id}})
                dbconn.db[collection].delete_many({'_id':server.id})
        await util.duelogger.info("DueUtil been removed from the server **%s**" % util.ultra_escape_string(server.name))
                                
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
        shard_number = shard_clients.index(self) +1
        help_status = discord.Game()
        help_status.name = "dueutil.tech | shard "+str(shard_number)+"/"+str(shard_count)
        await self.change_presence(game=help_status,afk=False)
        util.logger.info("\nLogged in shard %d as\n%s\nWith account @%s ID:%s \n-------",
                          shard_number,self.name,self.user.name,self.user.id)
        self.__set_log_channels()
        self.loaded = True
        if loaded():
            await util.duelogger.bot("DueUtil has *(re)*started\n"
                                     +"Bot version → ``%s``" % config["botVersion"])
        
    def __set_log_channels(self):
      
        """
        Setup the logging channels as the bot loads
        """
        
        channel = self.get_channel(config["logChannel"])
        if channel != None:
            gconf.log_channel = channel
        channel = self.get_channel(config["errorChannel"])
        if channel != None:
            gconf.error_channel = channel
        channel = self.get_channel(config["feedbackChannel"])
        if channel != None:
            gconf.feedback_channel = channel
        channel = self.get_channel(config["bugChannel"])
        if channel != None:
            gconf.bug_channel = channel
        channel = self.get_channel(config["announcementsChannel"])
        if channel != None:
            gconf.announcement_channel = channel

class ShardThread(Thread):
  
    """
    Thread for a shard client
    """
  
    def __init__(self,event_loop,shard_number):
        self.event_loop = event_loop
        self.shard_number = shard_number
        super().__init__()
        
    def run(self):
        asyncio.set_event_loop(self.event_loop)
        client = DueUtilClient(shard_id=self.shard_number,shard_count=shard_count)
        shard_clients.append(client)
        try:
            asyncio.run_coroutine_threadsafe(client.run(bot_key),client.loop)
        except:
            if level < MAX_RECOVERY_ATTEMPS:
                util.logger.warning("Bot recovery attempted for shard %d"%shard_id)
                shard_clients.remove(client)
                self.run(asyncio.new_event_loop(),shard_id,level+1)
            else:
                util.logger.critical("FALTAL ERROR: Shard down! Recovery failed")
        finally:
            util.logger.critical("Shard is down! Bot needs restarting!")
            # Should restart bot
            os._exit(1)
        
def load_config():
    try:
        with open('dueutil.json') as config_file:  
            return json.load(config_file)
    except Exception as exception:
        sys.exit("Config error! %s" % exception)

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
        for shard_number in range(0,shard_count):
            loaded_clients = len(shard_clients)
            shard_thread = ShardThread(asyncio.new_event_loop(),shard_number)
            shard_thread.start()
            while len(shard_clients) <= loaded_clients: pass   
        while not loaded(): pass
        loader.load_modules()
        
def loaded():
    return all(client.loaded for client in shard_clients)
            
if __name__ == "__main__":
    config = load_config()
    bot_key = config["botToken"]
    shard_count = config["shardCount"]
    shard_names = config["shardNames"]
    owner = discord.Member(user={"id":config["owner"]})
    if not permissions.has_permission(owner,Permission.DUEUTIL_ADMIN):
        permissions.give_permission(owner,Permission.DUEUTIL_ADMIN)
    util.load(shard_clients)
    util.logger.info("Starting DueUtil!")
    run_due()
