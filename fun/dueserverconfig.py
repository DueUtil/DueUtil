from botstuff import dbconn
from fun.misc import DueMap

muted_channels = DueMap()
server_keys = dict()
DEFAULT_SERVER_KEY = "!"

def update_server_config(server,**update):
    dbconn.conn()["serverconfigs"].update({'_id': server.id},
                                  {"$set": 
                                    update
                                  },
                                  upsert=True)

def is_mute(channel):
    key = channel.server.id+'/'+channel.id
    return key in muted_channels

def mute_channel(channel):
    global muted_channels
    key = channel.server.id+'/'+channel.id
    if key not in muted_channels:
        muted_channels[key] = True
        update_server_config(channel.server,**{"muted_channels":mute_channels[channel.server]})
        return True
    return False
    
def unmute_channel(channel):
    global muted_channels
    key = channel.server.id+'/'+channel.id
    if key in muted_channels:
        del muted_channels[key]
        update_server_config(channel.server,**{"muted_channels":mute_channels[channel.server]})
        return True
    return False
    
def server_cmd_key(server,*args):
    global server_keys
    if len(args) == 1:
        server_keys[server.id] = args[0]
        update_server_config(server,**{"server_key":args[0]})
    else:
        if server.id in server_keys:
            return server_keys[server.id]
        else:
            return DEFAULT_SERVER_KEY

def load():
     configs = dbconn.conn()["serverconfigs"].find()
     for config in configs:
        server_id = config["_id"]
        if "server_key" in config:
            server_keys[server_id] = config["server_key"]
        if "muted_channels" in config:
            print(config["muted_channels"])
load()
