import json
import jsonpickle
from pymongo import MongoClient

db = None
config = {}

def conn():
    global db
    if db == None:
        client = MongoClient(config['host'])
        client.admin.authenticate(config['user'], config['pwd'], mechanism='SCRAM-SHA-1')
        uri = "mongodb://"+config['user']+":"+config['pwd']+"@"+config['host']+"/admin?authMechanism=SCRAM-SHA-1"
        db = MongoClient(uri).dueutil
        # client.drop_database('dueutil')
        return db
    else:
        return db

def insert_object(id,object):
    if id.strip() == "":
        return
    conn()[type(object).__name__].update({'_id':id},{"$set": {'data':jsonpickle.encode(object)}},upsert=True)

def get_collection_for_object(object_class):
    return conn()[object_class.__name__]

def load_config():
    global config
    with open('dbconfig.json') as config_file:  
        config = json.load(config_file)

load_config()
