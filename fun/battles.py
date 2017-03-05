from fun import game,players;
from botstuff import util
import random 
from collections import OrderedDict
                
async def equip_weapon(message,player,wname):
    storedWeap = remove_weapon_from_store(player,wname);
    if(storedWeap != None):
        if owns_weapon_name(player,get_weapon_from_id(player.wID).name):
            player.owned_weps.append(storedWeap);
            await get_client(message.server.id).send_message(message.channel, ":bangbang: **Cannot put your current equiped weapon in your weapon storage as a weapon with the same name is already being stored!**"); 
            return;
        if(player.wID != no_weapon_id):
            player.owned_weps.append([player.wID,player.wep_sum]);
        player.wID = storedWeap[0];
        player.wep_sum = storedWeap[1];
        newWeap = get_weapon_from_id(player.wID);
        if(newWeap.wID != no_weapon_id):
            await harambe_check(message,newWeap,player);
            await get_client(message.server.id).send_message(message.channel, ":white_check_mark: **"+newWeap.name+"** equiped!");
        else:
            await get_client(message.server.id).send_message(message.channel, ":white_check_mark: equiped!");
        savePlayer(player);
    else:
        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You do not have that weapon stored!**");


async def buy_weapon(message,command_key):
    messageArg = message.content.lower().replace(command_key + "buy ", "", 1);
    Found = False;
    try:
        weapon = get_weapon_for_server(message.server.id, messageArg.strip());
        if(weapon != None and weapon.name != "None"):
            if ((weapon.server == "all") or (weapon.server == message.server.id)) and weapon.price != -1:
                Found = True;
                player = findPlayer(message.author.id);
                if(player == None):
                    return True;
                if((player.money - weapon.price) >= 0):
                    if(weapon.price <= max_value_for_player(player)):
                        if(len(player.owned_weps) < 6 or player.wID == no_weapon_id):
                            if(player.wID == no_weapon_id):
                                player.wID = weapon.wID;
                                await harambe_check(message,weapon,player);
                                await give_award(message, player, 4, "License to kill.");
                                player.wep_sum = get_weapon_sum(weapon.wID)
                                await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** bought a " + weapon.name + " for $" +  util.to_money(weapon.price,False) + "!");
                            else:
                                if not owns_weapon_name(player,weapon.name.lower()):
                                    player.owned_weps.append([weapon.wID,get_weapon_sum(weapon.wID)]);
                                    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** bought a " + weapon.name + " for $" +  util.to_money(weapon.price,False) + "!");
                                    await get_client(message.server.id).send_message(message.channel, ":warning: You have not yet equiped this weapon yet.\nIf you want to equip this weapon do **"+command_key+"equipweapon "+weapon.name.lower()+"**.");
                                else:
                                    await get_client(message.server.id).send_message(message.channel, ":bangbang: **You already have a weapon with that name stored!**"); 
                            player.money = player.money - weapon.price;
                            savePlayer(player);             
                        else:
                            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** you have no free weapon slots! Sell one of your weapons first!");
                    else:
                        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You're currently too weak to wield that weapon!**\nFind a weapon that better suits your limits with **"+command_key+"mylimit**");
                        
                else:
                    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** you can't afford this weapon.\nYou need **$"+util.to_money(weapon.price-player.money,False)+"** more.");
    except:
        Found = False;
    if(not Found):
        await get_client(message.server.id).send_message(message.channel, "Weapon not found!"); 

async def show_weapons(message,player,not_theirs):
    eweap = get_weapon_from_id(player.wID);
    output = "```"+player.name+"'s stored weapons\nEquipped: "+eweap.icon+" - "+eweap.name+"\n";
    #check wep not removed/replaced
    num = 1;
    for ws in player.owned_weps:
        weap = get_weapon_from_id(ws[0]);
        if(weap != None):
            if(weap.melee == True):
                Type = "Melee";
            else:
                Type = "Ranged";
            accy = round(weap.chance,2);
            output = output+str(num)+". "+weap.icon + " - " + weap.name + " | DMG: " + util.number_format_text(weap.attack) + " | ACCY: " + (str(accy)+"-").replace(".0-","").replace("-","") + "% | Type: " + Type + " |\n";
            num=num+1;
    if(len(player.owned_weps) == 0):
        if(not not_theirs):
            output = output + "You don't have any weapons stored!```";
        else:
            output = output + player.name+" does not have any weapons stored!```";
    else:
        if(not not_theirs):
            cmd = util.get_server_cmd_key(message.server);
            output = output+"Use "+cmd+"equipweapon [Weapon Name] to equip a stored weapon!\nUse "+cmd+"unequipweapon to store your equiped weapon.```";
        else:
            output = output + "```";
    await get_client(message.server.id).send_message(message.channel, output);
    
def get_server_weapon_list(message):
    global Weapons;
    weapon_listings = "";
    count = 0;
    for key in Weapons.keys():
        if key.startswith(message.server.id) or key.startswith("000000000000000000"):
            weapon = Weapons[key];
            if(weapon.price != -1 and weapon.wID != no_weapon_id):
                count = count + 1;
                Type = "";
                if(weapon.melee == True):
                    Type = "Melee";
                else:
                    Type = "Ranged";
                accy = round(weapon.chance,2);
                weapon_listings = weapon_listings + str((count)) + ". " + weapon.icon + " - " + weapon.name + " | DMG: " + util.number_format_text(weapon.attack) + " | ACCY: " + util.format_float_drop_zeros(accy) + "% | Type: " + Type + " | $" +  util.to_money(weapon.price,False)+ " |\n";	
    return weapon_listings;                     

async def shop(message):
    normal_title = "Welcome to DueUtil's weapon shop!";
    #past_page_one_title = "DueUtil's weapon shop";
    #constant_footer = "Type **" + util.get_server_cmd_key(message.server) + "buy [Weapon Name]** to purchase a weapon.";
    #final_page_footer = "Want more? Ask a server manager to add stock!";
    #await util.display_with_pages(message,get_server_weapon_list(message),"shop",normal_title,past_page_one_title,constant_footer,final_page_footer);
        
async def validate_weapon_store(message,player):
    weapon_sums = [];
    for ws in player.owned_weps:
        if(ws[1] != get_weapon_sum(ws[0])):
            weapon_sums.append(ws[1]);
            del player.owned_weps[player.owned_weps.index(ws)];
    if len(weapon_sums) > 0:
        await mass_recall(message,player,weapon_sums);        

async def sell(message, uID, recall):
    await sell_weapon(message,uID,recall,None); 

async def mass_recall(message, player, weapon_sums):
    refund = 0;
    for sum in weapon_sums:
        refund = refund + int(util.get_strings(sum)[0]);
    player.money = player.money + refund;
    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** a weapon or weapons you have stored have been recalled by the manufacturer. You get a full $" + util.to_money(refund,False) + " refund.");
    savePlayer(player);
    
async def sell_weapon(message, uID, recall,weapon_name):
    global Players;
    global Weapons;
    player = findPlayer(uID);
    if (player == None):
        return True;
    weapon_id= no_weapon_id;
    if(weapon_name == None):
        weapon_id = player.wID;
    else:
        weapon_data = remove_weapon_from_store(player,weapon_name);
        if(weapon_data == None):
            if(get_weapon_from_id(player.wID).name.lower() == weapon_name):
                weapon_name = None;
                weapon_id = player.wID;
            if(weapon_name != None):
                await get_client(message.server.id).send_message(message.channel, ":bangbang: **Weapon not found!**");
                return;
        if(weapon_data != None):
            weapon_id = weapon_data[0];
    if (weapon_id != no_weapon_id):
        weapon = get_weapon_from_id(weapon_id);
        price = int(((weapon.chance/100) * weapon.attack) / 0.04375);
        sellPrice = int(price - (price / 4));
        if(not recall):
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** sold their trusty " +weapon.name + " for $" +util.to_money(sellPrice,False)+ "!");
        else:
            if(weapon_name == None):
                sellPrice = int(util.get_strings(player.wep_sum)[0]);
            else:
                sellPrice = int(util.get_strings(weapon_data[1])[0]);
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** your weapon has been recalled by the manufacturer. You get a full $" + util.to_money(sellPrice,False) + " refund.");
        if(weapon_name == None):
            player.wID = no_weapon_id;
            player.wep_sum = get_weapon_sum(no_weapon_id)
        player.money = player.money + sellPrice;
        savePlayer(player);
    else:
        await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** nothing does not fetch a good price...");

# quest, wager normal
def battle(ctx,**kwargs):
  
    current_move = 1
    damage_modifier = 1.5
    
    player_one = kwargs.get('player_one',None)
    player_two = kwargs.get('player_two',None)
    
    player_one_hp = player_one.hp * (util.clamp(5 - player_one.level,1,5));
    player_two_hp = player_two.hp * (util.clamp(5 - player_two.level,1,5));

    moves = OrderedDict()
    
    def add_move(player,other_player,player_no):
        nonlocal moves, current_move, damage_modifier
        
        BABY_MOVES = ["slapped","scratched","hit","punched","licked","bit","kicked","tickled"]
        weapon = player.weapon;      
        message = ""
                                  
        if weapon.w_id == game.Weapons.NO_WEAPON_ID:
            message = random.choice(BABY_MOVES) 
        else:
            message = weapon.hit_message
                  
        moves[str(player_no)+'/'+str(current_move)] = ['**'+player.clean_name +'** '+ message +' **'+other_player.clean_name+'**',1]
        current_move += 1
        damage_modifier += 0.5

    def shrink_repeats(moves):  
        last_move = None
        moves_shrink_repeat = OrderedDict()
        for move, move_info in moves.items():
            if last_move != None:
                if last_move[0] == move[0]:
                    moves_shrink_repeat[last_move] = [move_info[0],move_info[1] + moves_shrink_repeat[last_move][1]] 
                    move = last_move
                else:
                    moves_shrink_repeat[move] = move_info 
            else:
                moves_shrink_repeat[move] = move_info
            last_move = move;
        return moves_shrink_repeat
    
    def shrink_duos(moves):
        moves_shrink_duos = OrderedDict()
        last_move = None
        count = 0
        for move, move_info in moves.items():
            count += 1
            if last_move != None and count % 2 == 0:
                moves_shrink_duos[last_move] = [moves[last_move][0],moves[last_move][1] - 1]
                moves_shrink_duos["Duo"+str(count)] = [moves[last_move][0] +" ⇆ " +move_info[0] ,1]
                moves_shrink_duos[move] = [move_info[0],move_info[1] - 1]
            last_move = move;
        if len(moves) % 2 == 1:
            odd_move = moves.popitem()
            moves_shrink_duos[odd_move[0]] = odd_move[1]
        for move, move_info in moves_shrink_duos.copy().items():
            if move_info[1] <= 0:
                del moves_shrink_duos[move]
        return moves_shrink_duos
                
    def compress_moves():
        nonlocal moves
        moves = shrink_repeats(shrink_duos(shrink_repeats(moves)))
    
    def hit(successful_hit_from):
              
        nonlocal player_one,player_two,player_one_hp,player_two_hp, damage_modifier
        
        if successful_hit_from == None:
            successful_hit_from = 1 if bool(random.getrandbits(1)) else 2
        else:
            if successful_hit_from == 1:
                player_two_hp -= (player_one.weapon.damage * player_one.attack)/player_two.strg * damage_modifier
                add_move(player_one,player_two,successful_hit_from)
            else:
                player_one_hp -= (player_two.weapon.damage * player_two.attack)/player_one.strg * damage_modifier
                add_move(player_two,player_one,successful_hit_from)
                  
    while player_one_hp > 0 and player_two_hp > 0:
        player_one_hit = player_one.weapon_hit()
        player_two_hit = player_two.weapon_hit()
        
        if player_one_hit:
            hit(1)
        if player_two_hit:
            hit(2)
        if not (player_one_hit or player_two_hit):
            hit(None)
    compress_moves()
    winner = None
    loser = None
    if player_one_hp > player_two_hp:
        winner = player_one
        loser = player_two
    elif player_one_hp < player_two_hp:
        winner = player_two
        loser = player_one
    moves["winner"] = [":trophy: **"+winner.clean_name+"** wins in **" +str(current_move-1) + "** turns!",1]
    return [moves,current_move-1]
    
    
def load_weapons():
    global Weaponse;
    for file in os.listdir("saves/weapons/"):
        if file.endswith(".json"):
            with open("saves/weapons/" + str(file)) as data_file:    
                try:
                    data = json.load(data_file);
                    w = jsonpickle.decode(data);
                    Weapons[w.wID] = w;
                except:
                    print("Weapon data corrupt!");

def add_weapon(weapon):
    global weapons;
    weapons[weapon.w_id] = weapon;
    save_weapon(weapon);
