import jsonpickle;
from pymongo import MongoClient

db = None;

def conn():
    global db;
    if db == None:
       db = MongoClient().dueutil;
       return db;
    else:
       return db;

def insert_object(id,object):
    if id.strip() == "":
        return
    conn()[type(object).__name__].update({'_id':id},{"$set": {'data':jsonpickle.encode(object)}},upsert=True)

def get_collection_for_object(object_class):
    return conn()[object_class.__name__]
