weapons = dict();         #Weapons
NO_WEAPON_ID = "000000000000000000_none";
STOCK_WEAPONS = ["stick","laser gun","gun","none","frisbee"];

quests_given=0;
quests_attempted=0;
servers_quests = dict();  #ServerQuests

#DueUtil stats
money_created = 0;
money_transferred =0;
players_leveled=0;
new_players_joined=0;

players = dict();         #Players
awards = [];
banners = dict();         #Banners
backgrounds = dict();     #Backgrounds

class Weapon:
  
    """A simple weapon that can be used by a monster or player in DueUtil"""
    
    def __init__(self,message,name,accy,damage,**kwargs):
      
        if does_weapon_exist(server,name):
            raise util.DueUtilException(message.channel,"A weapon with that name already exists on this server!");
            
        if len(name) > 30 or len(name) == 0 or name.strip == "":
            raise util.DueUtilException(message.channel,"Weapon names must be between 1 and 30 characters!");
            
        if accy == 0 or damage == 0:
            raise util.DueUtilException(message.channel,"No weapon stats can be zero!");
        
        if accy > 86 or accy < 1:
            raise util.DueUtilException(message.channel,"Accuracy must be between 1% and 86%!");
        
        self.server_id = message.server_id;
        self.icon = kwargs.get('icon',"!")
        self.hit_text = kwargs.get('hit_text',"hits");
        self.melee = kwargs.get('melee',True);
        self.image_url = kwargs.get('image_url',"");
  
        self.name = name;
        self.damage = damage;
        self.accy = accy;
        self.price = self.__price();
        self.w_id = self.__weapon_id();
        self.weapon_sum = self.__weapon_sum();
        
        add_weapon(self);
            
    def __weapon_id(self):
        return self.server_id+"_"+self.name.lower();
        
    def __weapon_sum(self):
        return '"'+str(self.price)+'"'+str(self.damage)+str(weapon.accy);
      
    def __price(self):
        return (self.accy/100 * self.damage) / 0.04375; 
        
    def does_hit(self,holder):
        return random.random()<(holder.weapon_accy/100);
      
    @staticmethod
    def get_weapon_from_id(id):
        if(id in Weapons):
            return Weapons[id]
        else:
            if(id != no_weapon_id):
                return Weapons[no_weapon_id];
    @staticmethod
    def does_weapon_exist(server_id,weapon_name):   
        if(get_weapon_for_server(server_id,weapon_name) != None):
            return True;
        return False;
    
    @staticmethod
    def get_weapon_for_server(server_id,weapon_name):
        if(weapon_name.lower() in stock_weapons):
            return Weapons["000000000000000000_"+weapon_name.lower()];
        else:
            weapon_id = server_id+"_"+weapon_name.lower();
            if(weapon_id in Weapons):
                return Weapons[weapID]
            else:
                return None;
                
    @staticmethod
    def remove_weapon_from_shop(player,wname):
        for weapon in player.owned_weps:
            stored_weapon = get_weapon_from_id(weapon[0]);
            if(stored_weapon != None and stored_weapon.name.lower() == wname.lower()):
                wID = weapon[0];
                sum = weapon[1];
                del player.owned_weps[player.owned_weps.index(weapon)];
                return [wID,sum];
        return None;
        
    @staticmethod
    def save_weapon(weapon):
        data = jsonpickle.encode(weapon);
        with open("saves/weapons/" + str(hashlib.md5(weapon.wID.encode('utf-8')).hexdigest()) + ".json", 'w') as outfile:
            json.dump(data, outfile);   
            
class BattleRequest:
  
    """A class to hold a wager"""
  
    def __init__(self,message,wager_amount):
        self.sender_id = message.author.id;
        self.wager_amount = wagers_amount;

class Quest:
  
    """A class to hold info about a server quest"""
  
    def __init__(self,message,name,base_attack,base_strg,base_accy,base_hp,**kwargs):
      
        if message.server.id in server_quests:
            if name.strip().lower() in server_quests[message.server.id]:
                raise util.DueUtilException(message.channel,"A foe with that name already exists on this server!");
      
        if base_accy < 1 or base_attack < 1 or base_strg < 1:
            raise util.DueUtilException(message.channel,"No quest stats can be less than 1!");

        if base_hp < 30:
            raise util.DueUtilException(message.channel,"Base HP must be at least 30!");

        if len(name) > 30 or len(name) == 0 or name.strip == "":
            raise util.DueUtilException(message.channel,"Quest names must be between 1 and 30 characters!");
      
        self.task = kwargs.get('task',"Battle a");
        self.w_id = kwargs.get('weapon_id',no_weapon_id);
        self.spawn_chance = kwargs.get('spawn_chance',4);
        self.image_url = kwargs.get('image_url',"");
        
        self.monster_name = name;
        self.base_attack = base_attack;
        self.server_id = message.server_id;
        self.base_strg = base_strg;
        self.base_accy = base_accy;
        self.base_hp = base_hp;
        
        created_by = message.author.id;
        
        base_reward = self__reward();
        self.q_id = self.__quest_id();
        
        add_quest(self);
        
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
                        
    @property
    def made_on():
        return self.server_id;
        
    @staticmethod
    def get_game_quest_from_id(id):
        id  = str(id);
        args = util.get_strings(id);
        if(len(args) == 2 and args[0] in ServersQuests and args[1] in ServersQuests[args[0]]):
            return ServersQuests[args[0]][args[1]];
        else:
            return None;
            
    def save(self):
        data = jsonpickle.encode(quest);
        quest_id = self.q_id.split('/',1);
        file_name = str(hashlib.md5(quest.monsterName.lower().encode('utf-8')).hexdigest())+".json";
        with open("saves/gamequests/" + quest_id[0] + "_"+file_name+".json", 'w') as outfile:
            json.dump(data, outfile);
            
class ActiveQuest(Player):
  
    def __init__(self,q_id):
        self.q_id = q_id;
        super(ActiveQuest,self).__init__();
        
    def get_avatar_url(self,*args):
        return self.info.image_url;
  
    @property
    def info(self):
        quest_id = self.q_id.split('/',1);
        return ServersQuests[quest_id[0]][quest_id[1]];            

class Award:

    def __init__(self,icon_path,name,description):
        self.name = name;
        self.description = description;
        self.icon = Image.open(icon_path);
        
    def register(icon_path,text):
        global awards;
        info = text.split('\n');
        awards.append(Award(icon_path,info[0],info[1]));
        
    @staticmethod
    def get_award(award_id):
        return awards[award_id]; 

    @staticmethod          
    def load():
        load_award("awards/Duseless.png","Duseless\nIgnore DueUtil");  # 0
        load_award("awards/questDone.png","Save The Server\nComplete a quest");  # 1
        load_award("awards/rank2.png","Attain Rank 2\nGet to level 10");  # 2
        load_award("awards/redmist.png","Red Mist\nFail a quest");  # 3
        load_award("awards/spender.png","Licence To Kill\nBuy a weapon");  # 4
        load_award("awards/rank3.png","Attain Rank 3\nGet to level 20");  # 5
        load_award("awards/rank4.png","Attain Rank 4\nGet to level 30");  # 6
        load_award("awards/rank5.png","Attain Rank 5\nGet to level 40");  # 7
        load_award("awards/rank6.png","Attain Rank 6\nGet to level 50");  # 8
        load_award("awards/rank7.png","Attain Rank 7\nGet to level 60");  # 9
        load_award("awards/rank8.png","Attain Rank 8\nGet to level 70");  # 10
        load_award("awards/rank9.png","Attain Rank 9\nGet to level 80");  # 11
        load_award("awards/forharambe.png","For Harambe\n???");  # 12
        load_award("awards/youwin.png","Win A Wager\nDon't not win a wager");  # 13
        load_award("awards/beat.png","Lose A Wager\nDon't win a wager");  # 14
        load_award("awards/daddy.png","Dumbledore\n???"); # 15
        load_award("awards/benfont.png","One True Type Font\n???"); # 16
        load_award("awards/givecash.png","Sugar Daddy\nGive another player over or $50"); # 17
        load_award("awards/potato.png","Bringer Of Potatoes\nGive a potato"); # 18
        load_award("awards/kingtat.png","Potato King\nGive out 100 potatoes"); # 19
        load_award("awards/kingtat.png","Potato King\nGive out 100 potatoes"); # 20
        load_award("awards/admin.png","DueUtil Admin\nOnly DueUtil admins can have this."); # 21
        load_award("awards/mod.png","DueUtil Mod\nOnly DueUtil mods can have this."); # 22
        load_award("awards/bg_accepted.png","Background Accepted!\nGet a background submission accepted");#23
        load_award("awards/top_dog.png","TOP DOG\nWhile you have this award you're undefeated"); #24
        load_award("awards/donor_award.png","All MacDue Ever Wanted!\nDonate to DueUtil"); #25


class PlayerInfoBanner:
    
    """Class to hold details & methods for a profile banner"""
    
    def __init__(self,name,image_name,**kwargs):
      
        self.price = kwargs.get('price',0);
        self.donor = kwargs.get('donor',False);
        self.admin_only = kwargs.get('admin_only',False);
        self.mod_only = kwargs.get('mod_only',False);
        self.unlock_level = kwargs.get('unlock_level',0);
        
        self.image_name = image_name;
        self.name = name;
        self.load_image();
        
    def banner_restricted(self,player):
        return ((not banner.admin_only or banner.admin_only == util.is_admin(player.userid)) 
                and (not banner.mod_only or banner.mod_only == util.is_mod_or_admin(player.userid)));
        
        
    def can_use_banner(self,player):
        return (not banner.donor or banner.donor == player.donor) and self.banner_restricted(player);
        
    def load_image(self):
        self.image = imagehelper.set_opacity(Image.open('screens/info_banners/'+image_name),0.9);
        
    def save(self):
        data = jsonpickle.encode(self);
        with open("screens/info_banners/" + self.name.lower().replace(" ","_")+ ".json", 'w') as outfile:
            json.dump(data, outfile);
        
    @staticmethod
    def load():
        global banners;
        banners["discord blue"] = PlayerInfoBanner("Discord Blue","info_banner.png");
      
class Player:
  
    """The DueUtil player!"""
  
    def __init__(self,*args):
        global players;
        self.user_id = args[0].id if len(args) > 0 and isinstance(args[0],discord.Member) else "";
        self.reset();
        players[self.user_id] = self;

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
        self.name = "Put name here";
        self.w_id = NO_WEAPON_ID;
        self.money = 0;
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
        self.owned_weps = [];
        self.save();
        
    def owns_weapon(self,weapon_name):
        for weapon_slot in self.owned_weps:
            if(Weapon.get_weapon_from_id(weapon_slot[0]).name.lower() == weapon_name.lower()):
                return True;
        return False;
        
    @property    
    def weapon_accy(self):
        max_value = self.max_value_for_player();
        price = self.weapon.price if self.weapon.price > 0 else 1;
        new_accy = numpy.clip(max_value/price * 100,1,86);
        new_accy = weapon.chance if new_accy > weapon.chance else new_accy;
        return new_accy if price > max_value else self.weapon.chance;
    
    def max_value_for_player(self):
        if not util.is_admin(self.user_id):
            return 10 * (math.pow(self.level,2)/3 + 0.5 * math.pow(self.level+1,2) * self.level);
        else:
            return math.inf;  #Best new feature!
            
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
        data = jsonpickle.encode(self);
        with open("saves/players/" + self.user_id + ".json", 'w') as outfile:
            json.dump(data, outfile);
            
    @property
    def weapon(self):
        return weapons[self.w_id];
        
    @property
    def banner(self):
        banner = banners.get(self.banner_id,banners["discord blue"]);
        if not banner.can_use_banner(player):
            player.banner_id = "discord blue";
            return banners["discord blue"];
        return banner;
        
    def get_avatar_url(self,*args):
        server = args[0];
        member = server.get_member(self.user_id);
        if member.avatar_url != "":
           return member.avatar_url;
        else:
           return member.default_avatar_url;
        
    @staticmethod
    def find_player(user_id):
        global players;
        
        if(user_id in players):
            return players[user_id]
        else:
            return None;
