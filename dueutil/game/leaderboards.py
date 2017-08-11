import threading
import time

from .. import events, util, dbconn
from ..game import players
from collections import namedtuple
from cachetools.func import ttl_cache

leaderboards = dict()
last_leaderboard_update = 0
UPDATE_INTERVAL = 3600

_LocalLeaderboard = namedtuple("LocalLeaderboard", ["updated", "data"])


def calculate_player_rankings(rank_name, sort_function, reverse=True):
    global leaderboards
    leaderboards[rank_name] = (sorted(players.players.values(),
                                      key=sort_function, reverse=reverse), sort_function, reverse)
    db = dbconn.conn()
    db.drop_collection(rank_name)
    for rank, player in enumerate(leaderboards[rank_name][0]):
        db[rank_name].insert({"rank": rank+1, "player_id": player.id})


def calculate_level_leaderboard():
    calculate_player_rankings("levels", lambda player: player.total_exp)


def get_leaderboard(rank_name):
    if rank_name in leaderboards:
        return leaderboards[rank_name][0]


@ttl_cache(maxsize=32, ttl=3600)
def get_local_leaderboard(server, rank_name):
    rankings = get_leaderboard(rank_name)
    if rankings is not None:
        rankings = list(filter(lambda player: server.get_member(player.id) is not None, rankings))
        return _LocalLeaderboard(updated=last_leaderboard_update, data=rankings)


def get_rank(player, rank_name, server=None):
    if server is not None:
        # Local
        rankings = get_local_leaderboard(server, rank_name).data
    else:
        rankings = get_leaderboard(rank_name)
    try:
        return rankings.index(player) + 1
    except (ValueError, IndexError):
        return -1


async def update_leaderboards(_):
    global last_leaderboard_update
    if time.time() - last_leaderboard_update >= UPDATE_INTERVAL:
        last_leaderboard_update = time.time()
        leaderboard_thread = threading.Thread(target=calculate_updates)
        leaderboard_thread.start()
        await util.duelogger.info("Global leaderboard updated!")


def calculate_updates():
    for rank_name, data in leaderboards.items():
        calculate_player_rankings(rank_name, data[1], data[2])


events.register_message_listener(update_leaderboards)
calculate_level_leaderboard()
