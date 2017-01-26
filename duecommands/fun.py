from commands.util import commands
import util_due as util;

@commands.command(args_pattern="II")
async def test(ctx,*args): 
    
    """A test command"""
  
    await util.say(ctx.channel,("Yo!!! What up dis be my test command fo show.\n"
                                    "I got deedz args ```"+str(args)+"```!"));
    print(args);


@commands.command(args_pattern="II")
async def add(ctx,*args):
    first_number = args[0];
    second_number = args[1];
    result = first_number + second_number;
    await util.say(ctx.channel,"Is "+result);
