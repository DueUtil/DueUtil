import json
from PIL import Image
from fun import dueserverconfig
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

def load():
    global awards
    with open('fun/configs/awards.json') as awards_file:  
        awards_json = json.load(awards_file)
    for award_id, award in awards_json["awards"].items():
        awards[award_id] = Award(award["icon"],award["name"],award.get('message',"???"))
    
async def give_award(channel, player, award_id, text):
    if get_award(award_id) != None and award_id not in player.awards:
        player.awards.append(award_id)
        player.save()
        if not channel.is_private and dueserverconfig.mute_level(channel) < 0:
            await util.say(channel, "**"+player.name+"** :trophy: **Award!** " + text)

load()
