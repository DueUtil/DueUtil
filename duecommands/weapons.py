import discord
from fun import battles, imagehelper, weapons, players, stats
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
    player_weapons = player.get_owned_weapons()
    page = 1
    if len(args) == 1:
        page = args[0]
    
    if type(page) is int:
        page -= 1
        title = player.get_name_possession_clean()+" Weapons"+(" : Page "+str(page+1) if page > 0 else "")
        if len(player_weapons) > 0:
            weapon_store = weapons_page(player_weapons,page,title,price_divisor=4/3)
        else: 
            weapon_store = discord.Embed(title=title,type="rich",color=16038978)
            weapon_store.add_field(name ="No weapons stored!",value="You can buy up to 6 more weapons from the shop and store them here!")
        weapon_store.description = "Currently equipped: "+str(player.weapon)
        weapon_store.set_footer(text="Do "+details["cmd_key"]+"equip (weapon name) to equip a weapon.")
        await util.say(ctx.channel,embed=weapon_store)
    else:
        weapon_name = page
        if player.w_id != weapons.NO_WEAPON_ID:
            player_weapons.append(weapons.get_weapon_from_id(player.w_id))
        weapon = next((weapon for weapon in player_weapons if weapon.name.lower() == weapon_name.lower()),None)
        if weapon != None:
            embed = discord.Embed(type="rich",color=16038978)
            info = weapon_info(weapon_name,**details,price_divisor=4/3,embed=embed)
            await util.say(ctx.channel,embed=info)
        else:
            raise util.DueUtilException(ctx.channel,"You don't have a weapon with that name!")
  
@commands.command(args_pattern=None)
async def unequip(ctx,*args,**details):
  
    """
    [CMD_KEY]unequip
    
    Unequips your current weapon
    """
    
    player = details["author"]
    weapon = player.weapon
    if weapon.w_id == weapons.NO_WEAPON_ID:
        raise util.DueUtilException(ctx.channel,"You don't have anything equiped anyway!")
    if len(player.weapon_inventory) >= 6:
        raise util.DueUtilException(ctx.channel, "No room in your weapon storage!")
    if player.owns_weapon(weapon.name):
        raise util.DueUtilException(ctx.channel,"You already have a weapon with that name stored!")
         
    player.store_weapon(weapon)
    player.set_weapon(weapons.get_weapon_from_id("None"))
    player.save()
    await util.say(ctx.channel, ":white_check_mark: **"+weapon.name_clean+"** unequiped!")
            
@commands.command(args_pattern='S')
async def equip(ctx,*args,**details):
  
    """
    [CMD_KEY]equip (weapon name)
    
    Equips a weapon from your weapon inventory.
    """
    
    player = details["author"]
    current_weapon = player.weapon

    weapon = player.get_weapon(args[0].lower())
    if weapon == None:
        raise util.DueUtilException(ctx.channel,"You do not have that weapon stored!")    
                
    weapon_info = player.pop_from_invetory(weapon)

    if player.owns_weapon(current_weapon.name):
        player.weapon_inventory.append(weapon_info)
        raise util.DueUtilException(ctx.channel,"Can't put your current weapon into storage! There is already a weapon with the same name stored!"); 
        
    if current_weapon.w_id != weapons.NO_WEAPON_ID:
        player.store_weapon(current_weapon)
        
    player.set_weapon(weapon)
    player.save()

    await util.say(ctx.channel,":white_check_mark: **"+weapon.name_clean+"** equiped!")
     
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
        weapons_embed.add_field(name=str(weapon),value='``'+util.format_number(weapon.price//price_divisor,full_precision=True,money=True)+'``')
    return weapons_embed    
 
@commands.command(args_pattern='PP?')
@commands.imagecommand()
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
  
@commands.command(args_pattern='PC')
async def wagerbattle(ctx,*args,**details):
  
    """
    [CMD_KEY]wagerbattle player amount
    
    Money will not be taken from your account after you use this command.
    If you cannot afford to pay when the wager is accepted you will be forced
    to sell your weapons.
    
    """
    sender = details["author"]
    receiver = args[0]
    money = args[1]
    
    if sender == receiver:
        raise util.DueUtilException(ctx.channel,"You can't wager against yourself!")
       
    if sender.money - money < 0:
        raise util.DueUtilException(ctx.channel,"You can't afford this wager!")
        
    battles.BattleRequest(sender,receiver,money)

    await util.say(ctx.channel,("**"+sender.name_clean+"** wagers **"+receiver.name_clean+"** ``"
                                    +util.format_number(money,full_precision=True,money=True)+"`` that they will win in a battle!"))
     
@commands.command(args_pattern='C?')
async def mywagers(ctx,*args,**details):
  
    """
    [CMD_KEY]mywagers (page)
    
    Lists your received wagers.
    
    """
    
    player = details["author"]
    page_size = 12
    page = 0
    if len(args) == 1:
        page = args[0] - 1
    title = player.get_name_possession_clean()+" Received Wagers"+(" : Page "+str(page+1) if page > 0 else "")
    wagers_embed = discord.Embed(title=title,type="rich",color=16038978)
    wager_list = player.battlers
    if len(wager_list) > 0:
        if page * page_size >= len(wager_list):
            raise util.DueUtilException(ctx.channel,"Page not found")
        for wager_index in range(page_size*page,page_size*page+page_size):
            if wager_index >= len(wager_list):
                break
            wager = wager_list[wager_index]
            sender = players.find_player(wager.sender_id)
            wagers_embed.add_field(name=str(wager_index+1)+". Request from "+sender.name_clean, 
                                   value="<@"+sender.id+"> ``"+util.format_number(wager.wager_amount,full_precision=True,money=True)+"``")
        wagers_embed.add_field(name="Actions",value=("Do ``"+details["cmd_key"]+"acceptwager (number)`` to accept a wager \nor ``"
                                                                +details["cmd_key"]+"declinewager (number)`` to decline"),inline=False)
        if page_size * page + page_size < len (wager_list):
            footer = "But wait there's more! Do "+details["cmd_key"]+"mywagers "+str(page+2)
        else:
            footer = 'That is all!'
        wagers_embed.set_footer(text=footer)
    else:
        wagers_embed.add_field(name ="No wagers received!",value="Wager requests you get from other players will appear here.")
    await util.say(ctx.channel,embed=wagers_embed)

@commands.command(args_pattern='C')   
@commands.imagecommand() 
async def acceptwager(ctx,*args,**details):
  
    """
    [CMD_KEY]acceptwager (wager number)
    
    Accepts a wager!
    
    """
    
    player = details["author"]
    wager_index = args[0] - 1
    if wager_index >= len(player.battlers):
        raise util.DueUtilException(ctx.channel,"Request not found!")
    if player.money - player.battlers[wager_index].wager_amount // 2 < 0:
        raise util.DueUtilException(ctx.channel,"You can't afford the risk!")

    wager = player.battlers.pop(wager_index)
    sender = players.find_player(wager.sender_id)
    battle_details = battles.get_battle_log(player_one=player,player_two=sender)
    battle_log = battle_details[0]
    battle_details[1]
    winner = battle_details[2]
    wager_amount_str = util.format_number(wager.wager_amount,full_precision=True,money=True)
    total_transferred = wager.wager_amount 
    if winner != player:
        battle_log.add_field(name = "Wager results", value = (":skull: **"+player.name_clean+"** lost to **"+sender.name_clean+"** and paid ``"
                                                              +wager_amount_str+"``"),inline=False)
        player.money -= wager.wager_amount 
        sender.money += wager.wager_amount 
         
    else:
        player.wagers_won += 1
        payback = ""
        if sender.money - wager.wager_amount >= 0:
            payback = ("**"+sender.name_clean+"** paid **"+player.name_clean+"** ``"
                       +wager_amount_str+"``")
            player.money += wager.wager_amount 
            sender.money -= wager.wager_amount  
        else:
            weapons_sold = 0             
            if sender.w_id != weapons.NO_WEAPON_ID:
                weapons_sold += 1
                sender.money += int(sender.weapon_sum.split("/")[0])//(4/3)
                sender.set_weapon(weapons.get_weapon_from_id("None"))
            if sender.money - wager.wager_amount < 0:
                for weapon in sender.get_owned_weapons():
                    weapon_info = sender.pop_from_invetory(weapon)
                    sender.money += int(weapon_info[1].split("/")[0])//(4/3)
                    weapons_sold += 1
                    if sender.money - wager.wager_amount >= 0:
                        break
            amount_not_paid = max(0,wager.wager_amount - sender.money)
            amount_paid = wager.wager_amount-amount_not_paid
            amount_paied_str = util.format_number(amount_paid,full_precision=True,money=True)

            if weapons_sold == 0:
                payback = ("**"+sender.name_clean+"** could not afford to pay and had no weapons to sell! \n``"
                          +amount_paied_str+"`` is all they could pay.")
            else:
                payback = ("**"+sender.name_clean+"** could not afford to pay and had to sell "
                          +str(weapons_sold)+" weapon"+("s" if weapons_sold != 1 else "")+" \n")
                if amount_paid != wager.wager_amount:
                    payback += "They were still only able to pay ``"+amount_paied_str+"``. \nPathetic."
                else:
                    payback += "They were able to muster up the full ``"+amount_paied_str+"``"
            sender.money -= amount_paid
            player.money += amount_paid
            total_transferred = amount_paid    
        battle_log.add_field(name = "Wager results", value = ":sparkles: **"+player.name_clean+"** won agaist **"+sender.name_clean+"**!\n"+payback,inline=False)
    stats.increment_stat(stats.Stat.MONEY_TRANSFERRED,total_transferred)
    sender.save()
    player.save()
    await imagehelper.battle_screen(ctx.channel,player,sender)
    await util.say(ctx.channel,embed=battle_log)
    
@commands.command(args_pattern='C')    
async def declinewager(ctx,*args,**details):
  
    """
    [CMD_KEY]declinewager (wager number)
    
    Declines a wager.
    
    """
    
    player = details["author"]
    wager_index = args[0] -1
    if wager_index < len(player.battlers):
        wager = player.battlers[wager_index]
        del player.battlers[wager_index]
        player.save()
        sender = players.find_player(wager.sender_id)
        await util.say(ctx.channel,"**"+player.name_clean +"** declined a wager from **"+sender.name_clean+"**")
                                   
    else:
        raise util.DueUtilException(ctx.channel,"Request not found!")
    
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
                                
   
@commands.command(permission = Permission.SERVER_ADMIN,args_pattern='S')
async def removeweapon(ctx,*args,**details):
    
    """
    [CMD_KEY]removeweapon (weapon name)
    
    Screw all the people that bought it :D
    """
    
    weapon_name = args[0].lower()
    weapon = weapons.get_weapon_for_server(ctx.server.id,weapon_name)
    if weapon == None or weapon.id == weapons.NO_WEAPON_ID:
        raise util.DueUtilException(ctx.channel,"Weapon not found")
    if weapon.id != weapons.NO_WEAPON_ID and weapons.stock_weapon(weapon_name) != weapons.NO_WEAPON_ID:
        raise util.DueUtilException(ctx.channel,"You can't remove stock weapons!")
    weapons.remove_weapon_from_shop(ctx.server,weapon_name)
    await util.say(ctx.channel,"**"+weapon.name_clean+"** has been removed from the shop!")
          
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
                customer.store_weapon(weapon)
                customer.money -= weapon.price
                await util.say(channel,("**"+customer.name_clean+"** bought a **"+weapon.name_clean+"** for "
                                            + util.format_number(weapon.price,money=True,full_precision=True)
                                            + "\n:warning: You have not equiped this weapon do **"
                                            + details["cmd_key"]+"equip "
                                            + weapon.name_command_clean.lower()+"** to equip this weapon."))
            else:
                raise util.DueUtilException(channel,"Cannot store new weapon! A you already have a weapon with the same name!")
        else:
            raise util.DueUtilException(channel,"No free weapon slots!")
    else:
        customer.set_weapon(weapon)
        customer.money -= weapon.price
        await util.say(channel,("**"+customer.name_clean+"** bought a **"
                                    +weapon.name_clean+"** for "+util.format_number(weapon.price,money=True,full_precision=True)))
    customer.save()

async def sell_weapon(weapon_name,**details):
  
    player = details["author"]
    channel = details["channel"]
    
    price_divisor=4/3
    
    if player.weapon.name.lower() == weapon_name:
        weapon_to_sell = player.weapon
        player.set_weapon(weapons.get_weapon_from_id("None"))
    else:
        weapon_to_sell = next((weapon for weapon in player.get_owned_weapons() if weapon.name.lower() == weapon_name),None)
        if weapon_to_sell == None:
            raise util.DueUtilException(channel,"Weapon not found!")
        player.pop_from_invetory(weapon_to_sell)
        
    sell_price = weapon_to_sell.price // price_divisor
    player.money += sell_price
    await util.say(channel,("**"+player.name_clean+"** sold their trusty **"+weapon_to_sell.name_clean
                            +"** for ``"+util.format_number(sell_price,money=True,full_precision=True)+"``"))
    player.save()
        
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
    
