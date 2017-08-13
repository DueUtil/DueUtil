import inspect
from inspect import Parameter
from . import commandtypes, util
from functools import wraps
import itertools


def dict_command(**spec):

    def wrap(command_func):

        expected = expand_spec(spec.get("expected", {}))
        optional = expand_spec(spec.get("optional", {}))

        @wraps(command_func)
        async def wrapped_command(ctx, *args, **details):
            # Find the last positional. That is where the dict_args will be passed.
            args_spec = inspect.signature(command_func)
            params = list(args_spec.parameters.values())
            args_dict_param = next((param for param in reversed(params)
                                    if param.kind is Parameter.POSITIONAL_OR_KEYWORD))

            # Get all args after and including the position of the arg for the dict_args
            # Those will be processed into a dict.
            arg_dict_index = params.index(args_dict_param) - 1  # -1 to ignore ctx arg
            dict_args = determine_dict_args(list(args[arg_dict_index:]), wrapped_command, ctx,
                                            expected=expected, optional=optional)

            if dict_args is False:
                # Invalid
                await util.say(ctx.channel, "<:TardQuester:345595519671992320> Trash args kys")
            else:
                # Run command.
                kwargs = details
                kwargs[args_dict_param.name] = dict_args
                await command_func(ctx, *args[:arg_dict_index], **kwargs)

        return wrapped_command

    return wrap


def determine_dict_args(args, called, ctx, **spec):

    """
    A simple function to convert an array of args into
    a dict with correctly parsed types (or false)
    Using the same types a determine_args

    a spec is {"param": "I", "param2": "S"}
    spec can also be {"param/altname": "I"}
    That would be a called param and a string called param2.

    This function would use that spec with args like ('parm2', 'apple', 'param', '12, 'dsd')
    to produce {'parm2': 'apple', 'param': 12}
    """

    expected = spec.get("expected", {})
    optional = spec.get("optional", {})
    ignore_extra = spec.get("ignore_extra", True)

    if len(args) % 2 != 0:
        args.pop()
    # The type definitions for all args it could get
    args_spec = dict(expected, **optional)
    # Ugly af line of code to do a simple task.
    # Convert args list (a,b,c,d) into {a:b,c:d} dict
    dict_args = dict(itertools.zip_longest(*[iter(args)] * 2, fillvalue=""))
    expected_seen = 0

    for arg_name, arg_value in dict_args.copy().items():
        arg_key = arg_name.lower()
        # Ignore extra args
        if arg_key not in args_spec:
            if ignore_extra:
                del dict_args[arg_name]
            continue
        arg_expected = arg_key in expected

        if arg_expected:
            expected_seen += 1

        # Parse the arg into the value it should be
        arg_type = args_spec[arg_key]
        value = commandtypes.parse_type(arg_type, arg_value, called=called, ctx=ctx)
        # Handle it being wrong.
        arg_invalid = value is False and arg_type != "B"
        if arg_invalid and expected:
            return False  # Required/expected arg is wrong
        elif arg_invalid and not expected:  # Optional
            del dict_args[arg_name]
            continue  # Ignore incorrect optional

        # Update dict args
        if arg_key != arg_name:
            del dict_args[arg_name]
        dict_args[arg_key] = value

    # Not all expected args seen/
    if expected_seen != len(expected):
        return False
    return dict_args


def expand_spec(spec_dict):
    for arg_name, arg_type in spec_dict.copy().items():
        if "/" in arg_name:
            del spec_dict[arg_name]
            arg_names = arg_name.split("/")
            spec_dict.update(dict.fromkeys(arg_names, arg_type))
    return spec_dict
