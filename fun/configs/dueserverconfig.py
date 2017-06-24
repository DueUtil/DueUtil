from botstuff import dbconn
from ..helpers.misc import DueMap

muted_channels = DueMap()
command_whitelist = DueMap()
server_keys = dict()
DEFAULT_SERVER_KEY = "!"

"""
General config for a particular server
"""


def update_server_config(server, **update):
    dbconn.conn()["serverconfigs"].update({'_id': server.id}, {"$set": update}, upsert=True)


def mute_level(channel):
    key = channel.server.id + '/' + channel.id
    if key in muted_channels:
        return muted_channels[key]
    return -1


def whitelisted_commands(channel):
    key = channel.server.id + '/' + channel.id
    if key in command_whitelist:
        return command_whitelist[key]


def set_command_whitelist(channel, command_list):
    global command_whitelist
    key = channel.server.id + '/' + channel.id
    if len(command_list) != 0:
        command_whitelist[key] = command_list
    elif key in command_whitelist:
        del command_whitelist[key]
    update_server_config(channel.server, **{"command_whitelist": command_whitelist[channel.server]})


def mute_channel(channel, **options):
    global muted_channels
    key = channel.server.id + '/' + channel.id
    prior_mute_level = mute_level(channel)
    new_level = options.get('mute_all', False)
    if prior_mute_level != new_level:
        muted_channels[key] = new_level
        update_server_config(channel.server, **{"muted_channels": muted_channels[channel.server]})
        return True
    return False


def unmute_channel(channel):
    global muted_channels
    key = channel.server.id + '/' + channel.id
    if key in muted_channels:
        del muted_channels[key]
        update_server_config(channel.server, **{"muted_channels": muted_channels[channel.server]})
        return True
    return False


def server_cmd_key(server, *args):
    global server_keys
    if len(args) == 1:
        server_keys[server.id] = args[0]
        update_server_config(server, **{"server_key": args[0]})
    else:
        if server.id in server_keys:
            return server_keys[server.id]
        else:
            return DEFAULT_SERVER_KEY


def _load():
    global server_keys, muted_channels
    configs = dbconn.conn()["serverconfigs"].find()
    for config in configs:
        server_id = config["_id"]
        if "server_key" in config:
            server_keys[server_id] = config["server_key"]
        if "muted_channels" in config:
            muted_channels[server_id] = config["muted_channels"]
        if "command_whitelist" in config:
            command_whitelist[server_id] = config["command_whitelist"]


_load()
