import asyncio
import time
from functools import wraps

from . import permissions
from .game import players, emojis
from .game.configs import dueserverconfig
from . import events, util, commandtypes
from .permissions import Permission
from . import commandextras

extras = commandextras
IMAGE_REQUEST_COOLDOWN = 5

"""
DueUtils random command system.
"""


def command(**command_rules):
    """A command wrapper for command functions"""

    # TODO: Include sender, timesent, etc in details

    def check(user, called):
        return permissions.has_permission(user, called.permission)

    def is_spam_command(ctx, called, *args):
        if called.permission < Permission.SERVER_ADMIN:
            return (sum(isinstance(arg, players.Player) for arg in args)
                    < len(ctx.raw_mentions) or ctx.mention_everyone
                    or '@here' in ctx.content or '@everyone' in ctx.content)
        return False

    def get_command_details(ctx, **details):
        details["timestamp"] = ctx.timestamp
        details["author"] = players.find_player(ctx.author.id)
        details["server_id"] = ctx.server.id
        details["server_name"] = ctx.server.name
        details["server_name_clean"] = util.ultra_escape_string(ctx.server.name)
        details["author_name"] = ctx.author.name
        details["author_name_clean"] = util.ultra_escape_string(ctx.author.name)
        details["channel"] = ctx.channel
        details["channel_name"] = ctx.channel.name
        details["channel_name_clean"] = util.ultra_escape_string(ctx.channel.name)
        return details

    def wrap(command_func):

        @wraps(command_func)
        async def wrapped_command(ctx, prefix, _, args, **details):
            name = command_func.__name__
            # Player has admin perms
            is_admin = permissions.has_permission(ctx.author, Permission.SERVER_ADMIN)
            if not is_admin and dueserverconfig.mute_level(ctx.channel) == 1:
                return True
            # Blacklist/whitelist
            command_whitelist = dueserverconfig.whitelisted_commands(ctx.channel)
            if command_whitelist is not None and not is_admin and name not in command_whitelist:
                if "is_blacklist" not in command_whitelist:
                    await util.say(ctx.channel, (":anger: That command is not whitelisted in this channel!\n"
                                                 + " You can only use the following commands: ``"
                                                 + ', '.join(command_whitelist) + "``."))
                else:
                    await util.say(ctx.channel, ":anger: That command is blacklisted in this channel!")
                return True
            # Do they have the perms for the command
            if check(ctx.author, wrapped_command):
                # Check args
                args_pattern = command_rules.get('args_pattern', "")
                # Send a copy of args to avoid possible issues.
                command_args = await determine_args(args_pattern, args.copy(), wrapped_command, ctx)
                if command_args is False:
                    # React ?
                    if not has_my_variant(name) or len(ctx.raw_mentions) > 0:
                        # Could not be a mistype for a personal my command
                        await util.get_client(ctx.server.id).add_reaction(ctx, emojis.QUESTION_REACT)
                    else:
                        # May have meant to call a personal command
                        personal_command_name = "my" + name
                        await events.command_event[personal_command_name](ctx, prefix, _, args, **details)
                elif not is_spam_command(ctx, wrapped_command, *args):
                    # Run command
                    details["cmd_key"] = prefix
                    details["command_name"] = name
                    await command_func(ctx, *command_args, **get_command_details(ctx, **details))
                else:
                    raise util.DueUtilException(ctx.channel, "Please don't include spam mentions in commands.")
            else:
                # React X
                await util.get_client(ctx.server.id).add_reaction(ctx, emojis.CROSS_REACT)
            return True

        wrapped_command.is_hidden = command_rules.get('hidden', False)
        wrapped_command.permission = command_rules.get('permission', Permission.PLAYER)
        wrapped_command.aliases = tuple(command_rules.get('aliases', ()))
        # Add myX to X aliases
        if command_func.__name__.startswith("my"):
            wrapped_command.aliases += command_func.__name__[2:],

        events.register_command(wrapped_command)

        return wrapped_command

    return wrap


def has_my_variant(command_name):
    """
    Returns if a command has a personal mycommand variant
    e.g. !info and !myinfo
    """
    return "my" + command_name.lower() in events.command_event


def replace_aliases(command_list):
    for index, given_command_name in enumerate(command_list):
        command_func = events.get_command(given_command_name)
        if command_func is None:
            continue
        command_name = command_func.__name__
        if command_name != given_command_name:
            # Fix aliases in whitelist
            command_list[index] = command_name
        if has_my_variant(command_name):
            command_list.append("my" + command_name)  # To avoid confuzzing
    return command_list


def imagecommand():
    def wrap(command_func):
        @ratelimit(slow_command=True, cooldown=IMAGE_REQUEST_COOLDOWN, error=":cold_sweat: Please don't break me!")
        @wraps(command_func)
        async def wrapped_command(ctx, *args, **kwargs):
            await util.get_client(ctx).send_typing(ctx.channel)
            await asyncio.ensure_future(command_func(ctx, *args, **kwargs))

        return wrapped_command

    return wrap


def ratelimit(**command_info):
    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, *args, **details):
            player = details["author"]
            command_name = details["command_name"]
            if command_info.get('save', False):
                command_name += "_saved_cooldown"
            now = int(time.time())
            time_since_last_used = now - player.command_rate_limits.get(command_name, 0)
            if time_since_last_used < command_info["cooldown"]:
                error = command_info["error"]
                if "[COOLDOWN]" in error:
                    time_to_wait = command_info["cooldown"] - time_since_last_used
                    error = error.replace("[COOLDOWN]", util.display_time(time_to_wait))
                await util.say(ctx.channel, error)
                return
            else:
                player.command_rate_limits[command_name] = now
            await command_func(ctx, *args, **details)

        return wrapped_command

    return wrap


def require_cnf(warning):
    # Checks the user confirms the command.
    # Only from commands with no args.
    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, cnf="", **details):
            if cnf.lower() != "cnf":
                await util.say(ctx.channel, ("Are you sure?! %s\n"
                                             + "Do ``%s%s cnf`` if you're sure!")
                               % (warning, details["cmd_key"], command_func.__name__))
                return
            await command_func(ctx, **details)

        return wrapped_command

    return wrap


def parse(command_message):
    """A basic command parser with support for escape strings.
    I don't think one like this exists that is not in a package
    that adds a lot more stuff I don't want.
    
    This is meant to be like a shell command lite style.
    
    Supports strings in double quotes & escape strings
    (e.g. \" for a quote character)
    
    The limitations of this parser are 'fixed' in determine_args
    that can guess where quotes should be most times.
    """

    key = dueserverconfig.server_cmd_key(command_message.server)
    command_string = command_message.content.replace(key, '', 1)
    user_mentions = command_message.raw_mentions
    escaped = False
    is_string = False
    args = []
    current_arg = ''

    def replace_mentions():
        nonlocal user_mentions, current_arg
        for mention in user_mentions:  # Replace mentions
            if mention in current_arg and len(current_arg) - len(mention) < 6:
                current_arg = mention
                del user_mentions[user_mentions.index(mention)]

    def add_arg():
        nonlocal current_arg, args
        if len(current_arg) > 0:
            replace_mentions()
            args = args + [current_arg]
            current_arg = ""

    for char_pos in range(0, len(command_string) + 1):
        current_char = command_string[char_pos] if char_pos < len(command_string) else ' '
        if char_pos < len(command_string) and (not current_char.isspace() or is_string):
            if not escaped:
                if current_char == '\\' and not (current_char.isspace() or current_char.isalpha()):
                    escaped = True
                    continue
                elif current_char == '"':
                    is_string = not is_string
                    add_arg()
                    continue
            else:
                escaped = False
            current_arg += command_string[char_pos]
        else:
            add_arg()

    if is_string:
        raise util.DueUtilException(command_message.channel, "Unclosed string in command!")

    if len(args) > 0:
        return key, args[0], args[1:]
    else:
        return key, "", []


async def determine_args(pattern, args, called, ctx):
    """
    
    Takes the args coming from parse()
    (all strings) and using the pattern defined with the 
    command attempts to derermine the args turple with the
    correct types (not just strings).
    
    Types: S(tring), I(nteger), C(ount), R(eal), P(layer), M(ixed) & B(oolean)
    Mods: * (zero or more) & ? (zero or one)
    Valid: SIR?
    Valid SI*PB?R?I?C?
    Invalid: SI?S
    
    This allows the commands to not need to parse their args
    unless they're doing something strange.
    
    TODO: This method probably can be improved and simplified
    
    Returns False if the args could not be determined or
    a turple of args if they could.
    
    WARNING: Python will resolve an empty turple to False so
    use 'is False' for checks insted of 'not determine_args(....)'
    
    """

    original_pattern = pattern

    # Internal helpers.
    def remove_optional(args_pattern):
        pattern_pos = len(args_pattern) - 1
        while pattern_pos >= 0:
            if len(args_pattern.replace('?', '')) == len(args):
                break
            elif pattern_pos == 0:
                return False
            if args_pattern[pattern_pos] == '?':
                args_pattern = args_pattern[:pattern_pos - 1]
                pattern_pos = len(args_pattern) - 1
                continue
            pattern_pos -= 1
        return args_pattern.replace('?', '')

    def could_be_string(args_pattern):
        if args_pattern[0] in commandtypes.STRING_TYPES:
            if len(args_pattern) > 1:
                pattern_pos = len(args_pattern) - 1
                while pattern_pos > 0:
                    if args_pattern[pattern_pos] == '?':
                        pattern_pos -= 2
                        continue
                    return False
            return args_pattern in commandtypes.STRING_TYPES or len(args_pattern) > 1
        return False

    def attempt_args_as_string(crappy_args, args_pattern):
        # A last ditch effort to get some use out of the shit known as input.
        if len(crappy_args) > 0 and could_be_string(args_pattern):
            # Only a pattern that can just be a string is valid
            return ' '.join(map(str, crappy_args)),
        return False

    def valid_args_len(test_args, args_pattern):
        # Length - zero or more types (as they are not needed)
        pattern_type_count = len(args_pattern) - args_pattern.count('*') * 2
        if '*' in args_pattern:
            return len(test_args) >= pattern_type_count
        return len(test_args) == pattern_type_count

    # Initial pattern checks
    guessing_arguments = False
    if pattern is None and len(args) > 0:
        return False
    elif pattern is None and len(args) == 0:
        return args
    if len(pattern) == 0:
        return args
    if '*' not in pattern:
        pattern_optional_removed = remove_optional(pattern)
        if pattern_optional_removed is False or len(args) > len(pattern_optional_removed):
            if could_be_string(pattern):
                # If the command is wrong by all other tests and it could be a string
                # merge the arguments to a single string.
                if len(args) > 0:
                    return ' '.join(args),
                return False
            # Guessing args: Trying to figure out if the user has forgot quotes.
            # With no context on the command it's fiddly
            guessing_arguments = True
        if not guessing_arguments:
            pattern = pattern_optional_removed
        else:
            pattern = pattern.replace('?', '')

    # Checking the command args match the given pattern.
    pos = 0
    args_index = 0
    current_rule = ''
    checks_satisfied = 0
    while pos < len(pattern) and args_index < len(args):
        pos_change = pattern[pos] != '*'
        if pos_change:
            current_rule = pattern[pos]
        if pos + 1 < len(pattern) and pattern[pos + 1] == '*':
            # We don't move in were we are in the pattern
            # if the rule is a Kleene star
            pos += 1
            pos_change = False
        # Get the value as the type it should be (if possible). Will return False or None if it fails.
        value = commandtypes.parse_type(current_rule, args[args_index], called=called, ctx=ctx)
        if (value is False and current_rule != 'B') or value is None:
            # We've got a incorrect value and are not expecting multiple (*)
            if pattern[pos] != '*':
                # We've been unable to parse it.
                # One last try.
                return attempt_args_as_string(args, original_pattern)
            else:
                # Must be the end of the repeated set of values (*)
                if pos + 1 < len(pattern):
                    args_index -= 1
                    pos_change = True
                else:
                    # Okay I'm super cereal - Giving up after this
                    return attempt_args_as_string(args, original_pattern)
        else:
            # Normal - All is good
            args[args_index] = value
            checks_satisfied += 1
        args_index += 1
        if pos_change:
            pos += 1

    # Final checks
    if (checks_satisfied == len(args) and not guessing_arguments
            and valid_args_len(args, pattern)):
        return args
    elif guessing_arguments:
        """
        If they've forgot quotes for the last sting
        so !command arg0 arg1 arg2 "A String here"
        and they've done
        !command arg0 arg1 arg2 A String here
        """
        if len(args) > len(pattern):
            last_string = -1
            # Find the last type that could be a string in the pattern.
            # Use a simple loop as the regex (re) kinda sucks for this
            for string_type in commandtypes.STRING_TYPES:
                last_string_type = pattern.rfind(string_type)
                if last_string_type > last_string:
                    last_string = last_string_type
            if last_string != -1:
                if could_be_string(pattern[last_string:]):
                    new_args = tuple(args[:last_string]) + (' '.join(args[last_string:]),)
                    if checks_satisfied == len(new_args) and valid_args_len(new_args, pattern):
                        return new_args
    return False
