from botstuff import util
import discord
from functools import wraps
import generalconfig as gconf 

"""
Generic wrappers to make listing items (e.g. backgrounds)
and setting them faster (to make)
"""

def item_preview(thing_info):
    
    """
    Generic mything command (time saver)
    Pass function that returns a dict
    
    Expects:
      thing_type
      thing_list
      thing_lister
      my_command
      thing_info
      thing_getter
    """
    
    @wraps(thing_info)
    async def mything(ctx,*args,**details):
        player = details["author"]
        page = 1
        
        things_info = thing_info(player)
        thing_type = things_info["thing_type"]

        if len(args) == 1:
            page = args[0]
        
        if type(page) is int:
            page-= 1
            thing_list = things_info["thing_list"]
            title = player.get_name_possession_clean()+" "+thing_type.title()
            thing_embed = things_info["thing_lister"](thing_list,page,title,price_divisor=4/3,
                                      footer_more="But wait there's more! Do "+details["cmd_key"]+things_info["my_command"]+" "+str(page+2))
            await util.say(ctx.channel,embed = thing_embed)
        else:
            thing_name = page.lower()
            thing = things_info["thing_getter"](thing_name)
            if thing == None:
                raise util.DueUtilException(ctx.channel,thing_type.title()+" not found!")
            thing_embed = things_info["thing_info"](thing_name,**details,embed=discord.Embed(type="rich",color=gconf.EMBED_COLOUR))
            thing_embed.set_footer(text="Do "+details["cmd_key"]+things_info["my_command"]+" "+thing.name_command+" to use this "+thing_type+"!")
            await util.say(ctx.channel,embed=thing_embed)
    return mything
    
def item_setter(thing_info):
  
    """
    Generic setthing command 
    
    Excects func that returns dict with:
      thing_type
      thing_getter
      thing_setter
      thing_list
    """
  
    @wraps(thing_info)
    async def setthing(ctx,*args,**details):
        player = details["author"]
        things_info = thing_info(player)
        thing_type = things_info["thing_type"]

        thing_id = args[0].lower()
        if thing_id in things_info["thing_list"]:
            thing = things_info["thing_getter"](thing_id)
            things_info["thing_setter"](thing_id)
            await util.say(ctx.channel,":white_check_mark: "+thing_type.title()+" set to **"+thing.name_clean+"**")
        else:
            raise util.DueUtilException(ctx.channel,thing_type.title()+" not found!")
    return setthing
