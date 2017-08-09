"""
Global vars
"""
import sys
import json
from datetime import datetime

DUE_COLOUR = 9819069

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
DUE_START_DATE = datetime.fromtimestamp(1498820132)

# Misc
THE_DEN = "213007664005775360"
DONOR_ROLE_ID = "343059674054262814"

BOT_INVITE = "https://dueutil.tech/invite"

VERSION = "Release 2.0.6"


def load_config_json():
    try:
        with open('dueutil.json') as config_file:
            return json.load(config_file)
    except Exception as exception:
        sys.exit("Config error! %s" % exception)


other_configs = load_config_json()
