import discord
import inspect
from fun.game import weapons, players
from duecommands import (
    weapons as weap_cmds,
    players as player_cmds)
from botstuff import commands, util
import generalconfig as gconf

from fun.helpers.shop_abstract import ShopBuySellItem


### Fill in the blanks buy/sell functions

class BuySellTheme(ShopBuySellItem):
    item_type = "theme"
    inventory_slot = "themes"

    def item_equipped_on_buy(self, player, item_name):
        if player.equipped["theme"] == "default":
            player.theme = item_name
            return True
        return False

    def get_item(self, item_name):
        return players.get_theme(item_name)


class BuySellBanner(ShopBuySellItem):
    item_type = "banner"
    inventory_slot = "banners"
    default_item = "discord blue"

    def item_equipped_on_buy(self, player, item_name):
        if player.equipped["banner"] == "discord blue":
            player.banner = item_name
            return True
        return False

    def get_item(self, item_name):
        return players.get_banner(item_name)


class BuySellBackground(BuySellTheme):
    item_type = "background"
    inventory_slot = "backgrounds"
    set_name = "bg"

    def item_equipped_on_buy(self, player, item_name):
        if player.equipped["background"] == "default":
            player.background = item_name
            return True
        return False

    def get_item(self, item_name):
        return players.get_background(item_name)


buy_sell_themes = BuySellTheme()
buy_sell_backgrounds = BuySellBackground()
buy_sell_banners = BuySellBanner()


def shop_weapons_list(page, **details):
    shop_weapons = list(weapons.get_weapons_for_server(details["server_id"]).values())
    shop_weapons.remove(weapons.NO_WEAPON)
    shop = weap_cmds.weapons_page(shop_weapons, page, "DueUtil's Weapon Shop!",
                                  footer_more="But wait there's more! Do " + details["cmd_key"] + "shop weapons " + str(
                                      page + 2),
                                  footer_end='Want more? Ask an admin on ' + details["server_name"] + ' to add some!')
    return shop


def shop_theme_list(page, **details):
    themes = list(players.get_themes().values())
    themes.remove(players.get_theme("default"))
    shop = player_cmds.theme_page(themes, page, "DueUtil's Theme Shop!",
                                  footer_more="But wait there's more! Do " + details["cmd_key"] + "shop themes " + str(
                                      page + 2),
                                  footer_end='More themes coming soon!')
    return shop


def shop_background_list(page, **details):
    backgrounds = list(players.backgrounds.values())
    backgrounds.remove(players.backgrounds["default"])
    shop = player_cmds.background_page(backgrounds, page, "DueUtil's Background Shop!",
                                       footer_more="But wait there's more! Do " + details[
                                           "cmd_key"] + "shop bgs " + str(page + 2),
                                       footer_end='More backgrounds coming soon!')
    return shop


def shop_banner_list(page, **details):
    banners = list(players.banners.values())
    banners = [banner for banner in banners if banner.can_use_banner(details["author"]) and banner.id != "discord blue"]
    shop = player_cmds.banner_page(banners, page, "DueUtil's Banner Shop!",
                                   footer_more="But wait there's more! Do " + details[
                                       "cmd_key"] + "shop banners " + str(page + 2),
                                   footer_end='More banners coming soon!')
    return shop


def get_department_from_name(name):
    return next(
        (department_info for department_info in departments.values() if name.lower() in department_info["alisas"]),
        None)


async def item_action(item_name, action, **details):
    exists_check = details.get('exists_check', "item_exists")
    message = details.get('error', "An item with that name exists in multiple departments!")
    # TODO pass full details
    possible_departments = [department_info for department_info in departments.values() if
                            department_info[exists_check](details, item_name)]
    if len(possible_departments) > 1:
        error = (":confounded: " + message + "\n"
                 + "Please be more specific!\n")
        if ' ' in item_name:
            item_name = '"%s"' % item_name
        for department_info in possible_departments:
            error += "``" + details["cmd_key"] + details["command_name"] + " " + department_info["alisas"][
                0] + " " + item_name + "``\n"
        await util.say(details["channel"], error)
    elif len(possible_departments) == 0:
        raise util.DueUtilException(details["channel"], "Item not found!")
    else:
        department = possible_departments[0]
        action = department["actions"][action]
        if inspect.iscoroutinefunction(action):
            action_result = await action(item_name, **details)
        else:
            action_result = action(item_name, **details)
        if isinstance(action_result, discord.Embed):
            await util.say(details["channel"], embed=action_result)


def _placeholder(_, **details):
    embed = details["embed"]
    embed.title = "Department closed"
    return embed


departments = {
    "weapons": {
        "alisas": [
            "weapons",
            "weaps",
            "weap",
            "weapon"
        ],
        "actions": {
            "info_action": weap_cmds.weapon_info,
            "list_action": shop_weapons_list,
            "buy_action": weap_cmds.buy_weapon,
            "sell_action": weap_cmds.sell_weapon
        },
        "item_exists": lambda details, name: name.lower() != "none" and weapons.does_weapon_exist(details["server_id"],
                                                                                                  name),
        "item_exists_sell": lambda details, name: (name != "none" and details["author"].weapon.name.lower() == name
                                                   or details["author"].owns_weapon(name))
    },
    "themes": {
        "alisas": [
            "themes",
            "skins",
            "theme",
            "skin"
        ],
        "actions": {
            "info_action": player_cmds.theme_info,
            "list_action": shop_theme_list,
            "buy_action": buy_sell_themes.buy_item,
            "sell_action": buy_sell_themes.sell_item
        },
        "item_exists": lambda _, name: name.lower() != "default" and players.get_theme(name) is not None,
        "item_exists_sell": lambda details, name: name.lower() in details["author"].inventory["themes"]

    },
    "backgrounds": {
        "alisas": [
            "backgrounds",
            "bgs",
            "bg",
            "background"
        ],
        "actions": {
            "info_action": player_cmds.background_info,
            "list_action": shop_background_list,
            "buy_action": buy_sell_backgrounds.buy_item,
            "sell_action": buy_sell_backgrounds.sell_item
        },
        "item_exists": lambda _, name: name.lower() != "default" and name.lower() in players.backgrounds,
        "item_exists_sell": lambda details, name: name.lower() in details["author"].inventory["backgrounds"]
    },
    "banners": {
        "alisas": [
            "banners",
            "banner"
        ],
        "actions": {
            "info_action": player_cmds.banner_info,
            "list_action": shop_banner_list,
            "buy_action": buy_sell_banners.buy_item,
            "sell_action": buy_sell_banners.sell_item
        },
        "item_exists": lambda details,
                              name: name.lower() != "discord blue" and name.lower() in players.banners and players.get_banner(
            name).can_use_banner(details["author"]),
        "item_exists_sell": lambda details, name: name.lower() in details["author"].inventory["banners"]
    }
}


@commands.command(args_pattern='S?M?')
async def shop(ctx, *args, **details):
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
    
    **Note**: You must always use quotes around item names
    that have spaces with this command due to it's internal workings.
    """

    shop = discord.Embed(type="rich", color=gconf.EMBED_COLOUR)
    details["embed"] = shop

    if len(args) == 0:
        greet = ":wave: **Welcome to the DueUtil general store!**\n"
        department_available = "Please have a look in some of our splendiferous departments!\n"
        for department_info in departments.values():
            department_available += "``" + details["cmd_key"] + "shop " + department_info["alisas"][0] + "``\n"
        help = "For more info on the new shop do ``" + details["cmd_key"] + "help shop``"
        await util.say(ctx.channel, greet + department_available + help)
    else:
        department = get_department_from_name(args[0])
        if department is not None:
            list_action = department["actions"]["list_action"]
            info_action = department["actions"]["info_action"]
            if len(args) == 1:
                await util.say(ctx.channel, embed=list_action(0, **details))
            else:
                if type(args[1]) is int:
                    await util.say(ctx.channel, embed=list_action(args[1] - 1, **details))
                else:
                    await util.say(ctx.channel, embed=info_action(args[1], **details))
        elif len(args) == 1:
            await item_action(args[0].lower(), "info_action", **details)
        else:
            raise util.DueUtilException(ctx.channel, "Department not found")


@commands.command(args_pattern='SS?')
async def buy(ctx, *args, **details):
    """
    [CMD_KEY]buy item

    **Note**: You must always use quotes around item names
    that have spaces with this command due to it's internal workings.
    """

    if len(args) == 1:
        await item_action(args[0].lower(), "buy_action", **details)
    else:
        department = get_department_from_name(args[0])
        if department is not None:
            await department["actions"]["buy_action"](args[1].lower(), **details)
        else:
            raise util.DueUtilException(ctx.channel, "Department not found")


@commands.command(args_pattern='SS?')
async def sell(ctx, *args, **details):
    """
    [CMD_KEY]sell item
    
    **Note**: You must always use quotes around item names
    that have spaces with this command due to it's internal workings.
    """
    error = "You own multiple items with the same name!"

    if len(args) == 1:
        await item_action(args[0].lower(), "sell_action", **details, exists_check="item_exists_sell", error=error)
    else:
        department = get_department_from_name(args[0])
        if department is not None:
            await department["actions"]["sell_action"](args[1].lower(), **details, exists_check="item_exists_sell",
                                                       error=error)
        else:
            raise util.DueUtilException(ctx.channel, "Department not found")
