import inspect
from inspect import Parameter
from . import commandtypes, util
from functools import wraps
import itertools


def dict_command(min_expect, optional={}):

    def wrap(command_func):
        @wraps(command_func)
        async def wrapped_command(ctx, *args, **details):
            args_spec = inspect.signature(command_func)
            params = list(args_spec.parameters.values())
            args_dict_param = next((param for param in reversed(params)
                                    if param.kind is Parameter.POSITIONAL_OR_KEYWORD))

            arg_dict_index = params.index(args_dict_param) - 1  # -1 to ignore ctx arg
            dict_args = determine_dict_args(list(args[arg_dict_index:]), wrapped_command, min_expect, optional)
            if dict_args is False:
                await util.say(ctx.channel, "<:TardQuester:345595519671992320> Trash args kys")
            else:
                kwargs = details
                kwargs[args_dict_param.name] = dict_args
                await command_func(ctx, *args[:arg_dict_index], **kwargs)

        return wrapped_command

    return wrap


def determine_dict_args(args, called, min_expect, optional={}):

    if len(args) % 2 != 0:
        args.pop()
    print(args)
    # The type definitions for all args it could get
    args_spec = dict(min_expect, **optional)
    # Ugly af line of code to do a simple task.
    # Convert args list (a,b,c,d) into {a:b,c:d} dict
    dict_args = dict(itertools.zip_longest(*[iter(args)] * 2, fillvalue=""))
    expected_seen = 0

    for key, value in dict_args.copy().items():
        arg_key = key.lower()
        # Ignore extra args
        if arg_key not in args_spec:
            continue
        expected = arg_key in min_expect

        if expected:
            expected_seen += 1

        arg_value = commandtypes.represents_type(args_spec[arg_key], value, called)
        if arg_value is False and expected:
            return False  # Required/expected arg is wrong
        elif arg_value is False and not expected:  # Optional
            del dict_args[key]
            continue  # Ignore incorrect optional

        if arg_key != key:
            del dict_args[key]
        dict_args[arg_key] = arg_value

    # Not all expected args seen/
    if expected_seen != len(min_expect):
        return False
    return dict_args
