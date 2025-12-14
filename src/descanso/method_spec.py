from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, ParamSpec, TypeVar

_MethodResultT = TypeVar("_MethodResultT")
_MethodParamSpec = ParamSpec("_MethodParamSpec")


@dataclass
class MethodSpec(Generic[_MethodParamSpec, _MethodResultT]):
    name: str
    doc: str | None
    result_type: Any
    func: Callable[_MethodParamSpec, _MethodResultT]
