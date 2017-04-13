import discord
from fun import battles, imagehelper, weapons
from botstuff import commands
from botstuff import util
from botstuff.permissions import Permission

@commands.command(args_pattern='M?')
async def myweapons(ctx,*args,**details):
  
    """
    [CMD_KEY]myweapons (page)/(weapon name)
    
    Shows the contents of your weapon inventory.
    
    """
         
    player = details["author"]
    player_weapons = [weapons.get_weapon_from_id(weapon_id) for weapon_id in player.weapon_inventory if weapon_id != weapons.NO_WEAPON_ID]
    page = 1
    if len(args) == 1:
        page = args[0]
    
    if type(page) is int:
        page -= 1
        weapon_store = weapons_page(player_weapons,page,player.name+"'s Weapons"+(" : Page "+str(page+1) if page > 0 else ""),price_divisor=4/3)
        weapon_store.description = "Currently equipped: "+str(player.weapon)
        weapon_store.set_footer(text="Do "+details["cmd_key"]+"equip (weapon name) to equip a weapon.")
        await util.say(ctx.channel,embed=weapon_store)
    else:
        weapon_name = page
        weapon = next((weapon for weapon in player_weapons if weapon.name.lower() == weapon_name.lower()),None)
        if weapon != None:
            embed = discord.Embed(type="rich",color=16038978)
            info = weapon_info(weapon_name,**details,price_divisor=4/3,embed=embed)
            await util.say(ctx.channel,embed=info)
        else:
            raise util.DueUtilException(ctx.channel,"You don't have a weapon with that name!")
      
def weapons_page(weapons_list,page,title,**extras):
    price_divisor = extras.get('price_divisor',1)
    weapons_embed = discord.Embed(title=title,type="rich",color=16038978)
    page_size = 12
    
    if page * page_size >= len(weapons_list):
        raise util.DueUtilException(None,"Page not found")
    for weapon_index in range(page_size*page,page_size*page+page_size):
        if weapon_index >= len(weapons_list):
            break
        weapon = weapons_list[weapon_index]
        if weapon.id == weapons.NO_WEAPON_ID:
            continue
        weapons_embed.add_field(name=str(weapon),value='``'+util.format_number(weapon.price//price_divisor,full_precision=True,money=True)+'``')
    return weapons_embed    
 
@commands.command(args_pattern='PP?')
async def battle(ctx,*args,**details):
  
    """
    [CMD_KEY]battle player (optional other player)
    
    Battle someone!
    
    Note! You don't again any exp or reward from these battles!
    Please do not spam anyone with unwanted battles.
    
    """
    
    player = details["author"]
    if len(args) == 2 and args[0] == args[1] or len(args) == 1 and player == args[0]:
        raise util.DueUtilException(ctx.channel,"Don't beat yourself up!")
    if len(args) == 2:
        player_one = args[0]
        player_two = args[1]
    else:
        player_one = player
        player_two = args[0]
        
    battle_log = battles.get_battle_log(player_one=player_one,player_two=player_two)[0]
    await imagehelper.battle_screen(ctx.channel,player_one,player_two)
    await util.say(ctx.channel,embed=battle_log)
    
@commands.command(permission = Permission.SERVER_ADMIN,args_pattern='SSCCB?S?S?')
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
    await util.say(ctx.channel,(weapon.icon+" **"+weapon.name_clean+"** is available in the shop for "
                                +util.format_number(weapon.price,money=True)+"!"))
  
# Part of the shop buy command
async def buy_weapon(weapon_name,**details):
    
    customer = details["author"]
    weapon = weapons.get_weapon_for_server(details["server_id"],weapon_name)
    channel = details["channel"]
    
    if weapon == None or weapon_name == "none":
        raise util.DueUtilException(channel,"Weapon not found")
    if customer.money - weapon.price < 0:
        await util.say(channel,":anger: You can't afford that weapon.")
    elif weapon.price > customer.item_value_limit:
        await util.say(channel,(":baby: Awwww. I can't sell you that.\n"
                                    +"You can use weapons with a value up to **"
                                    +util.format_number(customer.item_value_limit,money=True,full_precision=True)+"**"))
    elif customer.weapon.w_id != weapons.NO_WEAPON_ID:
        if len(customer.weapon_inventory) < 6:
            if weapon.w_id not in customer.weapon_inventory:
                customer.weapon_inventory.append(weapon.w_id)
                await util.say(channel,("**"+customer.name_clean+"** bought a **"+weapon.name_clean+"** for "
                                            + util.format_number(weapon.price,money=True,full_precision=True)
                                            + "\n:warning: You have not equiped this weapon do **"
                                            + details["cmd_key"]+"equip "
                                            + weapon.name_clean.lower()+"** to equip this weapon."))
            else:
                raise util.DueUtilException(channel,"Cannot store new weapon! A you already have a weapon with the same name!")
        else:
            raise util.DueUtilException("No free weapon slots!")
    else:
        customer.w_id = weapon.w_id
        await util.say(channel,("**"+customer.name_clean+"** bought a **"
                                    +weapon.name_clean+"** for "+util.format_number(weapon.price,money=True,full_precision=True)))
    customer.save()

def weapon_info(weapon_name,**details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor',1)
    weapon = weapons.get_weapon_for_server(details["server_id"],weapon_name)
    if weapon == None:
        raise util.DueUtilException(details["channel"],"Weapon not found")
    embed.title = weapon.icon+' | '+weapon.name_clean
    embed.set_thumbnail(url=weapon.image_url)
    embed.add_field(name='Damage',value=util.format_number(weapon.damage))
    embed.add_field(name='Accuracy',value=util.format_number(weapon.accy)+'%')
    embed.add_field(name='Price',value=util.format_number(weapon.price//price_divisor,money=True,full_precision=True))
    embed.add_field(name="Hit Message",value=weapon.hit_message)
    embed.set_footer(text='Image supplied by weapon creator.')
    return embed
    
