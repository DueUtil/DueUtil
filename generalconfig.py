"""
Global vars
"""
import sys
import json

EMBED_COLOUR = 16038978

trello_api_key = "a37e7838639da4b8e7e2d0da652cb40a"
trello_api_token = "3ef525e21139f7ad9bff80e9353bd9e9c38fc316dc70bb3b4122e937a4c9d97f"
trello_board = "https://trello.com/b/1ykaASKj/dueutil"

#### LOADED FROM dueutil.json config
error_channel = None
bug_channel = None
report_channel = None
log_channel = None
feedback_channel = None
announcement_channel = None

# Silly things:
DEAD_BOT_ID = "173391791884599297"
DISCORD_TEL_ID = "224662505157427200"
DISCORD_TEL_SERVER = "281815661317980160"
DISCORD_TEL_CHANNEL = "329013929890283541"

# Misc

BOT_INVITE = "https://dueutil.tech/invite"

VERSION = "Release 2.0.5"


def load_config_json():
    try:
        with open('dueutil.json') as config_file:
            return json.load(config_file)
    except Exception as exception:
        sys.exit("Config error! %s" % exception)


other_configs = load_config_json()
