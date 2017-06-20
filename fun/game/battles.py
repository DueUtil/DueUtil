import discord
from . import weapons
from botstuff import util
import random 
from collections import OrderedDict
import generalconfig as gconf 
            
class BattleRequest:
  
    """A class to hold a wager"""
    
    __slots__ = ["sender_id","receiver_id","wager_amount"]
  
    def __init__(self,sender,receiver,wager_amount):
        self.sender_id = sender.id
        self.receiver_id = receiver.id
        self.wager_amount = wager_amount
        self.__add(receiver)
        
    def __add(self,receiver):
        receiver.received_wagers.append(self)
        receiver.save()

def get_battle_log(**battleargs):
  
    """
    Creates a formatted embed of a battle
    """
    
    battle_result = battle(**battleargs)
    battle_moves = list(battle_result[0].values())
    battle_embed = discord.Embed(title=(battleargs['player_one'].name_clean
                                        +" :vs: "+battleargs['player_two'].name_clean),type="rich",color=gconf.EMBED_COLOUR)
    battle_log = ""
    for move in battle_moves:
        move_repetition = move[1]
        if move_repetition <= 1:
            battle_log += move[0] + '\n'
        else:
            battle_log += '('+ move[0] +') × ' + str(move_repetition) + '\n'
    battle_embed.add_field(name='Battle log',value=battle_log)
    return [battle_embed]+battle_result[1:]

# quest, wager normal
def battle(**battleargs):
  
    """
    Battles two player like things.
    Will return a log of the battle
    """
    
    current_move = 1
    damage_modifier = 1.5
    
    prefixes = [battleargs.get('p1_prefix',""),battleargs.get('p2_prefix',"")]

    players = [battleargs['player_one'], battleargs['player_two']]
    hp = [players[0].hp * util.clamp(5 - players[0].level,1,5), players[1].hp * util.clamp(5 - players[1].level,1,5)]

    moves = OrderedDict()
    
    def add_move(player_no):
        nonlocal players, moves, current_move, damage_modifier
        
        other_player_no = player_no-1
        BABY_MOVES = ("slapped","scratched","hit","punched","licked","bit","kicked","tickled")
        weapon = players[player_no].weapon      
        message = ""
        if weapon.w_id == weapons.NO_WEAPON_ID:
            message = random.choice(BABY_MOVES) 
        else:
            message = weapon.hit_message

        moves[str(player_no)+'/'+str(current_move)] = ([prefixes[player_no].title()+'**'+players[player_no].name_clean 
                                                       +'** '+ message +' '+prefixes[other_player_no]+'**'+players[other_player_no].name_clean+'**',1])
                                                    
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
    turns = str(current_move-1)
    moves["winner"] = [(":trophy: "+prefixes[players.index(winner)].title()+"**"
                        +winner.name_clean+"** wins in **" +turns+ "** turn"
                        +("s" if turns != 1 else "")+"!"),1]
    return [moves,current_move-1,winner,loser,turns]
