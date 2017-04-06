import discord
from fun import battles
from fun import weapons
from botstuff import commands
from botstuff import util

@commands.command()
async def myweapons(ctx,*args,**details):
  
    """
    [CMD_KEY]myweapons
    
    Shows the contents of your weapon inventory.
    
    """
         
    player = details["author"]
    weapon_store = weapons_page(player.weapon_inventory,0,player.name+"'s Weapons")
    
    await util.say(ctx.channel,embed=weapon_store)

@commands.command(args_pattern='M?')
async def shop(ctx,*args,**details):
  
    """
    [CMD_KEY]shop (page number) or (weapon name)
    
    Shows DueUtil's weapon store!
    
    Shows information about a weapon in the shop if given a weapon name.
    
    """
    
    page = args[0] if len(args) == 1 else 0
    
    if type(page) is int:
    
        shop_weapons = list(weapons.get_weapons_for_server(ctx.server.id).values())
        if 12 * page + 12 < len (shop_weapons):
            footer = "But wait there's more! Do "+details["cmd_key"]+"shop "+str(page+2)
        else:
            footer = 'Want more? Ask an admin on '+ctx.server.name+' to add some!'

        shop = weapons_page(shop_weapons,page,"DueUtil's Weapon Shop!")
        shop.set_footer(text=footer)
        
        await util.say(ctx.channel,embed=shop)
    else:
        weapon = weapons.get_weapon_for_server(ctx.server.id,page)
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

def weapons_page(weapons_list,page,title):
    weapons = discord.Embed(title=title,type="rich",color=16038978)
    for weapon_index in range(12*page,12*page+12):
        if weapon_index >= len(weapons_list):
            break
        weapon = weapons_list[weapon_index]
        weapons.add_field(name=weapon.icon+' | '+weapon.name,value='```'+util.format_number(weapon.price,full_precision=True,money=True)+'```')
    return weapons    

@commands.command(args_pattern='S')
async def buy(ctx,*args,**details):

    """
    [CMD_KEY]buy "weapon name"
    
    Buys a weapon from the shop.!
    
    """
    customer = details["author"]
    weapon = weapons.get_weapon_for_server(ctx.server.id,args[0])
    if weapon == None:
        raise util.DueUtilException(ctx.channel,"Weapon not found")
    if customer.money - weapon.price < 0:
        await util.say(ctx.channel,":anger: You can't afford that weapon.")
    elif weapon.price > customer.item_value_limit:
        await util.say(ctx.channel,(":baby: Awwww. I can't sell you that.\n"
                                    +"You can use weapons with a value up to **"
                                    +util.format_number(customer.item_value_limit,money=True,full_precision=True)+"**"))
    elif customer.weapon.w_id != weapons.NO_WEAPON_ID:
        if len(customer.weapon_inventory) < 6:
            if weapon.w_id not in customer.weapon_inventory:
                customer.weapon_inventory.append(weapon.w_id)
                await util.say(ctx.channel,("**"+customer.name+"** bought a **"+weapon.name+"** for "
                                            +util.format_number(weapon.price,money=True,full_precision=True)
                                            +"\n:warning: You have not equiped this weapon do **"
                                            +util.get_server_cmd_key(ctx.server)+"equip "
                                            +weapon.name.lower()+"** to equip this weapon."))
            else:
                raise util.DueUtilException("Cannot store new weapon! A you already have a weapon with the same name!")
        else:
            raise util.DueUtilException("No free weapon slots!")
    else:
        customer.w_id = weapon.w_id
        await util.say(ctx.channel,("**"+customer.clean_name+"** bought a **"
                                    +weapon.name+"** for "+util.format_number(weapon.price,money=True,full_precision=True)))
    customer.save()
 
@commands.command(args_pattern='PP')
async def battle(ctx,*args,**details):
    battle_result = battles.battle(player_one=args[0],player_two=args[1])
    battle_moves = list(battle_result[0].values())
    battle = discord.Embed( title=args[0].clean_name+" :vs: "+args[1].clean_name,type="rich",color=16038978)
    battle_log = ""
    for move in battle_moves:
        move_repetition = move[1]
        if move_repetition <= 1:
            battle_log += move[0] + '\n'
        else:
            battle_log += '('+ move[0] +') × ' + str(move_repetition) + '\n'
    battle.add_field(name='Battle log',value=battle_log)

    await util.say(ctx.channel,embed=battle)
 
@commands.command(admin_only=True,args_pattern='SSCCB?S?S?')
async def createweapon(ctx,*args,**details):
    
    """
    [CMD_KEY]createweapon "weapon name" "hit message" damage accy
    
    Creates a weapon for the server shop!
    
    Example usage: 
    
    [CMD_KEY]createweapon "Laser" "FIRES THEIR LAZOR AT" 100 50
    
    For extra customization you add the following:
    
    (ranged) (icon) (image url)

    """
    
    extras = dict()
    if len(args) >= 5:
        extras['melee'] = args[4]
    if len(args) >= 6:
        extras['icon'] = args[5]
    if len(args) == 7:
        extras['image_url'] = args[6]
  
    weapon = weapons.Weapon(*args[:4],**extras,ctx=ctx)
    await util.say(ctx.channel,(weapon.icon+" **"+weapon.name.strip('*')+"** is available in the shop for "
                                +util.format_number(weapon.price,money=True)+"!"))
                      
