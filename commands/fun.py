from commands.util import commands
import util_due;

@commands.command(args_pattern="II")
async def test(ctx,*args): 
    await util_due.say(ctx.channel,("Yo!!! What up dis be my test command fo show.\n"
                                    "I got deedz args ```"+str(args)+"```!"));
    print(args);
