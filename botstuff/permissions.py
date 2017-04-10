import discord
from enum import Enum
from fun import players
from botstuff import dbconn

special_permissions = dict()

"""
DueUtil permissions
"""

class Permission(Enum):
    BANNED = (lambda member: has_special_permission(member,permissions[0]),"banned","NoInherit")
    ANYONE = (lambda member: players.find_player(member.id) != None,"anyone",)
    SERVER_ADMIN = (lambda member: (member.server_permissions.manage_server 
                                    or next((role for role in member.roles if role.name == "Due Commander"),False)),"server_admin",)
    DUEUTIL_MOD = (lambda member: has_special_permission(member,permissions[3]) ,"dueutil_mod",)
    DUEUTIL_ADMIN = (lambda member: has_special_permission(member,permissions[4]),"dueutil_admin",)
    
permissions = [permission for permission in Permission]

def has_permission(member : discord.Member,permission):
    if permission != Permission.BANNED and not has_special_permission(member,Permission.BANNED):
        if permission.value[0](member) or has_special_permission(member,permission): return True
        elif len(permission.value) < 3:
            for higher_permission in permissions[permissions.index(permission):]:
               if higher_permission.value[0](member): return True
    return False

def has_special_permission(member : discord.Member,permission):
    return member.id in special_permissions and special_permissions[member.id] == permission.value[1]
      
def give_permission(member : discord.Member,permission):
    global special_permissions
    if permission != Permission.ANYONE:
        dbconn.conn()["permissions"].update({'_id': member.id},{"$set": {'permission':permission.value[1]}},upsert=True)
        special_permissions[member.id] = permission.value[1]
    else:
        strip_permissions(member)
        
def strip_permissions(member : discord.Member):
    global special_permissions
    dbconn.conn()["permissions"].remove({'_id': member.id})
    del special_permissions[member.id]
    
def load_dueutil_roles():
    permissions = dbconn.conn()["permissions"].find()
    for permission in permissions:
        special_permissions[permission["_id"]] = permission["permission"]

load_dueutil_roles()
