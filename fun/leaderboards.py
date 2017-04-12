import threading
from fun import players
from botstuff import events
import time

leaderboards = dict()
last_leaderboard_update = 0
UPDATE_INTERVAL = 3600

def calculate_player_rankings(rank_name,sort_function):
    global leaderboards
    leaderboards[rank_name] = [sorted(players.players.values(), key=sort_function),sort_function]

def calculate_level_leaderboard():
    calculate_player_rankings("levels",lambda player: player.level)
    
def get_leaderboard(rank_name):
    if rank_name in leaderboards:
        return leaderboards[rank_name]

async def update_leaderboards(_):
    global last_leaderboard_update
    if time.time() - last_leaderboard_update >= UPDATE_INTERVAL:
        last_leaderboard_update = time.time()
        leaderboard_thread = threading.Thread(target=calculate_updates)
        leaderboard_thread.start()

def calculate_updates():
    for rank_name,data in leaderboards.items():
        calculate_player_rankings(rank_name,data[1])

events.register_message_listener(update_leaderboards)
calculate_level_leaderboard()