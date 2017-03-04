import discord;
import jsonpickle;
import json;
import math;
import random 
import numpy
import emoji; #The emoji list in this is outdated.
from botstuff import dbconn,util;
from PIL import Image, ImageDraw, ImageFont

players = dict();         
awards = [];
banners = dict();         
backgrounds = dict();     
servers_quests = dict();  
weapons = dict();   
    
class Player:
  
    """The DueUtil player!"""
  
    def __init__(self,*args):
        global players,new_players_joined;
        self.user_id = args[0].id if len(args) > 0 and isinstance(args[0],discord.Member) else "";
        self.reset();
        players[self.user_id] = self;
        Stats.new_players_joined += 1;

    def reset(self):
        self.benfont = False;
        self.level = 1;
        self.attack = 1;
        self.strg = 1;
        self.accy = 1;
        self.banner_id = "discord blue";
        self.hp = 10;
        self.donor = False;
        self.background = "default.png";
        self.weapon_sum = '"0"01'     #price/attack/sum;
        self.name = "😂😂😂😂😂 adssd";
        self.w_id = Weapons.NO_WEAPON_ID;
        self.money = 100000;
        self.last_progress = 0;
        self.last_quest = 0;
        self.wagers_won = 0;
        self.quests_won = 0;
        self.potatos_given = 0;
        self.quest_day_start = 0;
        self.potatos = 0;
        self.quests_completed_today = 0;
        self.last_image_request = 0;
        self.quests = [];
        self.battlers = [];
        self.awards = [];
        self.weapon_inventory = [];
        self.save();
        
    def owns_weapon(self,weapon_name):
        for weapon_slot in self.owned_weps:
            if(Weapon.get_weapon_from_id(weapon_slot[0]).name.lower() == weapon_name.lower()):
                return True;
        return False;
        
    @property    
    def weapon_accy(self):
        max_value = self.item_value_limit;
        price = self.weapon.price if self.weapon.price > 0 else 1;
        new_accy = numpy.clip(max_value/price * 100,1,86);
        new_accy = self.weapon.accy if new_accy > self.weapon.accy else new_accy;
        return new_accy if price > max_value else self.weapon.accy;
    
    def weapon_hit(self):
        return random.random()<(self.weapon_accy/100);
    
    @property
    def clean_name(self):
        print (self.name.decode('utf-8'))
        return "";
    
    @property
    def item_value_limit(self):
        return math.inf
        return 10 * (math.pow(self.level,2)/3 + 0.5 * math.pow(self.level+1,2) * self.level);
            
    async def unequip_weapon(self,channel):
        if weapon.w_id != no_weapon_id:
            if len(self.owned_weps) < 6:
                if not self.owns_weapon(self.weapon.name):
                    self.owned_weps.append([active_wep.wID,self.weapon_sum]);
                    self.wID = no_weapon_id;
                    self.weapon_sum = weapons(no_weapon_id).weapon_sum;
                    await util.say(channel, ":white_check_mark: **"+active_wep.name+"** unequiped!");
                else:
                    raise util.DueUtilException(channel,"You already have a weapon with that name stored!"); 
            else:
                raise util.DueUtilException(channel, "No room in your weapon storage!");
        else:
            raise util.DueUtilException(channel,"You don't have anything equiped anyway!");
            
    def save(self):
        dbconn.insert_object(self.user_id,self);

    @property
    def weapon(self):
        return weapons[self.w_id];
        
    @property
    def rank(self):
        return int(self.level / 10) + 1;
        
    @property
    def rank_colour(self):
        if(self.rank == 1):
            return (255, 255, 255);
        elif (self.rank == 2):
            return (235, 196, 42);
        elif (self.rank == 3):
            return (235, 145, 42);
        elif (self.rank == 4):
            return (42, 235, 68);
        elif (self.rank == 5):
            return (174, 42, 235);
        elif (self.rank == 6):
            return (42, 103, 235);
        elif (self.rank == 7):
            return (163, 102, 90);
        elif (self.rank == 8):
            return (224, 33, 11);
        elif (self.rank > 8):
            return (15, 15, 15);
        return (255, 255, 255); 
        
    @property
    def banner(self):
        banner = banners.get(self.banner_id,banners["discord blue"]);
        if not banner.can_use_banner(self):
            player.banner_id = "discord blue";
            return banners["discord blue"];
        return banner;
        
    @property
    def clean_name(self):
        return util.filter_string(self.name);
        
    def get_avatar_url(self,*args):
        server = args[0];
        member = server.get_member(self.user_id);
        if member.avatar_url != "":
           return member.avatar_url;
        else:
           return member.default_avatar_url;
        
class Weapon:
  
    """A simple weapon that can be used by a monster or player in DueUtil"""
    
    def __init__(self,name,hit_message,damage,accy,**extras):
        message = extras.get('ctx',None);
        if message != None:
            if Weapons.does_weapon_exist(message.server.id,name):
                raise util.DueUtilException(message.channel,"A weapon with that name already exists on this server!");
            
            if len(name) > 30 or len(name) == 0 or name.strip == "":
                raise util.DueUtilException(message.channel,"Weapon names must be between 1 and 30 characters!");
            
            if accy == 0 or damage == 0:
                raise util.DueUtilException(message.channel,"No weapon stats can be zero!");
        
            if accy > 86 or accy < 1:
                raise util.DueUtilException(message.channel,"Accuracy must be between 1% and 86%!");
                
            if not util.char_is_emoji(emoji.emojize(extras.get('icon',":hocho:"))):
                raise util.DueUtilException(message.channel,":eyes: Weapon icons must be emojis! :ok_hand:");
        
            self.server_id = message.server.id;
            
        else:
            self.server_id = "000000000000000000";
            
        self.icon = extras.get('icon',":gun:")
        self.hit_message = hit_message;
        self.melee = extras.get('melee',True);
        self.image_url = extras.get('image_url',"https://cdn.discordapp.com/attachments/213007664005775360/280114370560917505/dueuti_deathl.png");
  
        self.name = name;
        self.damage = damage;
        self.accy = accy;
        self.price = self.__price();
        self.w_id = self.__weapon_id();
        self.weapon_sum = self.__weapon_sum();
        
        self.__add();
            
    def __weapon_id(self):
        return self.server_id+"_"+self.name.lower();
        
    def __weapon_sum(self):
        return '"'+str(self.price)+'"'+str(self.damage)+str(self.accy);
      
    def __price(self):
        return int((self.accy/100 * self.damage) / 0.04375); 
        
    def __add(self):
        global weapons;
        weapons[self.w_id] = self;
        self.save();
        
    def save(self):
        dbconn.insert_object(self.w_id,self);
            
class BattleRequest:
  
    """A class to hold a wager"""
  
    def __init__(self,message,wager_amount):
        self.sender_id = message.author.id;
        self.wager_amount = wagers_amount;

class Quest:
  
    """A class to hold info about a server quest"""
  
    def __init__(self,name,base_attack,base_strg,base_accy,base_hp,**extras):
        message = extras.get('ctx',None);
      
        if message != None:
            if message.server.id in server_quests:
                if name.strip().lower() in server_quests[message.server.id]:
                    raise util.DueUtilException(message.channel,"A foe with that name already exists on this server!");
      
            if base_accy < 1 or base_attack < 1 or base_strg < 1:
                raise util.DueUtilException(message.channel,"No quest stats can be less than 1!");

            if base_hp < 30:
                raise util.DueUtilException(message.channel,"Base HP must be at least 30!");

            if len(name) > 30 or len(name) == 0 or name.strip == "":
                raise util.DueUtilException(message.channel,"Quest names must be between 1 and 30 characters!");
                
            self.server_id = message.server.id;
            self.created_by = message.author.id;
        else:
            self.server_id = "";
            self.created_by = "";
      
        self.task = extras.get('task',"Battle a");
        self.w_id = extras.get('weapon_id',Weapons.NO_WEAPON_ID);
        self.spawn_chance = extras.get('spawn_chance',4);
        self.image_url = extras.get('image_url',"");
        
        self.monster_name = name;
        self.base_attack = base_attack;
        self.base_strg = base_strg;
        self.base_accy = base_accy;
        self.base_hp = base_hp;
        
        
        self.base_reward = 0 #self__reward();
        self.q_id = self.__quest_id();
        
        if self.server_id != "":
            self.__add();
        
    @property    
    def creator(self):
        game.Player.find_player(quest_info.created_by);
    
    @property
    def home(self):
        try:
            util.get_client(self.server_id).get_server(server_id);
        except:
            return None;
        
    def __quest_id(self):
        return self.server_id+'/'+self.monster_name.lower();
      
    def __reward(self):
        if(Weapon.get_weapon_from_id(self.w_id).melee):
            base_reward = (self.base_attack + self.base_strg) / 10 / 0.0883;
        else:
            base_reward = (self.base_accy + self.base_strg) / 10 / 0.0883;
    
        base_reward += base_reward * math.log10(self.base_hp) / 20 / 0.75;
        base_reward *= self.base_hp / abs(self.base_hp - 0.01);
        
        return base_reward;
                        
    def __add(self):
        global servers_quests
        location = self.q_id.split('/',1)
        servers_quests[location[0]][location[1]]
    
    @property
    def made_on(self):
        return self.server_id;
        
    def save(self):
        dbconn.insert_object(self.q_id,self);
        
class ActiveQuest(Player):
  
    def __init__(self,q_id):
        self.q_id = q_id;
        super(ActiveQuest,self).__init__();
        
    def get_avatar_url(self,*args):
        return self.info.image_url;
  
    @property
    def info(self):
        try:
            quest_id = self.q_id.split('/',1);
            return ServersQuests[quest_id[0]][quest_id[1]];
        except:
            return None;

class Award:

    def __init__(self,icon_path,name,description):
        self.name = name;
        self.description = description;
        self.icon = Image.open(icon_path);

class PlayerInfoBanner:
    
    """Class to hold details & methods for a profile banner"""
    
    def __init__(self,name,image_name,**kwargs):
      
        self.price = kwargs.get('price',0);
        self.donor = kwargs.get('donor',False);
        self.admin_only = kwargs.get('admin_only',False);
        self.mod_only = kwargs.get('mod_only',False);
        self.unlock_level = kwargs.get('unlock_level',0);
        self.image = None
        self.image_name = image_name;
        self.name = name;
                
    def banner_restricted(self,player):
        return ((not self.admin_only or self.admin_only == util.is_admin(player.userid)) 
                and (not self.mod_only or self.mod_only == util.is_mod_or_admin(player.userid)));
        
        
    def can_use_banner(self,player):
        return (not self.donor or self.donor == self.donor) and self.banner_restricted(player);
        
    def save(self):
        dbconn.insert_object(self.name.lower().replace(" ","_"),self);

class Awards:
  
    @staticmethod
    def register(icon_path,text):
        global awards;
        info = text.split('\n');
        awards.append(Award(icon_path,info[0],info[1]));
        
    @staticmethod
    def get_award(award_id):
        return awards[award_id]; 

    @staticmethod          
    def load():
        Awards.register("awards/Duseless.png","Duseless\nIgnore DueUtil");  # 0
        Awards.register("awards/questDone.png","Save The Server\nComplete a quest");  # 1
        Awards.register("awards/rank2.png","Attain Rank 2\nGet to level 10");  # 2
        Awards.register("awards/redmist.png","Red Mist\nFail a quest");  # 3
        Awards.register("awards/spender.png","Licence To Kill\nBuy a weapon");  # 4
        Awards.register("awards/rank3.png","Attain Rank 3\nGet to level 20");  # 5
        Awards.register("awards/rank4.png","Attain Rank 4\nGet to level 30");  # 6
        Awards.register("awards/rank5.png","Attain Rank 5\nGet to level 40");  # 7
        Awards.register("awards/rank6.png","Attain Rank 6\nGet to level 50");  # 8
        Awards.register("awards/rank7.png","Attain Rank 7\nGet to level 60");  # 9
        Awards.register("awards/rank8.png","Attain Rank 8\nGet to level 70");  # 10
        Awards.register("awards/rank9.png","Attain Rank 9\nGet to level 80");  # 11
        Awards.register("awards/forharambe.png","For Harambe\n???");  # 12
        Awards.register("awards/youwin.png","Win A Wager\nDon't not win a wager");  # 13
        Awards.register("awards/beat.png","Lose A Wager\nDon't win a wager");  # 14
        Awards.register("awards/daddy.png","Dumbledore\n???"); # 15
        Awards.register("awards/benfont.png","One True Type Font\n???"); # 16
        Awards.register("awards/givecash.png","Sugar Daddy\nGive another player over or $50"); # 17
        Awards.register("awards/potato.png","Bringer Of Potatoes\nGive a potato"); # 18
        Awards.register("awards/kingtat.png","Potato King\nGive out 100 potatoes"); # 19
        Awards.register("awards/kingtat.png","Potato King\nGive out 100 potatoes"); # 20
        Awards.register("awards/admin.png","DueUtil Admin\nOnly DueUtil admins can have this."); # 21
        Awards.register("awards/mod.png","DueUtil Mod\nOnly DueUtil mods can have this."); # 22
        Awards.register("awards/bg_accepted.png","Background Accepted!\nGet a background submission accepted");#23
        Awards.register("awards/top_dog.png","TOP DOG\nWhile you have this award you're undefeated"); #24
        Awards.register("awards/donor_award.png","All MacDue Ever Wanted!\nDonate to DueUtil"); #25
        
class Players:
  
    @staticmethod
    def find_player(user_id):
        if(user_id in players):
            return players[user_id]
        else:
            return None;

    @staticmethod
    def load():
        global players;
        reference = Player();
        for player in dbconn.get_collection_for_object(Player).find():
            loaded_player = jsonpickle.decode(player['data']); 
            players[loaded_player.user_id] = util.load_and_update(reference,loaded_player);

class Quests:
  
    @staticmethod
    def get_game_quest_from_id(id):
        id  = str(id);
        args = util.get_strings(id);
        if(len(args) == 2 and args[0] in ServersQuests and args[1] in ServersQuests[args[0]]):
            return ServersQuests[args[0]][args[1]];
        else:
            return None;
            
            
    @staticmethod
    def load():
        global servers_quests;
        reference = Quest('Reference',0,0,0,0)
        for quest in dbconn.get_collection_for_object(Quest).find():
            loaded_quest = jsonpickle.decode(quest['data']); 
            location = quest.q_id.split('/',1);
            servers_quests[location[0]][location[1]] = util.load_and_update(reference,loaded_quest);
                    

class Weapons:
    NO_WEAPON_ID = "000000000000000000_none";
    STOCK_WEAPONS = ["stick","laser gun","gun","none","frisbee"];
    
    @staticmethod
    def get_weapon_from_id(id):
        if id in weapons:
            return weapons[id]
        else:
            if id != no_weapon_id:
                return weapons[no_weapon_id];
                
    @staticmethod
    def does_weapon_exist(server_id,weapon_name):   
        if Weapons.get_weapon_for_server(server_id,weapon_name) != None:
            return True;
        return False;
    
    @staticmethod
    def get_weapon_for_server(server_id,weapon_name):
        if weapon_name.lower() in Weapons.STOCK_WEAPONS:
            return weapons["000000000000000000_"+weapon_name.lower()];
        else:
            weapon_id = server_id+"_"+weapon_name.lower();
            if weapon_id in weapons:
                return weapons[weapon_id]
            else:
                return None;
                
    @staticmethod
    def remove_weapon_from_shop(player,wname):
        for weapon in player.owned_weps:
            stored_weapon = Weapons.get_weapon_from_id(weapon[0]);
            if stored_weapon != None and stored_weapon.name.lower() == wname.lower():
                wID = weapon[0];
                sum = weapon[1];
                del player.owned_weps[player.owned_weps.index(weapon)];
                return [wID,sum];
        return None;
        
    @staticmethod
    def get_weapons_for_server(id):
        return {weapon_id: weapons[weapon_id] for weapon_id in weapons
                           if (weapons[weapon_id].name.lower() in Weapons.STOCK_WEAPONS
                           and weapon_id != Weapons.NO_WEAPON_ID) or weapon_id.startswith(id)}
        
    @staticmethod
    def load():
        global weapons;
        none = Weapon('None',None,1,66);
        weapons[none.w_id] = none;
        
        for weapon in dbconn.get_collection_for_object(Weapon).find():
            loaded_weapon= jsonpickle.decode(weapon['data']);
            weapons[loaded_weapon.w_id] = util.load_and_update(none,loaded_weapon)
                
class Misc:
    POSTIVE_BOOLS = ('true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh');
    
    @staticmethod
    def load():
        global banners;
        banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png");

class Stats:
    money_created = 0;
    money_transferred = 0;
    players_leveled = 0;
    new_players_joined = 0;
    quests_given = 0;
    quests_attempted = 0;  
    images_served = 0;
    
    @staticmethod
    def get_stats():
        return {key: value for key,
                value in Stats.__dict__.items() if not callable(key)}

Misc.load();
Awards.load();
Weapons.load();
Quests.load();
Players.load();
