import json
from botstuff import util

awards = dict()

class Award:

    def __init__(self,icon_path,name,description):
        self.name = name
        self.description = description
        self.icon = Image.open(icon_path)
        
def get_award(award_id):
    if award_id in awards:
        return awards[award_id]
    else:
        return None

def load():
    global awards
    with open('fun/awards.json') as awards_file:  
        awards_json = json.load(awards_file)
    awards = awards_json["awards"].items()
    
async def give_award(channel, player, award_id, text):
    if awards.get_award(award_id) != None:
        player.awards.append(award_id)
        player.save()
        if not channel.is_private: #or not (message.server.id+"/"+message.channel.id in util.mutedchan):
            await util.say(channel, "**"+player.name+"** :trophy: **Award!** " + text)
    
load()
