import math
import logging
import emoji  # The emoji list in this is outdated/not complete.
import generalconfig as gconf
import aiohttp
import io
import time
import asyncio
import discord
from botstuff.trello import TrelloClient
from itertools import chain

"""
A random jumble of classes & functionals that are some how
utilities.

Other than that no two things in this module have much in common
"""

shard_clients = []
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dueutil')

trello_client = TrelloClient(api_key=gconf.trello_api_key,
                             api_token=gconf.trello_api_token)


class DueLog:

    @staticmethod
    async def bot(message, **kwargs):
        await say(gconf.log_channel, ":robot: %s" % message, **kwargs)

    @staticmethod
    async def info(message, **kwargs):
        await say(gconf.log_channel, ":grey_exclamation: %s" % message, **kwargs)

    @staticmethod
    async def concern(message, **kwargs):
        await say(gconf.log_channel, ":warning: %s" % message, **kwargs)

    @staticmethod
    async def error(message, **kwargs):
        await say(gconf.error_channel, ":bangbang: %s" % message, **kwargs)


duelogger = DueLog()


class BotException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DueUtilException(BotException):
    def __init__(self, channel, message, *args, **kwargs):
        self.message = message
        self.channel = channel
        self.addtional_info = kwargs.get('addtional_info', "")

    def get_message(self):
        message = ":bangbang: **" + self.message + "**"
        if self.addtional_info != "":
            message += "```css\n" + self.addtional_info + "```"
        return message


class DueReloadException(BotException):
    def __init__(self, result_channel):
        self.channel = result_channel


class SlotPickleMixin:
    """
    Mixin for pickling slots
    MIT - http://code.activestate.com/recipes/578433-mixin-for-pickling-objects-with-__slots__/
    ^ Fuck this utter shite is WRONG and does not account for slot inherits
    """

    def __getstate__(self):
        all_slots = chain.from_iterable(getattr(cls, '__slots__', []) for cls in self.__class__.__mro__)
        return dict(
            (slot, getattr(self, slot))
            for slot in all_slots
            if hasattr(self, slot)
        )

    def __setstate__(self, state):
        for slot, value in state.items():
            setattr(self, slot, value)


async def download_file(url):
    with aiohttp.Timeout(10):
        async with aiohttp.get(url) as response:
            file_data = io.BytesIO()
            while True:
                chunk = await response.content.read(128)
                if not chunk:
                    break
                file_data.write(chunk)
            response.release()
            file_data.seek(0)
            return file_data


async def say(channel, *args, **kwargs):
    client = get_client(channel.server.id)
    if asyncio.get_event_loop() != client.loop:
        # Allows it to speak across shards
        client.run_task(say, *((channel,) + args), **kwargs)
    else:
        await client.send_message(channel, *args, **kwargs)


async def typing(channel):
    await get_client(channel.server.id).send_typing(channel)


def load_and_update(reference, bot_object):
    for item in dir(reference):
        if item not in dir(bot_object):
            setattr(bot_object, item, getattr(reference, item))
    return bot_object


def get_shard_index(server_id):
    return (int(server_id) >> 22) % len(shard_clients)


def pretty_time():
    return time.strftime('%l:%M%p %Z on %b %d, %Y')


def get_server_count():
    return sum(len(client.servers) for client in shard_clients)


def get_server_id(source):
    if isinstance(source, str):
        return source
    elif hasattr(source, 'server'):
        return source.server.id
    elif isinstance(source, discord.Server):
        return source.id


def get_client(source):
    try:
        return shard_clients[get_shard_index(get_server_id(source))]
    except IndexError:
        return None


def ultra_escape_string(string):
    if not isinstance(string, str):
        return string
    escaped_string = string
    escaped = []
    for character in string:
        if not character.isalnum() and not character.isspace() and character not in escaped:
            escaped.append(character)
            escaped_string = escaped_string.replace(character, '\\' + character)
    return escaped_string


def format_number(number, **kwargs):
    def small_format():
        nonlocal number
        return '{:,g}'.format(number)

    def really_large_format():
        nonlocal number
        units = ["Million", "Billion", "Trillion", "Quadrillion", "Quintillion", "Sextillion", "Septillion",
                 "Octillion"]
        reg = len(str(math.floor(number / 1000)))
        if (reg - 1) % 3 != 0:
            reg -= (reg - 1) % 3
        number = number / pow(10, reg + 2)
        try:
            string = " " + units[math.floor(reg / 3) - 1]
        except:
            string = " Fucktonillion"
        number = int(number * 100) / float(100)
        formatted = '{0:g}'.format(number)
        return formatted + string if len(formatted) < 17 else str(math.trunc(number)) + string

    if number >= 1000000 and not kwargs.get('full_precision', False):
        formatted = really_large_format()
    else:
        formatted = small_format()
    return formatted if not kwargs.get('money', False) else '¤' + formatted


def char_is_emoji(character):
    if len(character) > 1:
        return False
    emojize = emoji.emojize(character, use_aliases=True)
    demojize = emoji.demojize(emojize)
    return emojize != demojize


def is_server_emoji(server, possible_emoji):
    possible_emojis = [str(emoji) for emoji in server.emojis if str(emoji) in possible_emoji]
    return len(possible_emojis) == 1 and possible_emojis[0] == possible_emoji


def get_server_name(server, user_id):
    try:
        return server.get_member(user_id).name
    except AttributeError:
        return "Unknown User"


def clamp(number, min_val, max_val):
    return max(min(max_val, number), min_val)


def filter_string(string):
    new = ""
    for i in range(0, len(string)):
        if 32 <= ord(string[i]) <= 126:
            new = new + string[i]
        else:
            new = new + "?"
    return new


def load(shards):
    global shard_clients
    shard_clients = shards
