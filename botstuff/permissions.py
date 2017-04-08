import discord
from enum import Enum
from fun import players
from botstuff import dbconn

special_permissions = dict()

"""
DueUtil permissions
"""

class Permission(Enum):
    ANYONE = (lambda member: players.find_player(member.id) != None,"anyone",)
    SERVER_ADMIN = (lambda member: (member.server_permissions.manage_server 
                                    or next((role for role in member.roles if role.name == "Due Commander"),False)),"server_admin",)
    DUEUTIL_MOD = (lambda member: member.id in special_permissions and special_permissions[member.id] == "dueutil_mod" ,"dueutil_mod",)
    DUEUTIL_ADMIN = (lambda member: member.id in special_permissions and special_permissions[member.id] == "dueutil_admin","dueutil_admin",)
    
permissions = [permission for permission in Permission]

def has_permission(member : discord.Member,permission):
    if permission.value[0](member): return True
    else:
        for permission in permissions[permissions.index(permission):]:
           if permission.value[0](member): return True
    return False
      
def give_permission(member : discord.Member,permission):
    dbconn.conn()["permissions"].update({"member": member.id},{"permission": permission.value[1]}, upsert=True)
    
def strip_permissions(member : discord.Member):
    dbconn.conn()["permissions"].remove({"member": member.id})
    
def load_dueutil_roles():
    permissions = dbconn.conn()["permissions"].find()
    for permission in permissions:
        special_permissions[permission["member"]] = permission["permission"]
    
load_dueutil_roles()
"""

def increment_stat(dueutil_stat, increment = 1):
    dbconn.conn()["stats"].update({"stat" : dueutil_stat.value},
                                  { "$inc" : { "count" : increment } }, upsert=True)
    
def get_stats():
    stats_response = dbconn.conn()["stats"].find()
    return dict((stat["stat"], stat["count"]) for stat in stats_response)

"""
