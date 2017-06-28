import json

exp_per_level = dict()

"""
Some values needed for player, quests & etc
"""


def _load_game_rules():
    with open('dueutil/game/configs/progression.json') as progression_file:
        progression = json.load(progression_file)
        exp = progression["dueutil-ranks"]
        for levels, exp_details in exp.items():
            if "," in levels:
                level_range = eval("range(" + levels + "+1)")
            else:
                level_range = eval("range(" + levels + "," + levels + "+1)")
            exp_expression = str(exp_details["expForNextLevel"])
            exp_per_level[level_range] = exp_expression


def get_exp_for_next_level(level):
    for level_range, exp_details in exp_per_level.items():
        if level in level_range:
            return eval(exp_details.replace("oldLevel", str(level)))
    return -1


_load_game_rules()
