import inspect
from typing import Callable

from discord import Message

from . import commands
from .game.configs import dueserverconfig
from .game.helpers.misc import DueMap
from itertools import chain


class MessageEvent(list):
    async def __call__(self, ctx: Message):
        for listener in self:
            if await listener(ctx):
                break

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)

    def append(self, listener_function: Callable[[Message], None]):
        old = (find_old(listener_function, self))
        if old == -1:
            super(MessageEvent, self).append(listener_function)
        else:
            self[old] = listener_function


class CommandEvent(dict):
    """Command event subscription.
    
    """

    def __init__(self):
        super().__init__()
        self.command_categories = DueMap()

    def command_list(self, **options):
        filter_func = options.get("filter", (lambda command: command))
        include_aliases = options.get("aliases", False)
        return list(chain.from_iterable((command.__name__,) + (command.aliases if include_aliases else ())
                                        for command in filter(filter_func, self.values()) if not command.is_hidden))

    def category_list(self):
        return [category for category in self.command_categories.keys()]

    def __str__(self):
        return "Command(%s)" % self.command_list()

    def __repr__(self):
        return "Command(%s)" % dict.__repr__(self)

    def __setitem__(self, key: str, command: Callable[..., None]):
        module_name = inspect.getmodule(command).__name__.rsplit('.', 1)[1]
        self.command_categories[module_name + "/" + command.__name__] = command
        command.category = module_name
        super(CommandEvent, self).__setitem__(key, command)

    def __delitem__(self, key: str):
        command = self[key]
        module_name = inspect.getmodule(command).__name__.rsplit('.', 1)[1]
        del self.command_categories[module_name + "/" + command.__name__]
        super(CommandEvent, self).__delitem__(key)

    async def __call__(self, ctx):
        # Commands can be triggered by using the command key or 
        # mentioning the bot
        if not ctx.content.startswith(dueserverconfig.server_cmd_key(ctx.server)):
            return
        args = commands.parse(ctx)
        command = get_command(args[1])
        if command is not None:
            await command(ctx, *args)

    def to_dict(self):
        command_data = dict()
        for category, commands_dict in self.command_categories.items():
            command_data[category] = dict()
            for command_name, command_func in commands_dict.items():
                command_data[category][command_name] = {"name": command_func.__name__,
                                                        "help": command_func.__doc__,
                                                        "hidden": command_func.is_hidden,
                                                        "permission": command_func.permission.name,
                                                        "aliases": command_func.aliases}
        return command_data


message_event = MessageEvent()
command_event = CommandEvent()


async def on_message_event(ctx):
    await message_event(ctx)
    await command_event(ctx)


def find_old(listener_function, listeners):
    return next((index for index, listener in enumerate(listeners)
                 if listener.__name__ == listener_function.__name__), -1)


def register_message_listener(listener_function):
    message_event.append(listener_function)


def remove_message_listener(listener_function):
    message_event.remove(listener_function)


def register_command(command_function):
    if commands.has_my_variant(command_function.__name__):
        command_function.__doc__ += "\nNote: [CMD_KEY]{0} is an alias for [CMD_KEY]my{0}".format(command_function.__name__)
    command_event[command_function.__name__] = command_function


def remove_command(command_function):
    del command_event[command_function.__name__]


def get_command(command_name):
    command_name = command_name.lower()
    if command_name in command_event:
        return command_event[command_name]
    for command in command_event.values():
        # Sad - need to search
        if command_name in command.aliases:
            return command
