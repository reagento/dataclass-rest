__all__ = [
    "Unpack",
]

import sys
from typing import Any, TypeVar

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    T = TypeVar("T")
    Unpack = Any | T
