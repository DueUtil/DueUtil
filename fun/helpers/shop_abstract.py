from abc import ABC, abstractmethod
from botstuff import util

"""

Helper classes to make making sell/buy actions faster

"""


class ShopBuySellItem(ABC):
    """
    This class is designed to make creating sell/buy 
    commands faster. Given that the items work like themes/backgrounds/banners
    
    They must use player.equipped & player.inventory
    & have some properties with setters.
    
    It also assumes the use of !my<thing> and !set<thing> 
    commands
    
    """

    # Set these values
    item_type = ""
    inventory_slot = ""
    default_item = "default"

    async def sell_item(self, item_name, **details):
        player = details["author"]
        channel = details["channel"]
        price_divisor = 4 / 3

        if item_name not in player.inventory[self.inventory_slot]:
            raise util.DueUtilException(channel, self.item_type.title() + " not found!")
        if item_name == self.default_item:
            raise util.DueUtilException(channel, "You can't sell that " + self.item_type + "!")

        item = self.get_item(item_name)
        sell_price = item.price // price_divisor
        setattr(player, self.item_type, self.default_item)
        player.inventory[self.inventory_slot].remove(item_name)
        player.money += sell_price
        await util.say(channel, ("**" + player.name_clean + "** sold the " + self.item_type + " **" + item.name_clean
                                 + "** for ``" + util.format_number(sell_price, money=True,
                                                                    full_precision=True) + "``"))
        player.save()

    async def buy_item(self, item_name, **details):
        customer = details["author"]
        channel = details["channel"]
        if item_name in customer.inventory[self.inventory_slot]:
            raise util.DueUtilException(channel, "You already own that " + self.item_type)
        item = self.get_item(item_name)
        if item is None:
            raise util.DueUtilException(channel, self.item_type.title() + " not found!")
        if not self.can_buy(customer, item):
            return True
        if customer.money - item.price > 0:
            customer.money -= item.price
            customer.inventory[self.inventory_slot].append(item_name)
            if self.item_equipped_on_buy(customer, item_name):
                await util.say(channel, ("**%s** bought the %s **%s** for %s"
                                         % (customer.name_clean, self.item_type, item.name_clean,
                                            util.format_number(item.price, money=True, ull_precision=True))))
            else:
                await util.say(channel, (("**%s** bought the %s **%s** for %s\n"
                                          + ":warning: You have not yet set this %s! Do **%sset%s %s** to use this %s")
                                         % (customer.name_clean, self.item_type, item.name_clean,
                                            util.format_number(item.price, money=True, full_precision=True),
                                            self.item_type, details["cmd_key"],
                                            self.set_name if hasattr(self, "set_name") else self.item_type,
                                            item_name, self.item_type)))
            customer.save()
        else:
            await util.say(channel, ":anger: You can't afford that " + self.item_type + ".")

    def can_buy(self, customer, item):
        return True

    @abstractmethod
    def item_equipped_on_buy(self, player, item_name):

        """
        Equips the item if possible
        Returns true/false
        """

        pass

    @abstractmethod
    def get_item(self, item_name):
        pass
