import json
from .. import dbconn

exp_per_level = dict()

"""
Some values needed for player, quests & etc
"""


def _load_game_rules():
    with open('dueutil/game/configs/progression.json') as progression_file:
        progression = json.load(progression_file)
        exp = progression["dueutil-ranks"]
        # for web
        expanded_exp_per_level = dict()
        for levels, exp_details in exp.items():
            if "," in levels:
                level_range = eval("range(" + levels + "+1)")
            else:
                level_range = eval("range(" + levels + "," + levels + "+1)")
            exp_expression = str(exp_details["expForNextLevel"])
            expanded_exp_per_level[','.join(map(str, level_range))] = exp_per_level[level_range] = exp_expression
    dbconn.drop_and_insert("gamerules", expanded_exp_per_level)


def get_exp_for_next_level(level):
    for level_range, exp_details in exp_per_level.items():
        if level in level_range:
            return int(eval(exp_details.replace("oldLevel", str(level))))
    return -1


def get_exp_for_level(level):
    return sum([get_exp_for_next_level(level) for level in range(1, level)])


def get_level_from_exp(exp):
    level = 1
    while 1:
        exp -= get_exp_for_next_level(level)
        if exp < 0:
            break
        level += 1
    return level


_load_game_rules()
