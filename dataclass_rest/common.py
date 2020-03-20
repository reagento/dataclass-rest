import string
import sys
from inspect import getfullargspec
from typing import TypeVar, Callable, Any, Sequence, get_type_hints

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

RT = TypeVar("RT")
BT = TypeVar("BT")
F = TypeVar('F', bound=Callable[..., Any])
SessionType = TypeVar("SessionType")


def create_args_class(func: Callable, skipped: Sequence[str]):
    s = getfullargspec(func)
    fields = {}
    self_processed = False
    for x in s.args:
        if not self_processed:
            self_processed = True
            continue
        if x in skipped:
            continue
        fields[x] = s.annotations.get(x, Any)
    return TypedDict(f"{func.__name__}_Args", fields)  # type: ignore


def get_method_classes(func: Callable, body_name: str):
    """
    gets result class and body class from method typehints
    :param func: function to decorate
    :param body_name: name of body parameter
    :return: Result class, body class
    """
    hints = get_type_hints(func)
    result_class = hints.get("return")
    body_class = hints.get(body_name)
    return result_class, body_class


def get_skipped(url_format: str, body_name: str):
    """
    gets skipped args
    :param url_format: API URL format string
    :param body_name:  name of body parameter
    :return: List of skipped args
    """
    parsed_format = string.Formatter().parse(url_format)
    skipped = [x[1] for x in parsed_format]
    skipped.append(body_name)
    return skipped
