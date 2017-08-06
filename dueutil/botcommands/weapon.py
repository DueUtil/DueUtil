import discord

import generalconfig as gconf
from ..game import players
from ..permissions import Permission
from ..game import battles, weapons, stats, awards
from ..game.helpers import imagehelper, misc
from .. import commands, util


@commands.command(args_pattern='M?')
async def myweapons(ctx, *args, **details):
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
        title = player.get_name_possession_clean() + " Weapons" + (" : Page " + str(page + 1) if page > 0 else "")
        if len(player_weapons) > 0:
            weapon_store = weapons_page(player_weapons, page, title, price_divisor=4 / 3)
        else:
            weapon_store = discord.Embed(title=title, type="rich", color=gconf.EMBED_COLOUR)
            weapon_store.add_field(name="No weapons stored!",
                                   value="You can buy up to 6 more weapons from the shop and store them here!")
        weapon_store.description = "Currently equipped: " + str(player.weapon)
        weapon_store.set_footer(text="Do " + details["cmd_key"] + "equip (weapon name) to equip a weapon.")
        await util.say(ctx.channel, embed=weapon_store)
    else:
        weapon_name = page
        if player.equipped["weapon"] != weapons.NO_WEAPON_ID:
            player_weapons.append(player.weapon)
        weapon = next((weapon for weapon in player_weapons if weapon.name.lower() == weapon_name.lower()), None)
        if weapon is not None:
            embed = discord.Embed(type="rich", color=gconf.EMBED_COLOUR)
            info = weapon_info(**details, weapon=weapon, price_divisor=4 / 3, embed=embed)
            await util.say(ctx.channel, embed=info)
        else:
            raise util.DueUtilException(ctx.channel, "You don't have a weapon with that name!")


@commands.command(args_pattern="S?")
async def unequip(ctx, _=None, **details):
    """
    [CMD_KEY]unequip
    
    Unequips your current weapon
    """

    player = details["author"]
    weapon = player.weapon
    if weapon.w_id == weapons.NO_WEAPON_ID:
        raise util.DueUtilException(ctx.channel, "You don't have anything equipped anyway!")
    if len(player.inventory["weapons"]) >= 6:
        raise util.DueUtilException(ctx.channel, "No room in your weapon storage!")
    if player.owns_weapon(weapon.name):
        raise util.DueUtilException(ctx.channel, "You already have a weapon with that name stored!")

    player.store_weapon(weapon)
    player.weapon = weapons.NO_WEAPON_ID
    player.save()
    await util.say(ctx.channel, ":white_check_mark: **" + weapon.name_clean + "** unequipped!")


@commands.command(args_pattern='S')
async def equip(ctx, weapon_name, **details):
    """
    [CMD_KEY]equip (weapon name)
    
    Equips a weapon from your weapon inventory.
    """

    player = details["author"]
    current_weapon = player.weapon
    weapon_name = weapon_name.lower()

    weapon = player.get_weapon(weapon_name)
    if weapon is None:
        if weapon_name != current_weapon.name.lower():
            raise util.DueUtilException(ctx.channel, "You do not have that weapon stored!")
        await util.say(ctx.channel, "You already have that weapon equipped!")
        return

    player.discard_stored_weapon(weapon)
    if player.owns_weapon(current_weapon.name):
        player.store_weapon(weapon)
        raise util.DueUtilException(ctx.channel, ("Can't put your current weapon into storage!\n"
                                                  + "There is already a weapon with the same name stored!"))

    if current_weapon.w_id != weapons.NO_WEAPON_ID:
        player.store_weapon(current_weapon)

    player.weapon = weapon
    player.save()

    await util.say(ctx.channel, ":white_check_mark: **" + weapon.name_clean + "** equipped!")


@misc.paginator
def weapons_page(weapons_embed, weapon, **extras):
    price_divisor = extras.get('price_divisor', 1)
    weapons_embed.add_field(name=str(weapon),
                            value='``' + util.format_number(weapon.price // price_divisor, full_precision=True,
                                                            money=True) + '``')


@commands.command(args_pattern='PP?')
@commands.imagecommand()
async def battle(ctx, *args, **details):
    """
    [CMD_KEY]battle player (optional other player)
    
    Battle someone!
    
    Note! You don't again any exp or reward from these battles!
    Please do not spam anyone with unwanted battles.
    """
    # TODO: Handle draws
    player = details["author"]
    if len(args) == 2 and args[0] == args[1] or len(args) == 1 and player == args[0]:
        # TODO Check if args are the author or random player
        raise util.DueUtilException(ctx.channel, "Don't beat yourself up!")
    if len(args) == 2:
        player_one = args[0]
        player_two = args[1]
    else:
        player_one = player
        player_two = args[0]

    battle_log = battles.get_battle_log(player_one=player_one, player_two=player_two)

    await imagehelper.battle_screen(ctx.channel, player_one, player_two)
    await util.say(ctx.channel, embed=battle_log.embed)
    if battle_log.winner is None:
        # Both players get the draw battle award
        awards.give_award(ctx.channel, player_one, "InconceivableBattle")
        awards.give_award(ctx.channel, player_two, "InconceivableBattle")
    await battles.give_awards_for_battle(ctx.channel, battle_log)


@commands.command(args_pattern='PC', aliases=("wager",))
async def wagerbattle(ctx, receiver, money, **details):
    """
    [CMD_KEY]wagerbattle player amount
    
    Money will not be taken from your account after you use this command.
    If you cannot afford to pay when the wager is accepted you will be forced
    to sell your weapons.
    """
    sender = details["author"]

    if sender == receiver:
        raise util.DueUtilException(ctx.channel, "You can't wager against yourself!")

    if sender.money - money < 0:
        raise util.DueUtilException(ctx.channel, "You can't afford this wager!")

    battles.BattleRequest(sender, receiver, money)

    await util.say(ctx.channel, ("**" + sender.name_clean + "** wagers **" + receiver.name_clean + "** ``"
                                 + util.format_number(money, full_precision=True,
                                                      money=True) + "`` that they will win in a battle!"))


@commands.command(args_pattern='C?')
async def mywagers(ctx, page=1, **details):
    """
    [CMD_KEY]mywagers (page)
    
    Lists your received wagers.
    """

    # TODO: Update this command to paginator?

    player = details["author"]
    page_size = 12
    page -= 1
    title = player.get_name_possession_clean() + " Received Wagers" + (" : Page " + str(page + 1) if page > 0 else "")
    wagers_embed = discord.Embed(title=title, type="rich", color=gconf.EMBED_COLOUR)
    wager_list = player.received_wagers
    if len(wager_list) > 0:
        if page * page_size >= len(wager_list):
            raise util.DueUtilException(ctx.channel, "Page not found")
        for wager_index in range(page_size * page, page_size * page + page_size):
            if wager_index >= len(wager_list):
                break
            wager = wager_list[wager_index]
            sender = players.find_player(wager.sender_id)
            wagers_embed.add_field(name=str(wager_index + 1) + ". Request from " + sender.name_clean,
                                   value="<@" + sender.id + "> ``" + util.format_number(wager.wager_amount,
                                                                                        full_precision=True,
                                                                                        money=True) + "``")
        wagers_embed.add_field(name="Actions",
                               value=("Do ``" + details["cmd_key"] + "acceptwager (number)`` to accept a wager \nor ``"
                                      + details["cmd_key"] + "declinewager (number)`` to decline"), inline=False)
        if page_size * page + page_size < len(wager_list):
            footer = "But wait there's more! Do " + details["cmd_key"] + "mywagers " + str(page + 2)
        else:
            footer = 'That is all!'
        wagers_embed.set_footer(text=footer)
    else:
        wagers_embed.add_field(name="No wagers received!",
                               value="Wager requests you get from other players will appear here.")
    await util.say(ctx.channel, embed=wagers_embed)


@commands.command(args_pattern='C')
@commands.imagecommand()
async def acceptwager(ctx, wager_index, **details):
    """
    [CMD_KEY]acceptwager (wager number)
    
    Accepts a wager!
    """
    # TODO: Handle draws
    player = details["author"]
    wager_index -= 1
    if wager_index >= len(player.received_wagers):
        raise util.DueUtilException(ctx.channel, "Request not found!")
    if player.money - player.received_wagers[wager_index].wager_amount < 0:
        raise util.DueUtilException(ctx.channel, "You can't afford the risk!")

    wager = player.received_wagers.pop(wager_index)
    sender = players.find_player(wager.sender_id)
    battle_log = battles.get_battle_log(player_one=player, player_two=sender)
    battle_embed = battle_log.embed
    winner = battle_log.winner
    loser = battle_log.loser
    wager_amount_str = util.format_number(wager.wager_amount, full_precision=True, money=True)
    total_transferred = wager.wager_amount
    if winner == sender:
        wager_results = (":skull: **" + player.name_clean + "** lost to **"
                         + sender.name_clean + "** and paid ``" + wager_amount_str + "``")
        player.money -= wager.wager_amount
        sender.money += wager.wager_amount
        sender.wagers_won += 1
    elif winner == player:
        player.wagers_won += 1
        if sender.money - wager.wager_amount >= 0:
            payback = ("**" + sender.name_clean + "** paid **" + player.name_clean + "** ``"
                       + wager_amount_str + "``")
            player.money += wager.wager_amount
            sender.money -= wager.wager_amount
        else:
            weapons_sold = 0
            if sender.equipped["weapon"] != weapons.NO_WEAPON_ID:
                weapons_sold += 1
                sender.money += sender.weapon.get_summary().price // (4 / 3)
                sender.weapon = weapons.NO_WEAPON_ID
            if sender.money - wager.wager_amount < 0:
                for weapon in sender.get_owned_weapons():
                    weapon_price = weapon.get_summary().price
                    sender.money += weapon_price // (4 / 3)
                    weapons_sold += 1
                    if sender.money - wager.wager_amount >= 0:
                        break
            amount_not_paid = max(0, wager.wager_amount - sender.money)
            amount_paid = wager.wager_amount - amount_not_paid
            amount_paid_str = util.format_number(amount_paid, full_precision=True, money=True)

            if weapons_sold == 0:
                payback = ("**" + sender.name_clean + "** could not afford to pay and had no weapons to sell! \n``"
                           + amount_paid_str + "`` is all they could pay.")
            else:
                payback = ("**" + sender.name_clean + "** could not afford to pay and had to sell "
                           + str(weapons_sold) + " weapon" + ("s" if weapons_sold != 1 else "") + " \n")
                if amount_paid != wager.wager_amount:
                    payback += "They were still only able to pay ``" + amount_paid_str + "``. \nPathetic."
                else:
                    payback += "They were able to muster up the full ``" + amount_paid_str + "``"
            sender.money -= amount_paid
            player.money += amount_paid
            total_transferred = amount_paid
        wager_results = (":sparkles: **"
                         + player.name_clean
                         + "** won against **"
                         + sender.name_clean + "**!\n" + payback)
    else:
        wager_results = "Against all the odds the wager ended in a draw!"
    stats.increment_stat(stats.Stat.MONEY_TRANSFERRED, total_transferred)
    battle_embed.add_field(name="Wager results", value=wager_results, inline=False)
    await imagehelper.battle_screen(ctx.channel, player, sender)
    await util.say(ctx.channel, embed=battle_embed)
    if winner is not None:
        await awards.give_award(ctx.channel, winner, "YouWin", "Win a wager")
        await awards.give_award(ctx.channel, loser, "YouLose", "Lose a wager!")
        if winner.wagers_won == 2500:
            await awards.give_award(ctx.channel, winner, "2500Wagers")
    else:
        await  awards.give_award(ctx.channel, player, "InconceivableWager")
        await  awards.give_award(ctx.channel, sender, "InconceivableWager")
    await battles.give_awards_for_battle(ctx.channel, battle_log)
    sender.save()
    player.save()


@commands.command(args_pattern='C')
async def declinewager(ctx, wager_index, **details):
    """
    [CMD_KEY]declinewager (wager number)
    
    Declines a wager.
    """

    player = details["author"]
    wager_index -= 1
    if wager_index < len(player.received_wagers):
        wager = player.received_wagers[wager_index]
        del player.received_wagers[wager_index]
        player.save()
        sender = players.find_player(wager.sender_id)
        await util.say(ctx.channel, "**" + player.name_clean + "** declined a wager from **" + sender.name_clean + "**")

    else:
        raise util.DueUtilException(ctx.channel, "Request not found!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SSCCB?S?S?')
async def createweapon(ctx, name, hit_message, damage, accy, ranged=False, icon='🔫', image=None, **_):
    """
    [CMD_KEY]createweapon "weapon name" "hit message" damage accy
    
    Creates a weapon for the server shop!
    
    For extra customization you add the following:
    
    (ranged) (icon) (image url)
    
    __Example__: 
    Basic Weapon:
        ``[CMD_KEY]createweapon "Laser" "FIRES THEIR LAZOR AT" 100 50``
        This creates a weapon named "Laser" with the hit message
        "FIRES THEIR LAZOR AT", 100 damage and 50% accy
    Advanced Weapon:
        ``[CMD_KEY]createweapon "Banana Gun" "splats" 12 10 True :banana: http://i.imgur.com/6etFBta.png``
        The first four properties work like before. This weapon also has ranged set to ``true``
        as it fires projectiles, a icon (for the shop) ':banana:' and image of the weapon from the url.
    """

    extras = dict()
    extras['melee'] = not ranged
    extras['icon'] = icon
    if image is not None:
        extras['image_url'] = image

    weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
    await util.say(ctx.channel, (weapon.icon + " **" + weapon.name_clean + "** is available in the shop for "
                                 + util.format_number(weapon.price, money=True) + "!"))


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='S')
async def removeweapon(ctx, weapon_name, **_):
    """
    [CMD_KEY]removeweapon (weapon name)
    
    Screw all the people that bought it :D
    """

    weapon_name = weapon_name.lower()
    weapon = weapons.get_weapon_for_server(ctx.server.id, weapon_name)
    if weapon is None or weapon.id == weapons.NO_WEAPON_ID:
        raise util.DueUtilException(ctx.channel, "Weapon not found")
    if weapon.id != weapons.NO_WEAPON_ID and weapons.stock_weapon(weapon_name) != weapons.NO_WEAPON_ID:
        raise util.DueUtilException(ctx.channel, "You can't remove stock weapons!")
    weapons.remove_weapon_from_shop(ctx.server, weapon_name)
    await util.say(ctx.channel, "**" + weapon.name_clean + "** has been removed from the shop!")


# Part of the shop buy command
async def buy_weapon(weapon_name, **details):
    customer = details["author"]
    weapon = weapons.get_weapon_for_server(details["server_id"], weapon_name)
    channel = details["channel"]

    if weapon is None or weapon_name == "none":
        raise util.DueUtilException(channel, "Weapon not found")
    if customer.money - weapon.price < 0:
        await util.say(channel, ":anger: You can't afford that weapon.")
    elif weapon.price > customer.item_value_limit:
        await util.say(channel, (":baby: Awwww. I can't sell you that.\n"
                                 + "You can use weapons with a value up to **"
                                 + util.format_number(customer.item_value_limit, money=True,
                                                      full_precision=True) + "**"))
    elif customer.equipped["weapon"] != weapons.NO_WEAPON_ID:
        if len(customer.inventory["weapons"]) < 6:
            if weapon.w_id not in customer.inventory["weapons"]:
                customer.store_weapon(weapon)
                customer.money -= weapon.price
                await util.say(channel, ("**" + customer.name_clean + "** bought a **" + weapon.name_clean + "** for "
                                         + util.format_number(weapon.price, money=True, full_precision=True)
                                         + "\n:warning: You have not equipped this weapon! Do **"
                                         + details["cmd_key"] + "equip "
                                         + weapon.name_clean.lower() + "** to equip this weapon."))
            else:
                raise util.DueUtilException(channel,
                                            "Cannot store new weapon! A you already have a weapon with the same name!")
        else:
            raise util.DueUtilException(channel, "No free weapon slots!")
    else:
        customer.weapon = weapon
        customer.money -= weapon.price
        await util.say(channel, ("**" + customer.name_clean + "** bought a **"
                                 + weapon.name_clean + "** for " + util.format_number(weapon.price, money=True,
                                                                                      full_precision=True)))
        await awards.give_award(channel, customer, "Spender", "Licence to kill!")
    customer.save()


async def sell_weapon(weapon_name, **details):
    player = details["author"]
    channel = details["channel"]

    price_divisor = 4 / 3
    player_weapon = player.weapon
    if player_weapon != weapons.NO_WEAPON and player_weapon.name.lower() == weapon_name:
        weapon_to_sell = player.weapon
        player.weapon = weapons.NO_WEAPON_ID
    else:
        weapon_to_sell = next((weapon for weapon in player.get_owned_weapons() if weapon.name.lower() == weapon_name),
                              None)
        if weapon_to_sell is None:
            raise util.DueUtilException(channel, "Weapon not found!")
        player.discard_stored_weapon(weapon_to_sell)

    sell_price = weapon_to_sell.price // price_divisor
    player.money += sell_price
    await util.say(channel, ("**" + player.name_clean + "** sold their trusty **" + weapon_to_sell.name_clean
                             + "** for ``" + util.format_number(sell_price, money=True, full_precision=True) + "``"))
    player.save()


def weapon_info(weapon_name=None, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    weapon = details.get('weapon')
    if weapon is None:
        weapon = weapons.get_weapon_for_server(details["server_id"], weapon_name)
        if weapon is None:
            raise util.DueUtilException(details["channel"], "Weapon not found")
    embed.title = weapon.icon + ' | ' + weapon.name_clean
    embed.set_thumbnail(url=weapon.image_url)
    embed.add_field(name='Damage', value=util.format_number(weapon.damage))
    embed.add_field(name='Accuracy', value=util.format_number(weapon.accy * 100) + '%')
    embed.add_field(name='Price',
                    value=util.format_number(weapon.price // price_divisor, money=True, full_precision=True))
    embed.add_field(name="Hit Message", value=weapon.hit_message)
    embed.set_footer(text='Image supplied by weapon creator.')
    return embed
