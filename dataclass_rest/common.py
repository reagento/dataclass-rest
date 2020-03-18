import sys
from inspect import getfullargspec
from typing import TypeVar, Callable, Any, Sequence

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

RT = TypeVar("RT")
BT = TypeVar("BT")
F = TypeVar('F', bound=Callable[..., Any])


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
