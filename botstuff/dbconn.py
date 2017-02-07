import jsonpickle;
from pymongo import MongoClient
import json;

def conn():
    return MongoClient();

def players_collection():
    return conn().dueutil.players;
    
def quests_collection():
    return conn().dueutil.quests;
    
def weapons_collection():
    return conn().dueutil.weapons;
    

