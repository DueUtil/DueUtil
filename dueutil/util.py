import asyncio
import io
import logging
import math
import time
from itertools import chain

import aiohttp
import discord
import emoji  # The emoji list in this is outdated/not complete.

import generalconfig as gconf
from .trello import TrelloClient

"""
A random jumble of classes & functions that are some how
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
    def __init__(self, message):
        super().__init__(message)


class DueUtilException(BotException):
    def __init__(self, channel, message, **kwargs):
        self.message = message
        self.channel = channel
        self.additional_info = kwargs.get('additional_info', "")

    def get_message(self):
        message = ":bangbang: **" + self.message + "**"
        if self.additional_info != "":
            message += "```css\n" + self.additional_info + "```"
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
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
    if type(channel) is str:
        # Server/Channel id
        server_id, channel_id = channel.split("/")
        channel = get_server(server_id).get_channel(channel_id)
    if "client" in kwargs:
        client = kwargs["client"]
        del kwargs["client"]
    else:
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


def get_server(server_id):
    return get_client(server_id).get_server(server_id)


def ultra_escape_string(string):

    """
    A simple function to escape all discord crap!
    """

    if not isinstance(string, str):
        return string  # Dick move not to raise a ValueError here.
    escaped_string = string
    escaped = []
    for character in string:
        if not character.isalnum() and not character.isspace() and character not in escaped:
            escaped.append(character)
            escaped_string = escaped_string.replace(character, '\\' + character)

    # Escape the ultra annoying mentions that \@everyone does not block
    # Why? Idk
    escaped_string = escaped_string.replace("@everyone", u"@\u200Beveryone")\
                                   .replace("@here", u"@\u200Bhere")

    return escaped_string


def format_number(number, **kwargs):

    def small_format():
        nonlocal number
        full_number = '{:,f}'.format(number).rstrip('0').rstrip('.')
        return full_number if len(full_number) < 27 else '{:,g}'.format(number)

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
        except IndexError:
            string = " Fucktonillion"
        number = int(number * 100) / float(100)
        formatted_number = '{0:g}'.format(number)
        return formatted_number + string if len(formatted_number) < 17 else str(math.trunc(number)) + string

    if number >= 1000000 and not kwargs.get('full_precision', False):
        formatted = really_large_format()
    else:
        formatted = small_format()
    return formatted if not kwargs.get('money', False) else '¤' + formatted


def format_money(amount):
    return format_number(amount, money=True, full_precision=True)


def format_number_precise(number):
    return format_number(number, full_precision=True)


def char_is_emoji(character):
    if len(character) > 1:
        return False
    emojize = emoji.emojize(character, use_aliases=True)
    demojize = emoji.demojize(emojize)
    return emojize != demojize


def is_server_emoji(server, possible_emoji):
    possible_emojis = [str(custom_emoji) for custom_emoji in server.emojis if str(custom_emoji) in possible_emoji]
    return len(possible_emojis) == 1 and possible_emojis[0] == possible_emoji


def get_server_name(server, user_id):
    try:
        return server.get_member(user_id).name
    except AttributeError:
        return "Unknown User"


def clamp(number, min_val, max_val):
    return max(min(max_val, number), min_val)


def normalize(number, min_val, max_val):
    return (number - min_val)/(max_val - min_val)


def filter_string(string: str) -> str:
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


SUFFIXES = {1: "st", 2: "nd", 3: "rd", 4: "th"}


def int_to_ordinal(number: int) -> str:
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = SUFFIXES.get(number % 10, "th")
    return str(number) + suffix

# Simple time formatter based on "Mr. B" - https://stackoverflow.com/a/24542445
intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{:d} {}".format(int(value), name))
    return ', '.join(result[:granularity])
