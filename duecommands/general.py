import discord
from fun import weapons, game
from duecommands import weapons as weap_cmds
from botstuff import commands
from botstuff import util

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
    
    if len(args) == 0:
        await util.say("Welcome to the shop")
    elif len(args) == 1:
        if args[0] in ("weapons","weaps"):
            shop_weapons_list()
        elif args[0] in ("themes","skins"):
            shop_theme_list()
        else:
            weapon_exists = does_weapon_exist(ctx.server.id,args[0])
            theme_exists = game.get_theme(args[0]) != None
            if weapon_exists and not theme_exists:
                shop_weapon_info(args[0])
            elif theme_exists and not weapon_exists:
                shop_theme_info(args[0])
            elif weapon_exists and theme_exists:
                await util.say("Conflict")
            else:
                await util.say("Not found")
    else:
        if type(args[1]) is int:  
            if args[0] in ("weapons","weaps"):
                shop_weapons_list(args[1])
            elif args[0] in ("themes","skins"):
                shop_theme_list(args[1])
                

    async def shop_weapons_list(page):
        nonlocal ctx
        shop_weapons = list(weapons.get_weapons_for_server(ctx.server.id).values())
        if 12 * page + 12 < len (shop_weapons):
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
        themes = list(player.get_owned_themes().values())
        themes_listings = discord.Embed(title="Available themes",type="rich",color=16038978)      
        if 12 * page + 12 < len (themes):
            footer = "But wait there's more! Do "++"mythemes "+str(page+2)
        else:
            footer = 'More themes coming soon!'

        for theme_index in range(12 * page,12 * page + 12):
            if theme_index >= len(themes):
                break
            theme = themes[theme_index]
            themes_listings.add_field(name=theme["icon"]+" | "+theme["name"],value=theme["description"])
        themes_listings.set_footer(text=footer)
        await util.say(ctx.channel,embed=themes_listings)

    async def shop_theme_info(theme_name):
        nonlocal ctx
        theme = players.get_theme(theme_name)
        if theme == None:
            raise util.DueUtilException(ctx.channel,"Theme not found!")
        theme_info = discord.Embed(title=theme["icon"]+" | "+theme["name"],type="rich",color=16038978)
        theme_info.set_image(url=theme["preview"])
        theme_info.set_footer(text="Do "+details["cmd_key"]+"settheme "+theme["name"].lower()+" to use this theme!")
        await util.say(ctx.channel,embed=theme_info)
