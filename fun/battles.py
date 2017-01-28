import fun.players;
                
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
            #print(util.get_strings(player.wep_sum));
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** your weapon has been recalled by the manufacturer. You get a full $" + util.to_money(sellPrice,False) + " refund.");
        if(weapon_name == None):
            player.wID = no_weapon_id;
            player.wep_sum = get_weapon_sum(no_weapon_id)
        player.money = player.money + sellPrice;
        savePlayer(player);
    else:
        await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** nothing does not fetch a good price...");


async def battle(message, battlers, wager, quest):  # Quest like wager with diff win text
    global players, weapons,money_created,money_transferred,quests_attempted;
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10 and (wager == None and quest == False) ):
        await get_client(message.server.id).send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    if(wager == None and quest == False):
        player_one = findPlayer(players[0]);
        player_two = findPlayer(players[1]);
    elif (quest == True):
        player_one = findPlayer(players[0]);
        player_two = players[1];
        quests_attempted = quests_attempted + 1;
    else:
        player_one = findPlayer(message.author.id);
        player_two = findPlayer(wager.senderID);
        money_transferred = money_transferred + wager.wager;
    turns = 0;
    hp_player_one = 0;
    hp_player_two = 0;
    battle_lines = 0;
    if (player_one != None) and (player_two != None):
        hp_player_one = player_one.hp;
        hp_player_two = player_two.hp;
        weapon_player_one= get_weapon_from_id(player_one.wID);
        weapon_player_two = get_weapon_from_id(player_two.wID);
        bText = "```(" + player_one.name + " Vs " + player_two.name + ")\n";
        while (hp_player_one > 0) and (hp_player_two > 0):
            player_two_turn = battle_turn(player_two,player_one,weapon_player_two);
            hp_player_one += -player_two_turn[1];
            if player_two_turn[0] != None:
                bText += player_two_turn[0];
                battle_lines+=1;
            player_one_turn = battle_turn(player_one,player_two,weapon_player_one);
            hp_player_two += -player_one_turn[1];
            if player_one_turn[0] != None:
                bText += player_one_turn[0];
                battle_lines+=1;
            turns = turns + 1;
        txt = "turns";
        if(turns == 1):
            txt = "turn"
        if(battle_lines > 25):
            bText = "```(" + player_one.name + " Vs " + player_two.name + ")\nThe battle was too long to display!\n";
        if(hp_player_one > hp_player_two):
            if(wager == None):
                await battle_image(message, player_one, player_two, bText + player_one.name + " Wins in " + str(turns) + " " + txt + "!\n```\n");
            else:
                bText = bText +player_one.name + " Wins in " + str(turns) + " " + txt + "!\n";
                if not quest:
                    bText = bText + player_one.name + " receives $" + util.to_money(wager.wager,False)+ " in winnings from " + player_two.name + "!\n```\n";
                    player_one.money = player_one.money + (wager.wager * 2);
                    player_one.wagers_won = player_one.wagers_won + 1;
                    await give_award(message, player_one, 13, "Win a wager!");
                    await give_award(message, player_two, 14, "Lose a wager!");
                    savePlayer(player_one);
                    savePlayer(player_two);
                else:
                    player_one.money = player_one.money + wager;
                    money_created = money_created + wager;
                    bText = bText +player_one.name + " completed a quest and earned $" +  util.to_money(wager,False)+ "!\n```\n";
                    player_one.quests_won = player_one.quests_won + 1;
                    if(player_one.quests_completed_today == 0):
                        player_one.quest_day_start = time.time();
                    player_one.quests_completed_today  = player_one.quests_completed_today + 1;
                    await give_award(message, player_one, 1, "*Saved* the server.");
                    print(filter_func(player_one.name)+" ("+player_one.userid+") has received $"+util.to_money(wager,False)+" from a quest.");
                    savePlayer(player_one);
                await battle_image(message, player_one, player_two, bText);
        elif (hp_player_two > hp_player_one):
            if(wager == None):
                await battle_image(message, player_one, player_two, bText +player_two.name + " Wins in " + str(turns) + " " + txt + "!\n```\n");
            else:
                if not quest:
                    bText = bText +player_two.name + " Wins in " + str(turns) + " " + txt + "!\n";
                    bText = bText + player_two.name + " receives $" + util.to_money(wager.wager,False) + " in winnings from " + player_one.name + "!\n```\n";
                    player_two.money = player_two.money + (wager.wager * 2);
                    player_two.wagers_won = player_two.wagers_won + 1;
                    await give_award(message, player_two, 13, "Win a wager!");
                    await give_award(message, player_one, 14, "Lose a wager!");
                    savePlayer(player_one);
                    savePlayer(player_two);
                else:
                    bText = bText + "The " + player_two.name + " Wins in " + str(turns) + " " + txt + "!\n";
                    bText = bText + ""+player_one.name + " failed a quest and lost $" + util.to_money(int((wager) / 2),False)+ "!\n```\n";
                    player_one.money = player_one.money - int((wager) / 2);
                    await give_award(message, player_one, 3, "Red mist.");
                    savePlayer(player_one);
                await battle_image(message, player_one, player_two, bText);
        else:
            if(wager == None):
                await battle_image(message, player_one, player_two, bText + "Draw in " + str(turns) + " " + txt + "!\n```\n");
            else:
                if not quest:
                    player_two.money = player_two.money + wager.wager;
                    player_one.money = player_one.money + wager.wager;
                    await battle_image(message, player_one, player_two, bText + "Draw in " + str(turns) + " " + txt + " wagered money has been returned.\n```\n");
                    savePlayer(player_one);
                    savePlayer(player_two);
                else:
                    await battle_image(message, player_one, player_two, bText + "Quest ended in draw no money has been lost or won.\n```\n");
                    savePlayer(player_one);
                    savePlayer(player_two);

    else:
        if(player_one == None):
            await get_client(message.server.id).send_message(message.channel, "**"+util.get_server_name(message,players[0])+"** has not joined!");
        if(player_two == None):
            await get_client(message.server.id).send_message(message.channel, "**"+util.get_server_name(message,players[1])+"** has not joined!");


def battle_turn(player,other_player,weapon):
    battle_line = None;
    player_hit_damage = player.attack;
    other_name = "the "+other_player.name if isinstance(other_player,activeQuest) else other_player.name;
    player_name = "The "+player.name if isinstance(player,activeQuest) else player.name;
    if(player.wID != no_weapon_id):
        if(weapon_hit(player,weapon)):
            if(not weapon.melee):
                player_hit_damage = weapon.attack * player.shooting;
            else:
                player_hit_damage = weapon.attack * player.attack;
            battle_line = player_name + " " + weapon.useText + " " + other_name + "!\n";
    damage_dealt = (player_hit_damage / (other_player.strg / 3 +1));
    if damage_dealt < 0.01:
        damage_dealt = 0.01;
    return [battle_line,damage_dealt];

    
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
