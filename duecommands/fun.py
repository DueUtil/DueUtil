from fun import imagehelper
from botstuff import util,commands;

@commands.command(args_pattern=None)
async def test(ctx,*args,**details): 
    
    """A test command"""
    # print(args[0].__dict__)
    # args[0].save()
    await imagehelper.test(ctx.channel)
    await util.say(ctx.channel,("Yo!!! What up dis be my test command fo show.\n"
                                    "I got deedz args ```"+str(args)+"```!"));
                                    
@commands.command(args_pattern="II")
async def add(ctx,*args,**details):
    first_number = args[0];
    second_number = args[1];
    result = first_number + second_number;
    await util.say(ctx.channel,"Is "+result);
