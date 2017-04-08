import discord
from enum import Enum
from fun import players
from botstuff import dbconn

"""
DueUtil permissions
"""

class Permission(Enum):
    ANYONE = (lambda member: players.find_player(member.id) != None,)
    SERVER_ADMIN = (lambda member: (member.server_permissions.manage_server 
                                    or next((role for role in member.roles if role.name == "Due Commander"),False)),)
    DUEUTIL_MOD = (lambda member: False,)
    DUEUTIL_ADMIN = (lambda member: False,)

def has_permission(member : discord.Member,permission):
    return permission.value[0](member)

    
    
