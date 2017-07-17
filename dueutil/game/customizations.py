import json
import os

import discord
from PIL import Image

from .. import permissions, util
from ..game.helpers.misc import DueUtilObject
from ..permissions import Permission

from typing import Dict

"""

Basic classes to store themes, backgrounds and banners.

"""


# Both Theme & Background used to be an extension of dict and DUObj
# but had to be changed due to __slots__

class Customization(DueUtilObject):
    __slots__ = ["_customization_info"]

    # Use kwargs so maybe I could neatly define customizations in code.
    def __init__(self, id, **customization_info):
        self._customization_info = customization_info
        super().__init__(id, self["name"])

    def is_hidden(self):
        return self._customization_info.get('hidden', False)

    def __getattr__(self, name):
        """
        This helps customizations have both a dict & object
        interface
        """
        try:
            return self[name]
        except KeyError as exception:
            #### ULTRA WARNING!!!!!!!
            #### THIS ERROR MAY LIE
            raise AttributeError("%s has no attribute or index named %s" % (type(self).__name__, name)) from exception

    # Most customizations are read only & don't need to set values

    def __contains__(self, key):
        return key in self._customization_info

    def __getitem__(self, key):
        return self._customization_info[key]


class Theme(Customization):
    """
    Simple class to hold them data and
    be able to access DUObj methods
    
    Needs item setting & copying to support
    overriding theme attributes
    """

    __slots__ = []

    def __init__(self, id, **theme_data):
        super().__init__(id, **theme_data)

    def __copy__(self):
        return Theme(id, **self._customization_info)

    def __setitem__(self, key, value):
        self._customization_info[key] = value


class _Themes(dict):
    PROFILE_PARTS = ("screen", "avatar", "icons")

    def __init__(self):
        super().__init__()
        self._load_themes()

    @staticmethod
    def _find_part(part_name, path):
        while True:
            file_list = os.listdir(path)
            parent_path = os.path.dirname(path)
            if part_name in file_list:
                return os.path.join(path, part_name)
            else:
                if path == "themes/":
                    return "assets/themes/default/%s" % part_name
                else:
                    path = parent_path

    def _load_themes(self):

        """
        Theme loader.

        Finds json files in the theme directory.
        Loads them & finds the asset (images) for the themes.
        Checking the theme directory, if they are not there then
        it uses the assets in the parent directory (allowing for
        some basic theme inheritance & not needing to spec assets
        in the json). Default assets are used if none are found.
        """

        self.clear()
        for path, subdirs, files in os.walk("assets/themes/"):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(path, name)) as theme_json:
                        theme_details = json.load(theme_json)["theme"]
                        theme_id = theme_details["name"].lower()
                        for part in _Themes.PROFILE_PARTS:
                            theme_details[part] = _Themes._find_part(part + ".png", path)
                        self[theme_id] = Theme(theme_id, **theme_details)
        # This needs to be done after main load to be sure defaults are loaded.
        for theme in self.values():
            if "rankColours" not in theme:
                theme["rankColours"] = self["default"]["rankColours"]


class Background(Customization):
    __slots__ = ["image"]

    """
    Unlike Theme copy() & setting background data should
    never be needed
    """

    def __init__(self, id, **background_data):
        super().__init__(id, **background_data)
        self.image = Image.open("assets/backgrounds/" + self["image"])


class _Backgrounds(dict):
    BASE_PATH = 'assets/backgrounds/'

    def __init__(self):
        super().__init__()
        self._load_backgrounds()

    def _load_backgrounds(self):
        self.clear()
        with open(self.BASE_PATH+'stockbackgrounds.json') as stock_backgrounds_file:
            background_details = json.load(stock_backgrounds_file)
            added_backgrounds_path = self.BASE_PATH+'backgrounds.json'
            if os.path.isfile(added_backgrounds_path):
                with open(added_backgrounds_path) as uploaded_backgrounds_file:
                    try:
                        background_details.update(json.load(uploaded_backgrounds_file))
                    except ValueError:
                        util.logger.info("No none-stock backgrounds loaded/found.")
            for background_id, background in background_details.items():
                self[background_id] = Background(background_id, **background)


class Banner(Customization):
    """Class to hold details & methods for a profile banner
    This class is based off a legacy class from DueUtil V1
    and hence does not properly Customization
    """

    def __init__(self, id, **banner_data):
        self.price = banner_data["price"]
        self.donor = banner_data.get('donor', False)
        self.admin_only = banner_data.get('admin_only', False)
        self.mod_only = banner_data.get('mod_only', False)
        self.unlock_level = banner_data.get('unlock_level', 0)
        self.image = Image.open("assets/banners/" + banner_data["image"])
        self.image_name = banner_data["image"]
        self.icon = banner_data["icon"]
        self.description = banner_data["description"]
        super().__init__(id, **banner_data)

    def banner_restricted(self, player):
        member = discord.Member(user={"id": player.id})
        return ((not self.admin_only or self.admin_only
                 and permissions.has_permission(member, Permission.DUEUTIL_ADMIN))
                and (not self.mod_only or self.mod_only
                     and permissions.has_permission(member, Permission.DUEUTIL_MOD)))

    def can_use_banner(self, player):
        return (not self.donor or self.donor and player.donor) and self.banner_restricted(player)


class _Banners(dict):
    def __init__(self):
        super().__init__()
        self._load_banners()

    def _load_banners(self):
        self.clear()
        with open('assets/banners/banners.json') as banners_file:
            banners_details = json.load(banners_file)
            for banner_id, banner in banners_details.items():
                self[banner_id] = Banner(banner_id, **banner)


# Load customizations from json files
backgrounds = _Backgrounds()
banners = _Banners()
themes = _Themes()


def get_theme(theme_id: str) -> Theme:
    theme_id = theme_id.lower()
    if theme_id in themes:
        return themes[theme_id]


def get_background(background_id: str) -> Background:
    background_id = background_id.lower()
    if background_id in backgrounds:
        return backgrounds[background_id]


def get_banner(banner_id: str) -> Banner:
    banner_id = banner_id.lower()
    if banner_id in banners:
        return banners[banner_id]


def get_themes() -> Dict[str, Theme]:
    return themes
