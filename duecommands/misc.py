from botstuff import commands
from botstuff import util
from botstuff.permissions import Permission
from fun import misc

async def glitter_text(channel,text):
    gif_text = misc.get_glitter_text(text)
    await util.get_client(channel).send_file(channel, fp=gif_text,
                                             filename="glittertext.gif", 
                                             content=":sparkles: Your glitter text!")

@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="S")
@commands.imagecommand()
async def glittertext(ctx,*args,**details): 
    await glitter_text(ctx.channel,args[0])

@commands.command()
async def wish(ctx,*args,**details): 
    # TODO
    pass
