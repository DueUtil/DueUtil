import discord
import inspect
from fun import weapons, players
from duecommands import weapons as weap_cmds
from duecommands import players as player_cmds
from botstuff import commands
from botstuff import util

SHOP_PAGE_MAX_ITEMS = 12

def shop_weapons_list(page,**details):
    shop = details["embed"]
    shop_weapons = list(weapons.get_weapons_for_server(details["server_id"]).values())
    if SHOP_PAGE_MAX_ITEMS * page + SHOP_PAGE_MAX_ITEMS < len (shop_weapons):
        footer = "But wait there's more! Do "+details["cmd_key"]+"shop "+str(page+2)
    else:
        footer = 'Want more? Ask an admin on '+details["server_name_clean"]+' to add some!'
    shop = weap_cmds.weapons_page(shop_weapons,page,"DueUtil's Weapon Shop!")
    shop.set_footer(text=footer)
    return shop 

def weapon_info(weapon_name,**details):
    embed = details["embed"]
    weapon = weapons.get_weapon_for_server(details["server_id"],weapon_name)
    if weapon == None:
        raise util.DueUtilException(details["channel"],"Weapon not found")
    embed.title = weapon.icon+' | '+weapon.name_clean
    embed.set_thumbnail(url=weapon.image_url)
    embed.add_field(name='Damage',value=util.format_number(weapon.damage))
    embed.add_field(name='Accuracy',value=util.format_number(weapon.accy)+'%')
    embed.add_field(name='Price',value=util.format_number(weapon.price,money=True,full_precision=True))
    embed.add_field(name="Hit Message",value=weapon.hit_message)
    embed.set_footer(text='Image supplied by weapon creator.')
    return embed
    
def shop_theme_list(page,**details):
    shop = details["embed"]
    themes = list(players.get_themes().values())
    shop.title = "DueUtil's Theme Shop"
    if SHOP_PAGE_MAX_ITEMS * page + SHOP_PAGE_MAX_ITEMS < len (themes):
        footer = "But wait there's more! Do "++"mythemes "+str(page+2)
    else:
        footer = 'More themes coming soon!'
    for theme_index in range(SHOP_PAGE_MAX_ITEMS * page,SHOP_PAGE_MAX_ITEMS * page + SHOP_PAGE_MAX_ITEMS):
        if theme_index >= len(themes):
            break
        theme = themes[theme_index]
        shop.add_field(name=theme["icon"]+" | "+theme["name"],value=(theme["description"]+"\n ``"
                                                                      +util.format_number(theme["price"],money=True,full_precision=True)+"``"))
    shop.set_footer(text=footer)
    return shop
    
def theme_info(theme_name,**details):
    embed = details["embed"]
    theme = players.get_theme(theme_name)
    if theme == None:
            raise util.DueUtilException(details["channel"],"Theme not found!")
    embed.title = theme["icon"]+" | "+theme["name"]
    embed.set_image(url=theme["preview"])
    embed.set_footer(text="Buy this theme for "+util.format_number(theme["price"],money=True,full_precision=True))
    return embed
    
def get_department_from_name(name):
    return next((department_info for department_info in departments.values() if name.lower() in department_info["alisas"]),None)
        
async def item_action(item_name,action,**details):
    possible_departments = [department_info for department_info in departments.values() if department_info["item_exists"](details["server_id"],item_name)]
    if len(possible_departments) > 1:
        error = (":confounded: An item with that name exists in multiple departments!\n"
                  +"Please be more specific!\n")
        for department_info in possible_departments:
            error += "``"+details["cmd_key"]+details["command_name"]+" "+department_info["alisas"][0]+" "+item_name+"``\n"
        await util.say(details["channel"],error)
    elif len(possible_departments) == 0:
        raise util.DueUtilException(details["channel"],"Item not found!")
    else:
        department = possible_departments[0]
        action = department["actions"][action]
        if inspect.iscoroutinefunction(action):
            action_result = await action(item_name,**details)
        else:
            action_result = action(item_name,**details)
        if isinstance(action_result,discord.Embed):
            await util.say(details["channel"], embed = action_result)
            
def placeholder(_,**details):
    embed = details["embed"]
    embed.title = "Department closed"
    return embed
  
departments = {
   "weapons":{
      "alisas":[
         "weapons",
         "weaps"
      ],
      "actions":{
         "info_action":weapon_info,
         "list_action":shop_weapons_list,
         "buy_action":weap_cmds.buy_weapon
      },
      "item_exists":lambda server_id,name:weapons.does_weapon_exist(server_id,name)
   },
   "themes":{
      "alisas":[
         "themes",
         "skins"
      ],
      "actions":{
         "info_action":theme_info,
         "list_action":shop_theme_list,
         "buy_action":player_cmds.buy_theme
      },
      "item_exists":lambda _,name:players.get_theme(name) != None
   },
   "backgrounds":{
      "alisas":[
         "backgrounds",
         "bgs"
      ],
      "actions":{
         "info_action":placeholder,
         "list_action":placeholder,
         "buy_action":placeholder
      },
      "item_exists":lambda _,__:False
   }
}
    
@commands.command(args_pattern='S?M?')
async def shop(ctx,*args,**details):
  
    """
    [CMD_KEY]shop department (page or name)
    
    A place to see all the backgrounds, banners, themes 
    and weapons on sale.
    
    e.g. [CMD_KEY]shop weapons 
    will show all weapons currenly in store.
    [CMD_KEY]shop item 
    will show extra details about that item.
    If you want anything from the shop use the
    [CMD_KEY]buy command!
    """
    
    shop = discord.Embed(type="rich",color=16038978)
    details["embed"] = shop

    if len(args) == 0:
        greet = ":wave: **Welcome to the DueUtil general store!**\n"
        department_available = "Please have a look in some of our splendiferous departments!\n"
        for department_info in departments.values():
            department_available += "``"+details["cmd_key"]+"shop "+department_info["alisas"][0]+"``\n"
        help = "For more info on the new shop do ``"+details["cmd_key"]+"help shop``"
        await util.say(ctx.channel,greet+department_available+help)
    else:
        department = get_department_from_name(args[0])
        if department != None:
            list_action = department["actions"]["list_action"]
            info_action = department["actions"]["info_action"]
            if len(args) == 1:
                await util.say(ctx.channel,embed = list_action(0,**details))
            else:
                if type(args[1]) is int:
                    await util.say(ctx.channel,embed = list_action(args[1]-1,**details))
                else:
                    await util.say(ctx.channel,embed = info_action(args[1],**details))
        elif len(args) == 1:
            await item_action(args[0].lower(),"info_action",**details)
        else:
            raise util.DueUtilException(ctx.channel,"Department not found")

@commands.command(args_pattern='S?S?')
async def buy(ctx,*args,**details):
  
    """
    [CMD_KEY]buy item
    
    """

    if len(args) == 1:
        await item_action(args[0].lower(),"buy_action",**details)
    else:
        department = get_department_from_name(args[0])
        if department != None:
            await department["actions"]["buy_action"](args[1].lower(),**details)
        else:
            raise util.DueUtilException(ctx.channel,"Department not found")

@commands.command(args_pattern='S?S?')
async def sell(ctx,*args,**details):
    pass
