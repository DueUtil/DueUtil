"""
Global vars
"""
# General "Config"
import sys
import json
from datetime import datetime


DUE_COLOUR = 9819069
DUE_COMMANDER_ROLE = "Due Commander"
DUE_OPTOUT_ROLE = "Due Optout"

# Colour defaults to colour
DUE_ROLES = ({"name": DUE_COMMANDER_ROLE}, {"name": DUE_OPTOUT_ROLE, "colour": 0})

trello_api_key = "[REDACTED]"
trello_api_token = "[REDACTED]"
trello_board = "https://trello.com/b/1ykaASKj/dueutil"

# Silly things:
DEAD_BOT_ID = "173391791884599297"
DUE_START_DATE = datetime.utcfromtimestamp(1498820132)

# Misc
THE_DEN = "213007664005775360"
DONOR_ROLE_ID = "343059674054262814"
# Cap for all things. Quests, weapons and wagers.
THING_AMOUNT_CAP = 120

BOT_INVITE = "https://dueutil.tech/invite"

VERSION = "Release 2.0.6.2"


def load_config_json():
    try:
        with open('dueutil.json') as config_file:
            return json.load(config_file)
    except Exception as exception:
        sys.exit("Config error! %s" % exception)


other_configs = load_config_json()


#### LOADED FROM dueutil.json config
error_channel = other_configs.get("errorChannel")
bug_channel = other_configs.get("bugChannel")
log_channel = other_configs.get("logChannel")
feedback_channel = other_configs.get("feedbackChannel")
announcement_channel = other_configs.get("announcementsChannel")
