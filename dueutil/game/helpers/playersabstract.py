from functools import wraps

import discord

import generalconfig as gconf
from dueutil import util

"""
Generic wrappers to make listing items (e.g. backgrounds)
and setting them faster (to make)
"""
#TODO renamed to playersabstarct

def item_preview(thing_info_preview):
    """
    Generic mything command (time saver)
    Pass function that returns a dict
    
    Expects:
      thing_type
      thing_lister
      thing_list
      my_command
      thing_info
      thing_getter
    """

    @wraps(thing_info_preview)
    async def mything(ctx, *args, **details):
        player = details["author"]
        page = 1

        things_info = thing_info_preview(player)
        thing_type = things_info["thing_type"]

        if len(args) == 1:
            page = args[0]

        if type(page) is int:
            page -= 1
            thing_list = things_info["thing_list"]
            title = player.get_name_possession_clean() + " " + thing_type.title()
            thing_embed = things_info["thing_lister"](thing_list, page, title, price_divisor=4 / 3,
                                                      footer_more="But wait there's more! Do " + details["cmd_key"] +
                                                                  things_info["my_command"] + " " + str(page + 2))
            await util.say(ctx.channel, embed=thing_embed)
        else:
            thing_name = page.lower()
            thing = things_info["thing_getter"](thing_name)
            if thing is None:
                raise util.DueUtilException(ctx.channel, thing_type.title() + " not found!")
            thing_embed = things_info["thing_info"](thing_name, **details,
                                                    embed=discord.Embed(type="rich", color=gconf.EMBED_COLOUR))
            thing_embed.set_footer(text="Do " + details["cmd_key"] + things_info[
                "my_command"] + " " + thing.name + " to use this " + thing_type + "!")
            await util.say(ctx.channel, embed=thing_embed)

    return mything


def item_setter(item_info_setter):
    """
    Generic setthing command 
    
    Excects func that returns dict with:
      thing_type
      thing_inventory_slot
    """

    @wraps(item_info_setter)
    async def setthing(ctx, *args, **details):
        player = details["author"]
        thing_info = item_info_setter()
        thing_type = thing_info["thing_type"]
        thing_inventory_slot = thing_info["thing_inventory_slot"]

        thing_id = args[0].lower()
        if thing_id in player.inventory[thing_inventory_slot]:
            # This SHOULD a property setter function
            setattr(player, thing_type, thing_id)
            # This should be a property returning the 'thing' object
            thing = getattr(player, thing_type)
            player.save()
            await util.say(ctx.channel,
                           ":white_check_mark: " + thing_type.title() + " set to **" + thing.name_clean + "**")
        else:
            raise util.DueUtilException(ctx.channel, thing_type.title() + " not found!")

    return setthing
