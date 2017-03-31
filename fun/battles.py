from fun import players, weapons
from botstuff import util
import random 
from collections import OrderedDict

            
class BattleRequest:
  
    """A class to hold a wager"""
  
    def __init__(self,message,wager_amount):
        self.sender_id = message.author.id
        self.wager_amount = wagers_amount

                
async def equip_weapon(message,player,wname):
    storedWeap = remove_weapon_from_store(player,wname)
    if(storedWeap != None):
        if owns_weapon_name(player,get_weapon_from_id(player.wID).name):
            player.owned_weps.append(storedWeap)
            await get_client(message.server.id).send_message(message.channel, ":bangbang: **Cannot put your current equiped weapon in your weapon storage as a weapon with the same name is already being stored!**"); 
            return
        if(player.wID != no_weapon_id):
            player.owned_weps.append([player.wID,player.wep_sum])
        player.wID = storedWeap[0]
        player.wep_sum = storedWeap[1]
        newWeap = get_weapon_from_id(player.wID)
        if(newWeap.wID != no_weapon_id):
            await harambe_check(message,newWeap,player)
            await get_client(message.server.id).send_message(message.channel, ":white_check_mark: **"+newWeap.name+"** equiped!")
        else:
            await get_client(message.server.id).send_message(message.channel, ":white_check_mark: equiped!")
        savePlayer(player)
    else:
        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You do not have that weapon stored!**")

async def show_weapons(message,player,not_theirs):
    eweap = get_weapon_from_id(player.wID)
    output = "```"+player.name+"'s stored weapons\nEquipped: "+eweap.icon+" - "+eweap.name+"\n"
    #check wep not removed/replaced
    num = 1
    for ws in player.owned_weps:
        weap = get_weapon_from_id(ws[0])
        if(weap != None):
            if(weap.melee == True):
                Type = "Melee"
            else:
                Type = "Ranged"
            accy = round(weap.chance,2)
            output = output+str(num)+". "+weap.icon + " - " + weap.name + " | DMG: " + util.number_format_text(weap.attack) + " | ACCY: " + (str(accy)+"-").replace(".0-","").replace("-","") + "% | Type: " + Type + " |\n"
            num=num+1
    if(len(player.owned_weps) == 0):
        if(not not_theirs):
            output = output + "You don't have any weapons stored!```"
        else:
            output = output + player.name+" does not have any weapons stored!```"
    else:
        if(not not_theirs):
            cmd = util.get_server_cmd_key(message.server)
            output = output+"Use "+cmd+"equipweapon [Weapon Name] to equip a stored weapon!\nUse "+cmd+"unequipweapon to store your equiped weapon.```"
        else:
            output = output + "```"
    await get_client(message.server.id).send_message(message.channel, output)
    
async def validate_weapon_store(message,player):
    weapon_sums = []
    for ws in player.owned_weps:
        if(ws[1] != get_weapon_sum(ws[0])):
            weapon_sums.append(ws[1])
            del player.owned_weps[player.owned_weps.index(ws)]
    if len(weapon_sums) > 0:
        await mass_recall(message,player,weapon_sums);        

async def sell(message, uID, recall):
    await sell_weapon(message,uID,recall,None); 

async def mass_recall(message, player, weapon_sums):
    refund = 0
    for sum in weapon_sums:
        refund = refund + int(util.get_strings(sum)[0])
    player.money = player.money + refund
    await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** a weapon or weapons you have stored have been recalled by the manufacturer. You get a full $" + util.to_money(refund,False) + " refund.")
    savePlayer(player)
    
async def sell_weapon(message, uID, recall,weapon_name):
    global Players
    global Weapons
    player = findPlayer(uID)
    if (player == None):
        return True
    weapon_id= no_weapon_id
    if(weapon_name == None):
        weapon_id = player.wID
    else:
        weapon_data = remove_weapon_from_store(player,weapon_name)
        if(weapon_data == None):
            if(get_weapon_from_id(player.wID).name.lower() == weapon_name):
                weapon_name = None
                weapon_id = player.wID
            if(weapon_name != None):
                await get_client(message.server.id).send_message(message.channel, ":bangbang: **Weapon not found!**")
                return
        if(weapon_data != None):
            weapon_id = weapon_data[0]
    if (weapon_id != no_weapon_id):
        weapon = get_weapon_from_id(weapon_id)
        price = int(((weapon.chance/100) * weapon.attack) / 0.04375)
        sellPrice = int(price - (price / 4))
        if(not recall):
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** sold their trusty " +weapon.name + " for $" +util.to_money(sellPrice,False)+ "!")
        else:
            if(weapon_name == None):
                sellPrice = int(util.get_strings(player.wep_sum)[0])
            else:
                sellPrice = int(util.get_strings(weapon_data[1])[0])
            await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** your weapon has been recalled by the manufacturer. You get a full $" + util.to_money(sellPrice,False) + " refund.")
        if(weapon_name == None):
            player.wID = no_weapon_id
            player.wep_sum = get_weapon_sum(no_weapon_id)
        player.money = player.money + sellPrice
        savePlayer(player)
    else:
        await get_client(message.server.id).send_message(message.channel, "**"+player.name+"** nothing does not fetch a good price...")

# quest, wager normal
def battle(ctx,**battleargs):
    current_move = 1
    damage_modifier = 1.5
    
    players = [battleargs['player_one'], battleargs['player_two']]
    hp = [players[0].hp * util.clamp(5 - players[0].level,1,5), players[1].hp * util.clamp(5 - players[1].level,1,5)]

    moves = OrderedDict()
    
    def add_move(player_no):
        nonlocal players, moves, current_move, damage_modifier
        
        other_player_no = 0 if player_no == 1 else 1
        BABY_MOVES = ["slapped","scratched","hit","punched","licked","bit","kicked","tickled"]
        weapon = players[player_no].weapon      
        message = ""
                                  
        if weapon.w_id == weapons.NO_WEAPON_ID:
            message = random.choice(BABY_MOVES) 
        else:
            message = weapon.hit_message
                  
        moves[str(player_no)+'/'+str(current_move)] = ['**'+players[player_no].clean_name +'** '+ message +' **'+players[other_player_no].clean_name+'**',1]
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
            last_move = move
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
            last_move = move
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
              
        nonlocal players, damage_modifier
        
        if successful_hit_from == None:
            successful_hit_from = 0 if bool(random.getrandbits(1)) else 1
        else:
            winner_player = players[successful_hit_from]
            loser_player = players[0 if successful_hit_from == 1 else 1]
            weapon_damage_modifier = winner_player.attack
            if not winner_player.weapon.melee:
                weapon_damage_modifier = winner_player.accy
            hp[players.index(loser_player)] -= (winner_player.weapon.damage * weapon_damage_modifier)/loser_player.strg * damage_modifier
            add_move(successful_hit_from)
                  
    while hp[0] > 0 and hp[1] > 0:
        player_one_hit = players[0].weapon_hit()
        player_two_hit = players[1].weapon_hit()
        
        if player_one_hit:
            hit(0)
        if player_two_hit:
            hit(1)
        if not (player_one_hit or player_two_hit):
            hit(None)
            
    compress_moves()
    winner = None
    loser = None
    if hp[0] > hp[1]:
        winner = players[0]
        loser = players[1]
    elif hp[0] < hp[1]:
        winner = players[1]
        loser = players[0]
    moves["winner"] = [":trophy: **"+winner.clean_name+"** wins in **" +str(current_move-1) + "** turns!",1]
    return [moves,current_move-1]
