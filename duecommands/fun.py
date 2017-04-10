import discord
from fun import imagehelper
from botstuff import util,commands
import botstuff.permissions
from botstuff.permissions import Permission

@commands.command(args_pattern=None)
async def test(ctx,*args,**details): 
    
    """A test command"""
    
    # print(args[0].__dict__)
    # args[0].save()
    await imagehelper.test(ctx.channel)
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
    else:
        raise util.DueUtilException(ctx.channel,"Permission not found")
        
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
