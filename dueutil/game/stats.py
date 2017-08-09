from enum import Enum
from collections import defaultdict
from typing import Dict

from .. import dbconn

"""
General game stats
"""


class Stat(Enum):
    MONEY_CREATED = "moneycreated"
    MONEY_TRANSFERRED = "moneytransferred"
    PLAYERS_LEVELED = "playersleveled"
    NEW_PLAYERS_JOINED = "newusers"
    QUESTS_GIVEN = "questsgiven"
    QUESTS_ATTEMPTED = "questsattempted"
    IMAGES_SERVED = "imagesserved"
    DISCOIN_RECEIVED = "discoinreceived"


def increment_stat(dueutil_stat: Stat, increment=1):
    dbconn.conn()["stats"].update({"stat": dueutil_stat.value},
                                  {"$inc": {"count": increment}}, upsert=True)


def get_stats() -> Dict[Stat, int]:
    stats_response = dbconn.conn()["stats"].find()
    stats = dict((Stat(stat["stat"]), stat["count"]) for stat in stats_response)
    return defaultdict(int, stats)
