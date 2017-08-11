import re

from .game.helpers import misc
from .game import players
from .permissions import Permission
from . import util

# The max number the bot will accept. To avoid issues with crazy big numbers.
MAX_NUMBER = 99999999999999999999999999999999999999999999
MIN_NUMBER = -MAX_NUMBER
STRING_TYPES = ('S', 'M')


def represents_int(value):
    # An int limited between min and max number
    try:
        return util.clamp(int(value), MIN_NUMBER, MAX_NUMBER)
    except ValueError:
        return False


def represents_string(value):
    # When is a string not a string?
    """
    This may seem dumb. But not all strings are strings in my
    world. Fuck zerowidth bullshittery & stuff like that.

    -xoxo MacDue
    """
    # Remove zero width bullshit & extra spaces
    value = re.sub(r'[\u200B-\u200D\uFEFF]', '', value.strip())
    # Remove extra spaces/tabs/new lines ect.
    value = " ".join(value.split())
    if len(value) > 0:
        return value
    return False


def represents_count(value):
    # The counting numbers.
    # Natural numbers starting from 1
    int_value = represents_int(value)
    if not int_value:
        return False
    elif int_value - 1 >= 0:
        return int_value


def represents_float(value):
    # Float between min and max number
    try:
        return util.clamp(float(value), MIN_NUMBER, MAX_NUMBER)
    except ValueError:
        return False


def represents_player(player_id, called):
    # A DueUtil Player
    player = players.find_player(player_id)
    if player is None or not player.is_playing() \
            and called.permission < Permission.DUEUTIL_MOD:
        return False
    return player


def represents_type(arg_type, value, called=None):
    return {
        'S': represents_string(value),
        'I': represents_int(value),
        'C': represents_count(value),
        'R': represents_float(value),
        'P': represents_player(value, called),
        # This one is for page selectors that could be a page number or a string like a weapon name.
        'M': represents_count(value) if represents_count(value) else value,
        'B': value.lower() in misc.POSITIVE_BOOLS,
    }.get(arg_type)
