import discord
from . import weapons
from botstuff import util
import random 
from collections import OrderedDict
import generalconfig as gconf 
from collections import namedtuple

# Some tuples for use within this module.
_BattleResults = namedtuple("BattleResults",["moves","turns_count","winner","loser"])
_BattleLog = namedtuple("BattleLog",["embed","turns_count","winner","loser"])
_Move = namedtuple("Move",["message","repetitions"])
_OpponentInfo = namedtuple("OpponentInfo",["prefix","player"])
_Opponents = namedtuple("Opponents",["p1","p2"])

"""
        ===################===============                                           
        ===###   ####   ###   |   |   O  =====================================================
        ===################   |===|   |  I was meant to fill up white space but python sucks ===    
        ===###          ###   |   |   |  =====================================================
        ===################===============
"""
       
class BattleRequest:
  
    """A class to hold a wager"""
    
    __slots__ = ["sender_id","receiver_id","wager_amount"]
  
    def __init__(self,sender,receiver,wager_amount):
        self.sender_id = sender.id
        self.receiver_id = receiver.id
        self.wager_amount = wager_amount
        self._add(receiver)
        
    def _add(self,receiver):
        receiver.received_wagers.append(self)
        receiver.save()

def get_battle_log(**battleargs):
  
    """
    Creates a formatted embed of a battle
    """
    
    battle_result = battle(**battleargs)
    battle_moves = list(battle_result.moves.values())
    battle_embed = discord.Embed(title=(battleargs.get('player_one').name_clean
                                        +" :vs: "+battleargs.get('player_two').name_clean),type="rich",color=gconf.EMBED_COLOUR)
    battle_log = ""
    for move in battle_moves:
        move_repetition = move.repetitions
        if move_repetition <= 1:
            battle_log += move.message + '\n'
        else:
            battle_log += "(%s) × %d\n" % (move.message,move.repetitions)
    battle_embed.add_field(name='Battle log',value=battle_log)
    battle_info = battle_result._asdict()
    del battle_info["moves"]
    return _BattleLog(embed = battle_embed,**battle_info)

# quest, wager normal
def battle(**battleargs):
  
    """
    Battles two player like things.
    Will return a log of the battle
    """
    
    current_move = 1
    damage_modifier = 1.5
    
    opponents = _Opponents(p1 = _OpponentInfo(prefix = battleargs.get('p1_prefix',""),
                                              player = battleargs.get('player_one')),
                           p2 = _OpponentInfo(prefix = battleargs.get('p2_prefix',""),
                                              player = battleargs.get('player_two')))
    
    hp = [opponents.p1.player.hp * util.clamp(5 - opponents.p1.player.level,1,5),
          opponents.p2.player.hp * util.clamp(5 - opponents.p2.player.level,1,5)]

    moves = OrderedDict()
    
    def add_move(attacker,other,message = None):
        nonlocal opponents, moves, current_move, damage_modifier
        if message == None:
            BABY_MOVES = ("slapped","scratched","hit","punched","licked","bit","kicked","tickled")
            weapon = attacker.player.weapon      
            if weapon.id == weapons.NO_WEAPON_ID:
                message = random.choice(BABY_MOVES) 
            else:
                message = weapon.hit_message

        moves['%d/%d'%(opponents.index(attacker),
                       current_move)] = _Move(message = ("%s**%s** %s %s**%s**" 
                                                          % (attacker.prefix,
                                                             attacker.player.name_clean,
                                                             message,
                                                             other.prefix,
                                                             other.player.name_clean)
                                                        ),repetitions = 1)
        
        current_move += 1
        damage_modifier += 0.5

    def shrink_repeats(moves):
      
        """
        Replaces consecutive repeated moves with 
        moves with a single move with "repetitions"
        """
        
        last_move_id = None
        moves_shrink_repeat = OrderedDict()
        for move_id, move in moves.items():
            if last_move_id != None:
                # If last move and this move are from the same player
                if last_move_id[0] == move_id[0]:
                    last_move = moves_shrink_repeat[last_move_id]
                    move = move._replace(repetitions = move.repetitions + last_move.repetitions)
                    move_id = last_move_id
            moves_shrink_repeat[move_id] = move
            last_move_id = move_id
        return moves_shrink_repeat
    
    def shrink_duos(moves):
      
        """
        Replaces moves that swich between players. With a single duo move.
        
        E.g.
        
        P1 hits P2
        P2  hits P1
        
        to P1 hits P2 <-> P2 Hits P1
        """
        
        moves_shrink_duos = OrderedDict()
        last_move_id = None
        count = 0
        for move_id, move in moves.items():
            count += 1
            if last_move_id != None and count % 2 == 0:
                last_move = moves[last_move_id]
                moves_shrink_duos[last_move_id] = last_move._replace(repetitions = last_move.repetitions - 1)
                
                moves_shrink_duos["Duo%d"%count] = _Move(message = last_move.message +" ⇆ "+ move.message,
                                                         repetitions = 1)
                moves_shrink_duos[move_id] = move._replace(repetitions = move.repetitions -1)
            last_move_id = move_id
        if len(moves) % 2 == 1:
            # Add missed move
            odd_move = moves.popitem()
            moves_shrink_duos[odd_move[0]] = odd_move[1]
        for move_id, move in list(moves_shrink_duos.items()):
            if move.repetitions <= 0:
                del moves_shrink_duos[move_id]
        return moves_shrink_duos
                
    def compress_moves():
      
        """
        Shorcut for the full process to shrink the log
        """
        nonlocal moves
        moves = shrink_repeats(shrink_duos(shrink_repeats(moves)))
    
    def fight():
        nonlocal opponents, damage_modifier
        
        hits = [opponents.p1.player.weapon_hit(),
                opponents.p2.player.weapon_hit()]
        
        for hitter,hit in enumerate(hits):
            if hit:
                attacker = opponents.p1 if hitter == 0 else opponents.p2
                other = opponents[1-opponents.index(attacker)]
                weapon_damage_modifier = attacker.player.attack
                if not attacker.player.weapon.melee:
                    weapon_damage_modifier = attacker.player.accy
                # Deal damage
                hp[1-hitter] -= (attacker.player.weapon.damage * weapon_damage_modifier)/other.player.strg * damage_modifier
                add_move(attacker,other)
                  
    while hp[0] > 0 and hp[1] > 0:
        fight()
            
    compress_moves()
    if hp[0] > hp[1]:
        winner = opponents.p1
        loser = opponents.p2
    elif hp[0] < hp[1]:
        winner = opponents.p2
        loser = opponents.p1

    turns = current_move-1
    moves["winner"] = _Move(message = (":trophy: %s**%s** wins in **%d** turn%s!" 
                                        % (winner.prefix,
                                           winner.player.name_clean,
                                           turns,
                                           "s" if turns != 1 else "")
                                      ),repetitions = 1)
    # Results as a simple namedturple
    return _BattleResults(moves = moves,turns_count = turns,winner = winner.player,loser = loser.player)
