import discord
import jsonpickle
import json
import math
import random 
import numpy
import emoji #The emoji list in this is outdated.
from botstuff import dbconn,util;
from PIL import Image, ImageDraw, ImageFont
from misc import DueUtilObject
import awards
        
money_created = 0
money_transferred = 0
players_leveled = 0
new_players_joined = 0
quests_given = 0
quests_attempted = 0
images_served = 0
    
def get_stats():
    return {key: value for key,
            value in Stats.__dict__.items() if not callable(key)}
        
class Misc:
    POSTIVE_BOOLS = ('true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh')
    
    @staticmethod
    def load():
        global banners
        banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png")

