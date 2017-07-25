import asyncio
import inspect
import json
import os
import queue
import re
import sys
import traceback
from threading import Thread
import aiohttp

import discord
from dueutil.permissions import Permission

import generalconfig as gconf
from dueutil import loader
from dueutil.game import players
from dueutil.game.helpers import imagehelper
from dueutil.game.configs import dueserverconfig
from dueutil import permissions
from dueutil import util, events, dbconn

MAX_RECOVERY_ATTEMPTS = 100
CARBON_BOTDATA = "https://www.carbonitex.net/discord/data/botdata.php"

stopped = False
start_time = 0
bot_key = ""
shard_count = 0
shard_clients = []
shard_names = []

""" 
DueUtil: The most 1337 (worst) discord bot ever.     
This bot is not well structured...

(c) Ben Maxwell - All rights reserved
(Sections of this bot are MIT and GPL)
"""


class DueUtilClient(discord.Client):
    """
    DueUtil shard client
    """

    def __init__(self, **details):
        self.shard_id = details["shard_id"]
        self.queue_tasks = queue.Queue()
        self.name = shard_names[self.shard_id]
        self.loaded = False
        self.session = aiohttp.ClientSession()
        super(DueUtilClient, self).__init__(**details)
        asyncio.ensure_future(self.__check_task_queue(), loop=self.loop)

    @asyncio.coroutine
    def __check_task_queue(self):

        while True:
            try:
                task_details = self.queue_tasks.get(False)
                task = task_details["task"]
                args = task_details.get('args', ())
                kwargs = task_details.get('kwargs', {})
                if inspect.iscoroutinefunction(task):
                    yield from task(*args, **kwargs)
                else:
                    task(args, kwargs)
            except queue.Empty:
                pass
            yield from asyncio.sleep(0.1)

    def run_task(self, task, *args, **kwargs):

        """
        Runs a task from within this clients thread
        """
        self.queue_tasks.put({"task": task, "args": args, "kwargs": kwargs})

    async def carbon_stats_update(self):

        headers = {'content-type': 'application/json'}
        server_count = util.get_server_count()
        carbon_payload = {"key": config["carbonKey"], "servercount": server_count}
        async with self.session.post(CARBON_BOTDATA, data=json.dumps(carbon_payload), headers=headers) as response:
            util.logger.info("Carbon returned %s status for the payload %s" % (response.status, carbon_payload))

    @asyncio.coroutine
    def on_server_join(self, server):
        server_count = util.get_server_count()
        if server_count % 1000 == 0:
            # Announce every 100 servers (for now)
            yield from util.say(gconf.announcement_channel,
                                ":confetti_ball: I'm on __**%d SERVERS**__ now!!!1111" % server_count)

        util.logger.info("Joined server name: %s id: %s", server.name, server.id)

        if not any(role.name == "Due Commander" for role in server.roles):
            yield from self.create_role(server, name="Due Commander", color=discord.Color(16038978))

        server_stats = self.server_stats(server)
        yield from util.duelogger.info(("DueUtil has joined the server **"
                                        + util.ultra_escape_string(server.name) + "**!\n"
                                        + "``Member count →`` " + str(server_stats["member_count"]) + "\n"
                                        + "``Bot members →``" + str(server_stats["bot_count"]) + "\n"
                                        + ("**BOT SERVER**" if server_stats["bot_server"] else "")))

        # Message to help out new server admins.
        yield from self.send_message(server.default_channel, ":wave: __Thanks for adding me!__\n"
                                     + "If you would like to customize me to fit your "
                                     + "server take a quick look at the admins "
                                     + "guide at <https://dueutil.tech/howto/#adming>.\n"
                                     + "It shows how to change the command prefix here, and set which "
                                     + "channels I or my commands can be used in (along with a bunch of other stuff).")
        # Update carbon stats
        yield from self.carbon_stats_update()

    @staticmethod
    def server_stats(server):
        member_count = len(server.members)
        bot_count = sum(member.bot for member in server.members)
        bot_percent = int((bot_count / member_count) * 100)
        bot_server = bot_percent > 70
        return {"member_count": member_count, "bot_percent": bot_percent,
                "bot_count": bot_count, "bot_server": bot_server}

    @asyncio.coroutine
    def on_error(self, event, *args):
        ctx = args[0] if len(args) == 1 else None
        ctx_is_message = isinstance(ctx, discord.Message)
        error = sys.exc_info()[1]
        if ctx is None:
            yield from util.duelogger.error(("**DueUtil experienced an error!**\n"
                                             + "__Stack trace:__ ```" + traceback.format_exc() + "```"))
            util.logger.error("None message/command error: %s", error)
        elif isinstance(error, util.DueUtilException):
            if error.channel is not None:
                yield from self.send_message(error.channel, error.get_message())
            else:
                yield from self.send_message(ctx.channel, error.get_message())
            return
        elif isinstance(error, util.DueReloadException):
            loader.reload_modules()
            yield from util.say(error.channel, loader.get_loaded_modules())
            return
        elif isinstance(error, discord.Forbidden):
            if ctx_is_message:
                self.send_message(ctx.channel, ("I'm missing my required permissions in this channel!"
                                                + "\n If you don't want me in this channel do ``!shutupdue all``"))
        elif isinstance(error, discord.HTTPException):
            util.logger.error("Discord HTTP error: %s", error)
        elif ctx_is_message:
            yield from self.send_message(ctx.channel, (":bangbang: **Something went wrong...**"))
            trigger_message = discord.Embed(title="Trigger", type="rich", color=gconf.EMBED_COLOUR)
            trigger_message.add_field(name="Message", value=ctx.author.mention + ":\n" + ctx.content)
            yield from util.duelogger.error(("**Message/command triggred error!**\n"
                                             + "__Stack trace:__ ```" + traceback.format_exc()[-1500:] + "```"),
                                            embed=trigger_message)
        traceback.print_exc()

    @asyncio.coroutine
    def on_message(self, message):
        if (message.author == self.user
            or message.channel.is_private
            or message.author.bot
                or not loaded()):
            return

        if message.content.startswith(self.user.mention):
            message.content = re.sub(self.user.mention + "\s*",
                                     dueserverconfig.server_cmd_key(message.server),
                                     message.content)
        yield from events.on_message_event(message)

    @asyncio.coroutine
    def on_member_update(self, before, after):
        player = players.find_player(before.id)
        if player is not None:
            old_image = player.get_avatar_url(member=before)
            new_image = player.get_avatar_url(member=after)
            if old_image != new_image:
                imagehelper.delete_cached_image(old_image)

    @asyncio.coroutine
    def on_server_remove(self, server):
        for collection in dbconn.db.collection_names():
            if collection != "Player":
                dbconn.db[collection].delete_many({'_id': {'$regex': '%s.*' % server.id}})
                dbconn.db[collection].delete_many({'_id': server.id})
        yield from util.duelogger.info("DueUtil been removed from the server **%s**"
                                       % util.ultra_escape_string(server.name))
        # Update carbon stats
        yield from self.carbon_stats_update()

    @asyncio.coroutine
    def change_avatar(self, channel, avatar_name):
        try:
            avatar = open("avatars/" + avatar_name.strip(), "rb")
            avatar_object = avatar.read()
            yield from self.edit_profile(avatar=avatar_object)
            yield from self.send_message(channel, ":white_check_mark: Avatar now **" + avatar_name + "**!")
        except FileNotFoundError:
            yield from self.send_message(channel, ":bangbang: **Avatar change failed!**")

    @asyncio.coroutine
    def on_ready(self):
        shard_number = shard_clients.index(self) + 1
        help_status = discord.Game()
        help_status.name = "dueutil.tech | shard " + str(shard_number) + "/" + str(shard_count)
        yield from self.change_presence(game=help_status, afk=False)
        util.logger.info("\nLogged in shard %d as\n%s\nWith account @%s ID:%s \n-------",
                         shard_number, self.name, self.user.name, self.user.id)
        self.__set_log_channels()
        self.loaded = True
        if loaded():
            yield from util.duelogger.bot("DueUtil has *(re)*started\n"
                                          + "Bot version → ``%s``" % gconf.VERSION)

    def __set_log_channels(self):

        """
        Setup the logging channels as the bot loads
        """

        channel = self.get_channel(config["logChannel"])
        if channel is not None:
            gconf.log_channel = channel
        channel = self.get_channel(config["errorChannel"])
        if channel is not None:
            gconf.error_channel = channel
        channel = self.get_channel(config["feedbackChannel"])
        if channel is not None:
            gconf.feedback_channel = channel
        channel = self.get_channel(config["bugChannel"])
        if channel is not None:
            gconf.bug_channel = channel
        channel = self.get_channel(config["announcementsChannel"])
        if channel is not None:
            gconf.announcement_channel = channel


class ShardThread(Thread):
    """
    Thread for a shard client
    """

    def __init__(self, event_loop, shard_number):
        self.event_loop = event_loop
        self.shard_number = shard_number
        super().__init__()

    def run(self, level=1):
        asyncio.set_event_loop(self.event_loop)
        client = DueUtilClient(shard_id=self.shard_number, shard_count=shard_count)
        shard_clients.append(client)
        try:
            asyncio.run_coroutine_threadsafe(client.run(bot_key), client.loop)
        except Exception as client_exception:
            util.logger.exception(client_exception, exc_info=True)
            if level < MAX_RECOVERY_ATTEMPTS:
                util.logger.warning("Bot recovery attempted for shard %d" % self.shard_number)
                shard_clients.remove(client)
                self.event_loop = asyncio.new_event_loop()
                self.run(level + 1)
            else:
                util.logger.critical("FATAL ERROR: Shard down! Recovery failed")
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
    if not os.path.exists("assets/imagecache/"):
        os.makedirs("assets/imagecache/")
    if not stopped:
        for shard_number in range(0, shard_count):
            loaded_clients = len(shard_clients)
            shard_thread = ShardThread(asyncio.new_event_loop(), shard_number)
            shard_thread.start()
            while len(shard_clients) <= loaded_clients:
                pass
        while not loaded():
            pass
        loader.load_modules()
        ### Prune players - task
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(players.players.prune_task(), loop=loop)
        loop.run_forever()


def loaded():
    return all(client.loaded for client in shard_clients)


if __name__ == "__main__":
    config = load_config()
    bot_key = config["botToken"]
    shard_count = config["shardCount"]
    shard_names = config["shardNames"]
    owner = discord.Member(user={"id": config["owner"]})
    if not permissions.has_permission(owner, Permission.DUEUTIL_ADMIN):
        permissions.give_permission(owner, Permission.DUEUTIL_ADMIN)
    util.load(shard_clients)
    util.logger.info("Starting DueUtil!")
    run_due()
