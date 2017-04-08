from fun import imagehelper
from botstuff import util,commands
import botstuff.permissions

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
    permissions_report = ""
    for permission in botstuff.permissions.permissions:
        permissions_report += ("``"+permission.value[1]+"`` → "
                               + (":white_check_mark:" if botstuff.permissions.has_permission(ctx.author,permission) else ":no_entry:")+"\n")
    await util.say(ctx.channel,permissions_report)

@commands.command(args_pattern="II")
async def add(ctx,*args,**details):
    first_number = args[0]
    second_number = args[1]
    result = first_number + second_number
    await util.say(ctx.channel,"Is "+result)
