import json
import random
from collections import defaultdict
from typing import Dict, List

import discord
import jsonpickle

from ..util import SlotPickleMixin
from .. import dbconn
from .. import util
from ..game import players
from ..game import weapons
from ..game.helpers.misc import DueUtilObject, DueMap
from .players import Player

quest_map = DueMap()

MIN_QUEST_IV = 0
QUEST_DAY = 86400
QUEST_COOLDOWN = 360
MAX_DAILY_QUESTS = 50
MAX_ACTIVE_QUESTS = 10


class Quest(DueUtilObject, SlotPickleMixin):
    """A class to hold info about a server quest"""

    __slots__ = ["server_id", "created_by",
                 "task", "w_id", "spawn_chance", "image_url",
                 "base_attack", "base_strg", "base_accy", "base_hp",
                 "channel", "times_beaten"]

    def __init__(self, name, base_attack, base_strg, base_accy, base_hp, **extras):
        message = extras.get('ctx', None)
        given_spawn_chance = extras.get('spawn_chance', 4)

        if message is not None:
            if message.server in quest_map:
                if name.lower() in quest_map[message.server]:
                    raise util.DueUtilException(message.channel, "A foe with that name already exists on this server!")

            if base_accy < 1 or base_attack < 1 or base_strg < 1:
                raise util.DueUtilException(message.channel, "No quest stats can be less than 1!")

            if base_hp < 30:
                raise util.DueUtilException(message.channel, "Base HP must be at least 30!")

            if len(name) > 30 or len(name) == 0 or name.strip == "":
                raise util.DueUtilException(message.channel, "Quest names must be between 1 and 30 characters!")

            if given_spawn_chance > 25:
                raise util.DueUtilException(message.channel, "Spawn chance cannot be greater than 25%")

            self.server_id = message.server.id
            self.created_by = message.author.id
        else:
            self.server_id = extras.get('server_id', "DEFAULT")
            self.created_by = ""

        self.name = name
        super().__init__(self._quest_id(), **extras)
        self.task = extras.get('task', "Battle a")
        self.w_id = extras.get('weapon_id', weapons.NO_WEAPON_ID)
        self.spawn_chance = given_spawn_chance / 100
        self.image_url = extras.get('image_url', "")
        self.base_attack = base_attack
        self.base_strg = base_strg
        self.base_accy = base_accy
        self.base_hp = base_hp
        self.channel = extras.get('channel', "ALL")
        self.times_beaten = 0
        self._add()
        self.save()

    def _quest_id(self):
        return self.server_id + '/' + self.name.lower()

    def _add(self):
        global quest_map
        if self.server_id != "":
            quest_map[self.id] = self

    def base_values(self):
        return (self.base_hp, self.base_attack,
                self.base_strg, self.base_accy,)

    @property
    def made_on(self):
        return self.server_id

    @property
    def creator(self):
        creator = players.find_player(self.created_by)
        if creator is not None:
            return creator.name
        else:
            return "Unknown"

    @property
    def q_id(self):
        return self.id

    @property
    def home(self):
        try:
            return util.get_client(self.server_id).get_server(self.server_id).name
        except:
            return "Unknown"


class ActiveQuest(Player, util.SlotPickleMixin):
    __slots__ = ["level", "attack", "strg", "hp",
                 "equipped", "q_id", "quester_id", "cash_iv",
                 "quester", "accy"]

    def __init__(self, q_id, quester: Player):
        # The base quest (holds the quest information)
        self.q_id = q_id
        base_quest = self.info

        self.name = base_quest.name

        self.quester_id = quester.id
        self.quester = quester

        """ The quests equipped items.
        Quests only have weapons but I may add more things a quest
        can have so a default dict will help with that """
        self.equipped = defaultdict(lambda: "default",
                                    weapon=base_quest.w_id)

        self.level = random.randint(quester.level, quester.level * 2)
        self._calculate_stats()
        quester.quests.append(self)
        quester.save()

    def _calculate_stats(self, **spoof_values):
        # HP is not the same! Don't treat it as such
        base_values = self.info.base_values()
        stats = []
        # For testing purposes only
        avg_quester_stat = spoof_values.get('q_stats', self.quester.get_avg_stat())
        weapon_damage = spoof_values.get('w_damage', self.weapon.damage)
        weapon_accy = spoof_values.get('w_accy', self.weapon.accy)
        avg_base_value = sum(base_values[1:]) / 4
        quester_stat_per_level = avg_quester_stat / self.quester.level
        quester_hp_per_level = self.quester.hp / self.quester.level
        for stat_calculation in range(1, 4):
            iv = random.uniform(MIN_QUEST_IV, avg_base_value)
            stat = (base_values[stat_calculation] + iv + quester_stat_per_level) / 3 * self.level + self.level
            stats.append(stat)
        hp_iv = random.uniform(30, base_values[0])
        self.hp = (base_values[0] + hp_iv + quester_hp_per_level) / 3 * self.level + self.level
        self.attack = stats[0]
        self.strg = stats[1]
        self.accy = stats[2]
        self.cash_iv = random.uniform(MIN_QUEST_IV, avg_base_value) * weapon_damage * (weapon_accy / 100)

    def get_avatar_url(self, *args):
        quest_info = self.info
        if quest_info is not None:
            return quest_info.image_url

    def get_reward(self):
        if not hasattr(self, "cash_iv"):
            self.cash_iv = 0
        avg_stat = self.get_avg_stat()
        hp_scale = self.hp / self.quester.hp
        reward_multiplier = (avg_stat / self.quester.get_avg_stat() + hp_scale) / 2
        return int(avg_stat / self.quester.level * self.cash_iv / self.get_quest_scale() * reward_multiplier) + 1

    def get_quest_scale(self):
        quester_weapon = self.quester.weapon
        scale_value = (quester_weapon.damage * (quester_weapon.accy / 100)
                       / max(1, (MAX_DAILY_QUESTS - self.quester.quests_completed_today) / 2))
        return max(1 / 3, scale_value)

    def get_threat_level(self, player):
        return [
            player.attack / max(player.attack, self.attack),
            player.strg / max(player.strg, self.strg),
            player.accy / max(player.accy, self.accy),
            self.money / max(player.money, self.money),
            player.weapon.damage / max(player.weapon.damage, self.weapon.damage)
        ]

    @property
    def money(self):
        return self.get_reward()

    @money.setter
    def money(self, value):
        pass

    @property
    def info(self):
        return quest_map[self.q_id]

    def save(self):
        pass

    def __setstate__(self, object_state):
        SlotPickleMixin.__setstate__(self, object_state)
        """ quester is set in the player's setstate
        as quests are part of the player's save.
        Also we don't want to inherit the Player setstate.
         """
        self.equipped = defaultdict(self.DEFAULT_FACTORIES["equipped"], **self.equipped)

    def __getstate__(self):
        object_state = SlotPickleMixin.__getstate__(self)
        del object_state["quester"]
        object_state["equipped"] = dict(object_state["equipped"])
        return object_state


def get_server_quest_list(server: discord.Server) -> Dict[str, Quest]:
    return quest_map[server]


def get_quest_on_server(server: discord.Server, quest_name: str) -> Quest:
    return quest_map[server.id + "/" + quest_name.lower()]


def remove_quest_from_server(server: discord.Server, quest_name: str):
    quest_id = server.id + "/" + quest_name.lower()
    del quest_map[quest_id]
    dbconn.get_collection_for_object(Quest).remove({'_id': quest_id})


def get_quest_from_id(quest_id: str) -> Quest:
    return quest_map[quest_id]


def get_channel_quests(channel: discord.Channel) -> List[Quest]:
    return [quest for quest in quest_map[channel.server].values() if quest.channel in ("ALL", channel.id)]


def get_random_quest_in_channel(channel):
    if channel.server in quest_map:
        return random.choice(get_channel_quests(channel))


def add_default_quest_to_server(server):
    default = random.choice(list(quest_map["DEFAULT"].values()))
    Quest(default.name,
          default.base_attack,
          default.base_strg,
          default.base_accy,
          default.base_hp,
          task=default.task,
          weapon_id=default.w_id,
          image_url=default.image_url,
          spawn_chance=default.spawn_chance * 100,
          server_id=server.id,
          no_save=True)


def has_quests(place):
    if isinstance(place, discord.Server):
        return place in quest_map and len(quest_map[place]) > 0
    elif isinstance(place, discord.Channel):
        if place.server in quest_map:
            return len(get_channel_quests(place)) > 0
    return False


REFERENCE_QUEST = Quest('Reference', 1, 1, 1, 1, server_id="", no_save=True)


def _load():
    def load_default_quests():
        with open('dueutil/game/configs/defaultquests.json') as defaults_file:
            defaults = json.load(defaults_file)
            for quest_data in defaults.values():
                Quest(quest_data["name"],
                      quest_data["baseAttack"],
                      quest_data["baseStrg"],
                      quest_data["baseAccy"],
                      quest_data["baseHP"],
                      task=quest_data["task"],
                      weapon_id=weapons.stock_weapon(quest_data["weapon"]),
                      image_url=quest_data["image"],
                      spawn_chance=quest_data["spawnChance"],
                      no_save=True)

    load_default_quests()

    for quest in dbconn.get_collection_for_object(Quest).find():
        loaded_quest = jsonpickle.decode(quest['data'])
        quest_map[loaded_quest.id] = util.load_and_update(REFERENCE_QUEST, loaded_quest)


_load()
