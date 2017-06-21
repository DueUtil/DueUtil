import importlib
import pkgutil
from importlib import util as importutil
import os
import sys
from botstuff import events, util
import os

MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')
BOT_PACKAGES = ('duecommands', 'fun')
loaded_modules = []


def loader(action, packages=BOT_PACKAGES):
    """
    Inefficient - but allows me to load all the modules (needed to register commands & load game stuff)
    and produce a pretty list
    """

    # subpackages = []
    for package_name in packages:
        package = importlib.import_module(package_name)
        for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                              prefix=package.__name__ + '.'):
            if not ispkg:
                action(modname)
                # else:
                # subpackages.append(modname)
                # if len(subpackages) > 0:
                # print(subpackages)
                # loader(action,packages=subpackages)
    # if packages == BOT_PACKAGES:
    util.logger.info('Bot extensions loaded with %d commands\n%s', len(events.command_event),
                     ', '.join(events.command_event.command_list()))


def load_module(module):
    """
  Import modules.
  """

    importlib.import_module(module)
    loaded_modules.append(module)


def reload_module(module):
    """
  Import modules.
  """

    if module in loaded_modules:
        importlib.reload(sys.modules[module])


def module_refresh(module):
    """
  Eat fresh (TM)
  """

    if module not in loaded_modules:
        importlib.import_module(module)
        loaded_modules.append(module)


def load_modules():
    loader(load_module)


def reload_modules():
    loaded_modules = []
    loader(reload_module)


def refresh_modules():
    loader(module_refresh)


def get_loaded_modules():
    loaded = "Loaded:\n"
    for module in loaded_modules:
        loaded += "``" + module + "``\n"
    return loaded
