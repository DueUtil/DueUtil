import discord
import math
from datetime import datetime
import repoze.timeago
from fun import awards
from fun import leaderboards
import fun.players, fun.weapons, fun.quests
from botstuff import util,commands,events
import botstuff.permissions
from botstuff.permissions import Permission
import generalconfig as gconf 
import subprocess
import os

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
    fun.players
    fun.weapons
    fun.quests
    
    details["author"]
    await util.say(ctx.channel,":ferris_wheel: Eval...\n"
    "**Result** ```"+str(eval(args[0]))+"```")
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="PS")
async def sudo(ctx,*args,**details):
    
    """
    [CMD_KEY]sudo victim command
    
    Infect a victims mind to make them run any command you like!
    """
    
    try:
        victim = args[0]
        ctx.author = ctx.server.get_member(victim.id)
        ctx.content = args[1]
        await util.say(ctx.channel,":smiling_imp: Sudoing **"+victim.name_clean+"**!")
        await events.command_event(ctx)
    except:
        raise util.DueUtilException(ctx.channel,"Sudo failed!")
    
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
            await util.duelogger.info("**%s** is now a DueUtil mod!" % player.name_clean)
        elif "Mod" in player.awards:
            player.awards.remove("Mod")
        if permission == Permission.DUEUTIL_ADMIN:
            await awards.give_award(ctx.channel,player,"Admin","Become an admin!")
            await util.duelogger.info("**%s** is now a DueUtil admin!" % player.name_clean)
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
    await util.duelogger.concern("**%s** has been banned!" % player.name_clean)
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="P")
async def unban(ctx,*args,**details):
    player = args[0]
    member = discord.Member(user={"id":player.id})
    botstuff.permissions.give_permission(member,Permission.ANYONE)
    await util.say(ctx.channel,":unicorn: **"+player.name_clean+"** has been unbanned!")
    await util.duelogger.info("**%s** has been unbanned" % player.name_clean)
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="P")
async def toggledonor(ctx,*args,**details):
    player = args[0]
    player.donor = not player.donor
    if player.donor:
        await util.say(ctx.channel,"**"+player.name_clean+"** is now a donor!")
    else:
        await util.say(ctx.channel,"**"+player.name_clean+"** is nolonger donor")

@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern=None)
async def duereload(ctx,*args,**details):
    await util.say(ctx.channel,":ferris_wheel: Reloading DueUtil modules!")
    await util.duelogger.concern("DueUtil Reloading!")
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

@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern=None)
async def updateleaderboard(ctx,*args,**details):
    leaderboards.last_leaderboard_update = 0
    await leaderboards.update_leaderboards(ctx)
    await util.say(ctx.channel,":ferris_wheel: Updating leaderboard!")
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern=None)
async def updatebot(ctx,*args,**details):
      
    """
    [CMD_KEY]updatebot
    
    Updates DueUtil
    
    """
    
    try:
        update_result = subprocess.check_output(['bash', 'update_script.sh'])
    except subprocess.CalledProcessError as updateexc:
        update_result = updateexc.output
    update_result = update_result.decode("utf-8")
    if len(update_result.strip()) == 0:
        update_result = "No output."
    update_embed = discord.Embed(title=":gear: Updating DueUtil!",type="rich",color=gconf.EMBED_COLOUR)
    update_embed.description = "Pulling lasted version from **GitLab**!"
    update_embed.add_field(name='Changes',value='```'+update_result+'```',inline=False)
    await util.say(ctx.channel,embed=update_embed)
    update_result = update_result.strip()
    if not (update_result.endswith("is up to date.") or update_result.endswith("up-to-date.")):
        await util.duelogger.concern("DueUtil updating!")
        os._exit(1)
        
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern=None)
async def stopbot(ctx,*args,**details):
    await util.say(ctx.channel,":wave: Stopping DueUtil!")
    await util.duelogger.concern("DueUtil shutting down!")
    os._exit(0)
    
@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern=None)
async def restartbot(ctx,*args,**details):
    await util.say(ctx.channel,":ferris_wheel: Restarting DueUtil!")
    await util.duelogger.concern("DueUtil restarting!!")
    os._exit(1)
    
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

    leaderboard_embed = discord.Embed(title="DueUtil Leaderboard",type="rich",color=gconf.EMBED_COLOUR)

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
            leaderboard_embed.add_field(name = "#"+str(index+1)+bonus,value = (name+" "+player_id+" ``Level "+level+"``"
                                                +" ``Total Exp: "+str(math.trunc(player.total_exp)))+"``",inline=False)
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
                                   +"That's on ``"+details["cmd_key"]+"leaderboard`` page "+str(page+1)+"!"))
    except:
        await util.say(ctx.channel,(":confounded: I can't find you in the leaderboard!?\n"
                                    +"This probably means you're new and leaderboard has not updated yet!"))

async def give_emoji(channel,sender,receiver,emoji):
    if not util.char_is_emoji(emoji) and not util.is_server_emoji(channel.server,emoji):
        raise util.DueUtilException(channel,"You can only send emoji!")
    if sender == receiver:
        raise util.DueUtilException(channel,"You can't send a "+emoji+" to yourself!")
    receiver.emojis +=1
    sender.emojis_given += 1
    await util.say(channel,"**"+receiver.name_clean+"** "+emoji+" :heart: **"+sender.name_clean+"**")

@commands.command(args_pattern='PS')
async def giveemoji(ctx,*args,**details):
  
    """
    [CMD_KEY]giveemoji player emoji
    
    Give a friend an emoji.
    Why? Who knows.
    I'm sure you can have loads of fun with the :cancer: emoji though!
    Also see ``[CMD_KEY]givepotato``
    
    """
    
    await give_emoji(ctx.channel,details["author"],args[0],args[1])
        
@commands.command(args_pattern='P')
async def givepotato(ctx,*args,**details):
  
    """
    [CMD_KEY]givepotato player
    
    Who doesn't like potatoes?
    """

    await give_emoji(ctx.channel,details["author"],args[0],'🥔')
