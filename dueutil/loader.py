import importlib
import pkgutil
import sys

from . import events, util, dbconn

MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')
GAME = 'dueutil.game'
COMMANDS = 'dueutil.botcommands'
BOT_PACKAGES = (COMMANDS, GAME)
loaded_modules = []


def loader(action, packages=BOT_PACKAGES):
    if isinstance(packages, str):
        packages = (packages,)
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
    dbconn.drop_and_insert("commands", events.command_event.to_dict())
    if COMMANDS in packages:
        util.logger.info('Bot extensions loaded with %d commands\n%s', len(events.command_event),
                         ', '.join(events.command_event.command_list()))


def load_module(module_name):
    """
  Import modules.
  """

    importlib.import_module(module_name)
    loaded_modules.append(module_name)


def reload_module(module_name):
    """
  Import modules.
  """

    if module_name in loaded_modules:
        importlib.reload(sys.modules[module_name])


def module_refresh(module_name):
    """
  Eat fresh (TM)
  """

    if module_name not in loaded_modules:
        importlib.import_module(module_name)
        loaded_modules.append(module_name)


def load_modules(packages=BOT_PACKAGES):
    loader(load_module, packages=packages)


def reload_modules(packages=BOT_PACKAGES):
    # loaded_modules = []
    loader(reload_module, packages=packages)


def refresh_modules(packages=BOT_PACKAGES):
    loader(module_refresh, packages=packages)


def get_loaded_modules():
    loaded = "Loaded:\n"
    for module_name in loaded_modules:
        loaded += "``" + module_name + "``\n"
    return loaded
