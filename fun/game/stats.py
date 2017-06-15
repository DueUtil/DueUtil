from enum import Enum
from botstuff import dbconn

class Stat(Enum):
    MONEY_CREATED = "moneycreated"
    MONEY_TRANSFERRED = "moneytransferred"
    PLAYERS_LEVELED = "playersleveled"
    NEW_PLAYERS_JOINED = "newusers"
    QUESTS_GIVEN = "questsgiven"
    QUESTS_ATTEMPTED = "questsattempted"
    IMAGES_SERVED = "imagesserved"

def increment_stat(dueutil_stat, increment = 1):
    dbconn.conn()["stats"].update({"stat" : dueutil_stat.value},
                                  { "$inc" : { "count" : increment } }, upsert=True)
    
def get_stats():
    stats_response = dbconn.conn()["stats"].find()
    return dict((stat["stat"], stat["count"]) for stat in stats_response)
