import discord
from fun import weapons, players
from duecommands import weapons as weap_cmds
from botstuff import commands
from botstuff import util

SHOP_PAGE_MAX_ITEMS = 12

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
    
    #if type(page) is int:
    
    # Think more shop logic
    
    async def shop_weapons_list(page):
        nonlocal ctx
        shop_weapons = list(weapons.get_weapons_for_server(ctx.server.id).values())
        if SHOP_PAGE_MAX_ITEMS * page + SHOP_PAGE_MAX_ITEMS < len (shop_weapons):
            footer = "But wait there's more! Do "+details["cmd_key"]+"shop "+str(page+2)
        else:
            footer = 'Want more? Ask an admin on '+ctx.server.name+' to add some!'

        shop = weap_cmds.weapons_page(shop_weapons,page,"DueUtil's Weapon Shop!")
        shop.set_footer(text=footer)
        
        await util.say(ctx.channel,embed=shop)    

    async def shop_weapon_info(weapon_name):
        nonlocal ctx
        weapon = weapons.get_weapon_for_server(ctx.server.id,weapon_name)
        if weapon == None:
            raise util.DueUtilException(ctx.channel,"Weapon not found")
        weapon_info = discord.Embed(title=weapon.icon+' | '+weapon.name,type="rich",color=16038978)
        weapon_info.set_thumbnail(url=weapon.image_url)
        weapon_info.add_field(name='Damage',value=util.format_number(weapon.damage))
        weapon_info.add_field(name='Accuracy',value=util.format_number(weapon.accy)+'%')
        weapon_info.add_field(name='Price',value=util.format_number(weapon.price,money=True,full_precision=True))
        weapon_info.add_field(name="Hit Message",value=weapon.hit_message)
        weapon_info.set_footer(text='Image supplied by weapon creator.')

        await util.say(ctx.channel,embed=weapon_info)
        
    async def shop_theme_list(page):
        themes = list(players.get_themes().values())
        themes_listings = discord.Embed(title="DueUtil's Theme Shop!",type="rich",color=16038978)      
        if SHOP_PAGE_MAX_ITEMS * page + SHOP_PAGE_MAX_ITEMS < len (themes):
            footer = "But wait there's more! Do "++"mythemes "+str(page+2)
        else:
            footer = 'More themes coming soon!'

        for theme_index in range(SHOP_PAGE_MAX_ITEMS * page,SHOP_PAGE_MAX_ITEMS * page + SHOP_PAGE_MAX_ITEMS):
            if theme_index >= len(themes):
                break
            theme = themes[theme_index]
            themes_listings.add_field(name=theme["icon"]+" | "+theme["name"],value=(theme["description"]+"\n ``"
                                                                                    +util.format_number(theme["price"],money=True,full_precision=True)+"``"))
        themes_listings.set_footer(text=footer)
        await util.say(ctx.channel,embed=themes_listings)

    async def shop_theme_info(theme_name):
        nonlocal ctx
        theme = players.get_theme(theme_name)
        if theme == None:
            raise util.DueUtilException(ctx.channel,"Theme not found!")
        theme_info = discord.Embed(title=theme["icon"]+" | "+theme["name"],type="rich",color=16038978)
        theme_info.set_image(url=theme["preview"])
        theme_info.set_footer(text="Buy this theme for "+util.format_number(theme["price"],money=True,full_precision=True))
        await util.say(ctx.channel,embed=theme_info)
    
    departments = {
                     "weapons":{
                        "alisas":[
                           "weapons",
                           "weaps"
                        ],
                        "actions":{
                           "info_action": shop_weapon_info,
                           "list_action": shop_weapons_list
                        },
                        "item_exists": lambda name : weapons.does_weapon_exist(ctx.server.id,name)
                     },
                    "themes":{
                        "alisas":[
                           "themes",
                           "skins"
                        ],
                        "actions":{
                           "info_action": shop_theme_info,
                           "list_action": shop_theme_list
                        },
                        "item_exists": lambda name : players.get_theme(name) != None
                     }
                  }

    if len(args) == 0:
        greet = ":wave: **Welcome to the DueUtil general store!**\n"
        department_available = "Please have a look in some of our splendiferous departments!\n"
        for department_info in departments.values():
            department_available += "``"+details["cmd_key"]+"shop "+department_info["alisas"][0]+"``\n"
        help = "For more info on the new shop do ``"+details["cmd_key"]+"help shop``"
        await util.say(ctx.channel,greet+department_available+help)
    else:
        department = next((department_info for department_info in departments.values() if args[0].lower() in department_info["alisas"]),None)
        if department != None:
            list_action = department["actions"]["list_action"]
            info_action = department["actions"]["info_action"]
            if len(args) == 1:
                await list_action(0)
            else:
                if type(args[1]) is int:
                    await list_action(args[1])
                else:
                    await info_action(args[1])
        elif len(args) == 1:
            item_name = args[0].lower()
            possible_departments = [department_info for department_info in departments.values() if department_info["item_exists"](item_name)]
            if len(possible_departments) > 1:
                error = (":confounded: An item with that name exists in multiple departments!\n"
                         +"Please be more specific!\n")
                for department_info in possible_departments:
                    error += "``"+details["cmd_key"]+"shop "+department_info["alisas"][0]+" "+item_name+"``\n"
                await util.say(ctx.channel,error)
            elif len(possible_departments) == 0:
                raise util.DueUtilException(ctx.channel,"Item not found!")
            else:
                department = possible_departments[0]
                await department["actions"]["info_action"](item_name)
        else:
            raise util.DueUtilException(ctx.channel,"Department not found")
