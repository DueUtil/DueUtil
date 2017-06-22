import json
from PIL import Image
from ..configs import dueserverconfig
from botstuff import util

awards = dict()

"""
DueUtil awards
"""


class Award:
    __slots__ = ["name", "description", "icon", "special"]

    # Colour for special award text & stuff
    SPECIAL_AWARD_COLOUR = "#4B0082"

    def __init__(self, icon_name, name, description, special=False):
        self.name = name
        self.description = description
        self.special = special
        self.icon = Image.open("awards/" + icon_name)

    def get_colour(self, default="white"):
        return Award.SPECIAL_AWARD_COLOUR if self.special else default


def get_award(award_id: str) -> Award:
    if award_id in awards:
        return awards[award_id]


def _load():
    with open('fun/configs/awards.json') as awards_file:
        awards_json = json.load(awards_file)
        for award_id, award in awards_json["awards"].items():
            awards[award_id] = Award(award["icon"],
                                     award["name"],
                                     award.get('message', "???"),
                                     award.get('special', False))


async def give_award(channel, player, award_id, text):
    if get_award(award_id) is not None and award_id not in player.awards:
        player.awards.append(award_id)
        player.save()
        if not channel.is_private and dueserverconfig.mute_level(channel) < 0:
            await util.say(channel, "**" + player.name_clean + "** :trophy: **Award!** " + text)


_load()
