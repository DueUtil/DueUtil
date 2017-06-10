from abc import ABC, abstractmethod
from botstuff import util

"""

Helper classes to make making sell/buy actions faster

"""

class ShopBuySellItem(ABC):
  
    async def sell_item(self,item_name,**details):
        player = details["author"]
        channel = details["channel"]
        price_divisor=4/3
        
        if not item_name in self.store_location(player):
            raise util.DueUtilException(channel,self.item_type_name().title()+" not found!")
        if not self.can_sell(item_name):
            raise util.DueUtilException(channel,"You can't sell that "+self.item_type_name()+"!")
            
        item = self.get_item(item_name)
        sell_price = self.item_price(item) // price_divisor
        self.remove_item(item_name,item,player)
        player.money += sell_price
        await util.say(channel,("**"+player.name_clean+"** sold the "+self.item_type_name()+" **"+item.name_clean
                                +"** for ``"+util.format_number(sell_price,money=True,full_precision=True)+"``"))
        player.save()

    async def buy_item(self,item_name,**details):
        customer = details["author"]
        channel = details["channel"]
        if item_name in self.store_location(customer):
            raise util.DueUtilException(channel,"You already own that "+self.item_type_name())
        item = self.get_item(item_name)
        if item == None:
            raise util.DueUtilException(channel,self.item_type_name().title()+" not found!")
        if not self.can_buy(customer,item):
            return True
        if customer.money - self.item_price(item) > 0:
            customer.money -= self.item_price(item)
            self.store_item(customer,item_name)
            customer.save()
            await util.say(channel,("**"+customer.name_clean+"** bought the "+self.item_type_name()+" **"
                                    +item.name_clean+"** for "
                                    +util.format_number(self.item_price(item),money=True,full_precision=True)))
        else:
            await util.say(channel,":anger: You can't afford that "+self.item_type_name()+".")
            
    def can_buy(self,customer,item):
        return True
    
    @abstractmethod
    def store_item(self,player,item_name):
        pass
    
    @abstractmethod
    def store_location(self,player):
        pass
        
    @abstractmethod
    def get_item(self,item_name):
        pass
        
    @abstractmethod
    def item_price(self,item):
        pass
        
    @abstractmethod
    def item_type_name():
        pass
        
    @abstractmethod
    def can_sell(self,item_name):
        pass   
        
    @abstractmethod
    def remove_item(self,item_name,item,player):
        pass
