import jsonpickle
import json
from botstuff import util, dbconn
from fun.misc import DueUtilObject

NO_WEAPON_ID = "000000000000000000_none"
STOCK_WEAPONS = ["stick","laser gun","gun","none","frisbee"]

weapons = dict()

class Weapon(DueUtilObject):
  
    """A simple weapon that can be used by a monster or player in DueUtil"""
    
    def __init__(self,name,hit_message,damage,accy,**extras):
        message = extras.get('ctx',None)
        if message != None:
            if does_weapon_exist(message.server.id,name):
                raise util.DueUtilException(message.channel,"A weapon with that name already exists on this server!")
            
            if len(name) > 30 or len(name) == 0 or name.strip == "":
                raise util.DueUtilException(message.channel,"Weapon names must be between 1 and 30 characters!")
            
            if accy == 0 or damage == 0:
                raise util.DueUtilException(message.channel,"No weapon stats can be zero!")
        
            if accy > 86 or accy < 1:
                raise util.DueUtilException(message.channel,"Accuracy must be between 1% and 86%!")
                
            if not util.char_is_emoji(emoji.emojize(extras.get('icon',":hocho:"))):
                raise util.DueUtilException(message.channel,":eyes: Weapon icons must be emojis! :ok_hand:")
        
            self.server_id = message.server.id
            
        else:
            self.server_id = "000000000000000000"
        
        self.name = name
        super().__init__(self.__weapon_id(),**extras)    
        self.icon = extras.get('icon',":gun:")
        self.hit_message = hit_message
        self.melee = extras.get('melee',True)
        self.image_url = extras.get('image_url',"https://cdn.discordapp.com/attachments/213007664005775360/280114370560917505/dueuti_deathl.png")
        self.damage = damage
        self.accy = accy
        self.price = self.__price()
        self.weapon_sum = self.__weapon_sum()
        
        self.__add()
            
    @property
    def w_id(self):
        return self.id
    
    def __weapon_id(self):
        return self.server_id+"_"+self.name.lower()
        
    def __weapon_sum(self):
        return '"'+str(self.price)+'"'+str(self.damage)+str(self.accy)
      
    def __price(self):
        return int((self.accy/100 * self.damage) / 0.04375); 
        
    def __add(self):
        global weapons
        weapons[self.w_id] = self
        self.save()
    
def get_weapon_from_id(id):
    if id in weapons:
        return weapons[id]
    else:
        if id != NO_WEAPON_ID:
            return weapons[NO_WEAPON_ID]
                
def does_weapon_exist(server_id,weapon_name):   
    if get_weapon_for_server(server_id,weapon_name) != None:
        return True
    return False
    
def get_weapon_for_server(server_id,weapon_name):
    if weapon_name.lower() in STOCK_WEAPONS:
        return weapons["000000000000000000_"+weapon_name.lower()]
    else:
        weapon_id = server_id+"_"+weapon_name.lower()
        if weapon_id in weapons:
            return weapons[weapon_id]
        else:
            return None
                
def remove_weapon_from_shop(player,wname):
    for weapon in player.owned_weps:
        stored_weapon = get_weapon_from_id(weapon[0])
        if stored_weapon != None and stored_weapon.name.lower() == wname.lower():
            wID = weapon[0]
            sum = weapon[1]
            del player.owned_weps[player.owned_weps.index(weapon)]
            return [wID,sum]
    return None
        
def get_weapons_for_server(id):
    return {weapon_id: weapons[weapon_id] for weapon_id in weapons
            if (weapons[weapon_id].name.lower() in STOCK_WEAPONS
            and weapon_id != NO_WEAPON_ID) or weapon_id.startswith(id)}
            
def load_stock_weapons():
    with open('fun/defaultweapons.json') as defaults_file:  
        defaults = json.load(defaults_file)
    for weapon_data in defaults.values():
        weapon = Weapon(weapon_data["name"],
                        weapon_data["useText"],
                        weapon_data["damage"],
                        weapon_data["accy"],
                        icon = weapon_data["icon"],
                        image_url = weapon_data["image"],
                        melee = weapon_data["melee"],
                        no_save = True)
              
def load():
    global weapons
    none = Weapon('None', None, 1, 66, no_save = True)
    
    load_stock_weapons()
    
    # Load from db    
    for weapon in dbconn.get_collection_for_object(Weapon).find():
        loaded_weapon = jsonpickle.decode(weapon['data'])
        weapons[loaded_weapon.w_id] = util.load_and_update(none,loaded_weapon)
        
load()
