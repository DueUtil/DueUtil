import discord
import math
from datetime import datetime
import repoze.timeago
from fun import imagehelper, awards, leaderboards
import fun.players, fun.weapons, fun.quests
from botstuff import util,commands
import botstuff.permissions
from botstuff.permissions import Permission

@commands.command(args_pattern="S*")
async def test(ctx,*args,**details): 
    
    """A test command"""
    
    # print(args[0].__dict__)
    # args[0].save()
    # await imagehelper.test(ctx.channel)
    await util.say(ctx.channel,("Yo!!! What up dis be my test command fo show.\n"
                                    "I got deedz args ```"+str(args)+"```!"))
   
@commands.command(hidden = True,args_pattern=None)
async def permissions(ctx,*args,**details):
  
    """
    [CMD_KEY]permissions
    
    A debug command for the permissions system.
    Why the fuck am I writing help entries for these hidden commands?
    
    Nobody will find the command that gives you god mode & 10 Trillion Billion moneyz
    
    """
    
    permissions_report = ""
    for permission in botstuff.permissions.permissions:
        permissions_report += ("``"+permission.value[1]+"`` → "
                               + (":white_check_mark:" if botstuff.permissions.has_permission(ctx.author,permission) else ":no_entry:")+"\n")
    await util.say(ctx.channel,permissions_report)

@commands.command(args_pattern="RR")
async def add(ctx,*args,**details):
  
    """
    [CMD_KEY]add (number) (number)
    
    One of the first test commands for Due2
    I keep it for sentimental reasons
    
    """
    
    first_number = args[0]
    second_number = args[1]
    result = first_number + second_number
    await util.say(ctx.channel,"Is "+str(result))
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="S")
async def dueeval(ctx,*args,**details):

    """
    For 1337 haxors only! Go away!
    """
    players = fun.players
    weapons = fun.weapons
    quests = fun.quests
    
    player = details["author"]
    await util.say(ctx.channel,":ferris_wheel: Eval...\n"
    "**Result** ```"+str(eval(args[0]))+"```")
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="PC")
async def setpermlevel(ctx,*args,**details):
    player = args[0]
    member = discord.Member(user={"id":player.id})
    permission_index = args[1] - 1
    permissions = botstuff.permissions.permissions
    if permission_index < len(permissions):
        permission = permissions[permission_index]
        botstuff.permissions.give_permission(member,permission)
        await util.say(ctx.channel,"**"+player.name_clean+"** permission level set to ``"+permission.value[1]+"``.")
        if permission == Permission.DUEUTIL_MOD:
            await awards.give_award(ctx.channel,player,"Mod","Become an mod!")
        elif "Mod" in player.awards:
            player.awards.remove("Mod")
        if permission == Permission.DUEUTIL_ADMIN:
            await awards.give_award(ctx.channel,player,"Admin","Become an admin!")
        elif "Admin" in player.awards:
            player.awards.remove("Admin")
    else:
        raise util.DueUtilException(ctx.channel,"Permission not found")
  
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="P")
async def ban(ctx,*args,**details):
    player = args[0]
    member = discord.Member(user={"id":player.id})
    botstuff.permissions.give_permission(member,Permission.BANNED)
    await util.say(ctx.channel,":hammer: **"+player.name_clean+"** banned!")
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="P")
async def unban(ctx,*args,**details):
    player = args[0]
    member = discord.Member(user={"id":player.id})
    botstuff.permissions.give_permission(member,Permission.ANYONE)
    await util.say(ctx.channel,":unicorn: **"+player.name_clean+"** has been unbanned!")
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern=None)
async def duereload(ctx,*args,**details):
    await util.say(ctx.channel,":ferris_wheel: Reloading DueUtil modules!")
    raise util.DueReloadException(ctx.channel)

@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="PI")
async def givecash(ctx,*args,**details):
    player = args[0]
    amount = args[1]
    player.money += amount
    amount_str = util.format_number(abs(amount),money = True, full_precision = True)
    if amount >= 0:
        await util.say(ctx.channel,"Added ``"+amount_str+"`` to **"+player.get_name_possession_clean()+"** account!")
    else:
        await util.say(ctx.channel,"Subtracted ``"+amount_str+"`` from **"+player.get_name_possession_clean()+"** account!")
    player.save()

@commands.command(args_pattern="C?")
async def leaderboard(ctx,*args,**details):
    
    """
    [CMD_KEY]leaderboard (page)
    
    The global leaderboard of DueUtil!
    
    The leaderboard updated every hour.
    
    Bet someone's gonna whine about there not being a server leaderboard now.
    Don't worry I'll add one if there is demand.
    
    """
    
    page_size = 10
    page = 0

    leaderboard_embed = discord.Embed(title="DueUtil Leaderboard",type="rich",color=16038978)

    player_leaderboard = leaderboards.get_leaderboard("levels")
    if player_leaderboard != None:
      
        leaderboard_data = player_leaderboard[0]
        
        if len(args) == 1:
            page = args[0] - 1
        if page > 0:
            leaderboard_embed.title += ": Page "+str(page+1)
        if page * page_size >= len(leaderboard_data):
            raise util.DueUtilException(ctx.channel,"Page not found")

        index = 0
        for index in range(page_size * page,page_size * page + page_size):
            if index >= len(leaderboard_data):
              break
            bonus = ""
            if index == 0:
                bonus = "     :first_place:"
            elif index == 1:
                bonus = "     :second_place:"
            elif index == 2:
                bonus = "     :third_place:"
            player = leaderboard_data[index]
            name = player.name_clean
            player_id = "<@"+player.id+">"
            level = str(math.trunc(player.level))
            leaderboard_embed.add_field(name = "#"+str(index+1)+bonus,value = name+" "+player_id+" ``Level "+level+"``",inline=False)
            last_updated = datetime.utcfromtimestamp(leaderboards.last_leaderboard_update)
            leaderboard_embed.set_footer(text="Leaderboard calculated "+repoze.timeago.get_elapsed(last_updated))
        if index < len(leaderboard_data) - 1:
            leaderboard_embed.add_field(name = "+"+str(len(leaderboard_data)-(page_size*(page+1)))+" more!",
                                        value = "Do ``"+details["cmd_key"]+"leaderboard "+str(page+2)+"`` for the next page!",inline=False)
    else:
        leaderboard_embed.set_image(url="http://i.imgur.com/KQd9EJ9.gif")
        leaderboard_embed.add_field(name="Sorry",value=("The leaderboard has yet to be calculated!\n"
                                                        +"Check again soon!"))
    await util.say(ctx.channel,embed=leaderboard_embed)

@commands.command(args_pattern=None)
async def myrank(ctx,*args,**details):
  
    """
    [CMD_KEY]myrank
    
    Tells you where you are in the [CMD_KEY]leaderboard. 
    """
    
    player = details["author"]
    try:
        leaderboard_data = leaderboards.get_leaderboard("levels")[0]
        position = leaderboard_data.index(player)
        page = position//10
        await util.say(ctx.channel,(":sparkles: You're position **"+str(position+1)+"** on the leaderboard!\n"
                                   +"That's on page "+str(page+1)+"!"))
    except:
        await util.say(ctx.channel,(":confounded: I can't find you in the leaderboard!?\n"
                                    +"This probably means you're new and leaderboard has not updated yet!"))

