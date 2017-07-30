import asyncio
import math
import random
import time
from collections import defaultdict
from copy import copy

import discord
import jsonpickle
import numpy

from ..util import SlotPickleMixin
from .. import dbconn, util, tasks
from ..game import awards
from ..game import weapons
from ..game import gamerules
from ..game.helpers.misc import DueUtilObject, Ring
from . import customizations
from .customizations import Theme

""" Player related classes & functions """


class Players(dict):
    # Amount of time before the bot will prune a player.
    PRUNE_INACTIVITY_TIME = 3600  # (1 Hour)

    def prune(self):

        """
        Removes player that the bot has not seen 
        for over an hour. If anyone metions these
        players (in a command) their data will be
        fetched directly from the database
        """
        players_pruned = 0
        for id, player in list(self.items()):
            if time.time() - player.last_progress >= Players.PRUNE_INACTIVITY_TIME:
                del self[id]
                players_pruned += 1
        util.logger.info("Pruned %d players for inactivity", players_pruned)


players = Players()


@tasks.task(timeout=3600)
def prune_task():
    try:
        players.prune()
    except RuntimeError as exception:
        util.logger.warning("Failed to prune players: %s" % exception)


class Player(DueUtilObject, SlotPickleMixin):
    """
    The DueUtil player!
    This (and a few other classes) are very higgledy-piggledy due to
    being make very early on in development & have been changed so many
    times while trying not to break older versions & code.
    
    defaultdict is to hold sets of attributes that can be changed/Added to
    randomly.
    
    It allows attrs to be added automatically
    """

    # These are all the attrbs needed for a player
    # This is meant to optimize players. One caveat all new attributes
    # Must be a misc_stat, inventory item or equipped item
    __slots__ = ["level", "attack", "strg", "hp",
                 "exp", "money", "total_exp", "accy",
                 "last_progress", "last_quest",
                 "wagers_won", "quests_won",
                 "quest_day_start", "benfont",
                 "quests_completed_today",
                 "spam_detections", "quests",
                 "received_wagers", "awards",
                 "quest_spawn_build_up", "donor",
                 "misc_stats", "equipped", "inventory",
                 "last_message_hashes", "command_rate_limits",
                 "additional_attributes"]

    # additional_attributes is not defined but is there for possible future use.
    # I expect new types of quests/weapons to be subclasses.

    DEFAULT_FACTORIES = {"equipped": lambda: "default", "inventory": lambda: ["default"]}

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and isinstance(args[0], discord.User):
            super().__init__(args[0].id, args[0].name, **kwargs)
            players[self.id] = self
        else:
            super().__init__("NO_ID", "DueUtil Player", **kwargs)
        self.reset()
        self.money = 100

    def reset(self, discord_user=None):

        ### New rule: The default of all new items MUST have the id default now.

        if discord_user is not None:
            self.name = discord_user.name
        self.benfont = False

        ##### STATS #####
        self.level = 1
        self.exp = 0
        self.total_exp = 0
        self.attack = 1
        self.strg = 1
        self.accy = 1
        self.hp = 10
        self.money = 0

        ##### USAGE STATS #####
        self.last_progress = 0
        self.last_quest = 0
        self.wagers_won = 0
        self.quests_won = 0
        self.quest_day_start = 0
        self.quests_completed_today = 0
        self.last_message_hashes = Ring(10)
        self.spam_detections = 0

        if not hasattr(self, "command_rate_limits"):
            self.command_rate_limits = {}

        ##### THINGS #####
        self.quests = []
        self.received_wagers = []

        if not hasattr(self, "awards"):
            self.awards = []
        else:
            # Keep special awards even after reset
            kept_awards = [award_id for award_id in self.awards if awards.get_award(award_id).special]
            # To ensure stats don't get weird
            for award_id in set(self.awards) - set(kept_awards):
                awards.update_award_stat(award_id, "times_given", -1)
            self.awards = kept_awards

        # To help the noobz
        self.quest_spawn_build_up = 1

        # lol no
        self.donor = False

        ##### Dumb misc stats (easy to add & remove)
        self.misc_stats = defaultdict(int,
                                      emojis_given=0,
                                      emojis=0,
                                      potatoes=0,
                                      potatoes_given=0,
                                      average_spelling_correctness=1,
                                      average_quest_battle_turns=1)

        ##### Equiped items
        self.equipped = defaultdict(Player.DEFAULT_FACTORIES["equipped"],
                                    weapon=weapons.NO_WEAPON_ID,
                                    banner="discord blue",
                                    theme="default",
                                    background="default")

        ##### Inventory. defaultdict so I can add more stuff - without fuss
        ##### Also makes shop simpler
        self.inventory = defaultdict(Player.DEFAULT_FACTORIES["inventory"],
                                     weapons=[],
                                     themes=["default"],
                                     backgrounds=["default"],
                                     banners=["discord blue"])

        self.save()

    def progress(self, attack, strg, accy, **options):
        max_attr = options.get('max_attr', 0.1)
        max_exp = options.get('max_exp', 15)
        self.attack += min(attack, max_attr)
        self.strg += min(strg, max_attr)
        self.accy += min(accy, max_attr)
        exp = min((attack + strg + accy) * 100, max_exp)
        self.exp += exp
        self.total_exp += exp

    def get_owned(self, item_type, all_items):
        return {item_id: item for item_id, item in all_items.items() if item_id in self.inventory[item_type]}

    def get_owned_themes(self):
        return self.get_owned("themes", customizations.themes)

    def get_owned_backgrounds(self):
        return self.get_owned("backgrounds", customizations.backgrounds)

    def get_owned_banners(self):
        return self.get_owned("banners", customizations.banners)

    def get_owned_weapons(self):
        return [weapons.get_weapon_from_id(weapon_id) for weapon_id in self.inventory["weapons"] if
                weapon_id != weapons.NO_WEAPON_ID]

    def get_weapon(self, weapon_name):
        return next((weapon for weapon in self.get_owned_weapons() if weapon.name.lower() == weapon_name.lower()), None)

    def owns_weapon(self, weapon_name):
        return self.get_weapon(weapon_name) is not None

    def get_name_possession(self):
        if self.name.endswith('s'):
            return self.name + "'"
        return self.name + "'s"

    def get_name_possession_clean(self):
        return util.ultra_escape_string(self.get_name_possession())

    def discard_stored_weapon(self, weapon):
        if weapon.id in self.inventory["weapons"]:
            self.inventory["weapons"].remove(weapon.id)
            return True
        return False

    def store_weapon(self, weapon):
        self.inventory["weapons"].append(weapon.id)

    def weapon_hit(self):
        return random.random() < self.weapon_accy

    def get_avatar_url(self, server=None, **extras):
        if server is None:
            member = extras.get("member")
        elif server is not None:
            member = server.get_member(self.id)
        else:
            raise ValueError("Invalid arguments")
        if member.avatar_url != "":
            return member.avatar_url
        return member.default_avatar_url

    def get_avg_stat(self):
        return sum((self.attack, self.strg, self.accy)) / 4

    @property
    def item_value_limit(self):
        # Take into account the progress in the current level.
        precise_level = self.level + self.exp / gamerules.get_exp_for_next_level(self.level)
        return int(30 * (math.pow(precise_level, 2) / 3
                         + 0.5 * math.pow(precise_level + 1, 2)
                         * precise_level))

    @property
    def rank(self):
        return self.level // 10

    @property
    def rank_colour(self):
        rank_colours = self.theme["rankColours"]
        return rank_colours[self.rank % len(rank_colours)]

    @property
    def weapon_accy(self):
        max_value = self.item_value_limit
        price = self.weapon.price if self.weapon.price > 0 else 1
        new_accy = numpy.clip(max_value / price * 100, 1, 86)
        new_accy = self.weapon.accy if new_accy > self.weapon.accy else new_accy
        return new_accy if price > max_value else self.weapon.accy

    @property
    def user_id(self):
        return self.id

    @property
    def weapon(self):
        return weapons.get_weapon_from_id(self.equipped["weapon"])

    @weapon.setter
    def weapon(self, weapon):
        self._setter("weapon", weapon)

    @property
    def background(self):
        current_background = self.equipped["background"]
        if current_background not in customizations.backgrounds:
            # Check (just to quick fix)
            # TODO: Remove later
            if current_background in self.inventory["backgrounds"]:
                self.inventory["backgrounds"].remove(current_background)
            self.equipped.background = "default"
        return customizations.backgrounds[self.equipped["background"]]

    @background.setter
    def background(self, background):
        self._setter("background", background)

    @property
    def banner(self):
        banner = customizations.banners.get(self.equipped["banner"],
                                            customizations.banners["discord blue"])
        if not (self.equipped["banner"] in customizations.banners or banner.can_use_banner(self)):
            self.inventory["banners"].remove(self.equipped["banner"])
            self.equipped["banner"] = "discord blue"
        return banner

    @banner.setter
    def banner(self, banner):
        self._setter("banner", banner)

    @property
    def theme(self):
        current_theme = self.equipped["theme"]
        if current_theme in customizations.themes:
            theme = copy(customizations.themes[current_theme])
        else:
            theme = customizations.themes["default"].copy()
        if theme["background"] != self.equipped["background"]:
            theme["background"] = self.equipped["background"]
        if theme["banner"] != self.equipped["banner"]:
            theme["banner"] = self.equipped["banner"]
        return theme

    @theme.setter
    def theme(self, theme):
        self._setter("theme", theme)
        if not isinstance(theme, Theme):
            theme = customizations.themes[theme]
        self.equipped["banner"] = theme["banner"]
        self.equipped["background"] = theme["background"]

    def _setter(self, thing, value):
        if isinstance(value, DueUtilObject):
            self.equipped[thing] = value.id
        elif isinstance(value, str):
            self.equipped[thing] = value
        else:
            raise util.BotException("%s cannot be set to %s" % (thing, value))

    def __setstate__(self, object_state):
        SlotPickleMixin.__setstate__(self, object_state)
        # TODO Remove:
        if not hasattr(self, "command_rate_limits"):
            self.command_rate_limits = {}
        self.last_message_hashes = Ring(10)
        self.inventory = defaultdict(Player.DEFAULT_FACTORIES["inventory"], **self.inventory)
        self.equipped = defaultdict(Player.DEFAULT_FACTORIES["equipped"], **self.equipped)
        self.misc_stats = defaultdict(int, **self.misc_stats)
        for quest in self.quests:
            quest.quester = self

    def __getstate__(self):
        object_state = SlotPickleMixin.__getstate__(self)
        del object_state["last_message_hashes"]
        object_state["command_rate_limits"] = {command_name: last_used for (command_name, last_used) in
                                               self.command_rate_limits.items()
                                               if command_name.endswith("_saved_cooldown")}
        if len(object_state["command_rate_limits"]) == 0:
            del object_state["command_rate_limits"]
        # Know need to save the default dict info (as the
        # defaults are known)
        object_state["inventory"] = dict(object_state["inventory"])
        object_state["equipped"] = dict(object_state["equipped"])
        object_state["misc_stats"] = dict(object_state["misc_stats"])
        return object_state


def find_player(user_id: str) -> Player:
    if user_id in players:
        return players[user_id]
    elif load_player(user_id):
        return players[user_id]


REFERENCE_PLAYER = Player(no_save=True)


def load_player(player_id):
    response = dbconn.get_collection_for_object(Player).find_one({"_id": player_id})
    if response is not None and 'data' in response:
        player_data = response['data']
        loaded_player = jsonpickle.decode(player_data)
        players[loaded_player.id] = util.load_and_update(REFERENCE_PLAYER, loaded_player)
        return True
