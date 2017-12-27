import json
import jsonpickle
from pymongo import MongoClient

db = None
config = {}


def conn():
    global db
    if db is None:
        client = MongoClient(config['host'])
        client.admin.authenticate(config['user'], config['pwd'], mechanism='SCRAM-SHA-1')
        uri = "mongodb://" + config['user'] + ":" + config['pwd'] + "@" + config[
            'host'] + "/admin?authMechanism=SCRAM-SHA-1"
        db = MongoClient(uri).dueutil
        # client.drop_database('dueutil')
        return db
    else:
        return db


def insert_object(id, pickleable_object):
    if id.strip() == "":
        return
    #todo
    # jsonpickle_data = json.loads(jsonpickle.encode(pickleable_object))
    conn()[type(pickleable_object).__name__].update({'_id': id},
                                                    {"$set": {'data': jsonpickle.encode(pickleable_object)}},
                                                    upsert=True)


def drop_and_insert(collection, data):
    connection = conn()
    connection.drop_collection(collection)
    connection[collection].insert_one(data)


def get_collection_for_object(object_class):
    return conn()[object_class.__name__]


def delete_objects(object_class, id_pattern):
    return conn()[object_class.__name__].delete_many({'_id': {'$regex': id_pattern}})


def _load_config():
    global config
    with open('dbconfig.json') as config_file:
        config = json.load(config_file)


_load_config()
