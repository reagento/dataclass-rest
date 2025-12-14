from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Protocol,
    runtime_checkable,
)

from .method_spec import MethodSpec


class FieldDestination(Enum):
    URL = "url"
    HEADER = "headers"
    BODY = "body"
    FILE = "files"
    QUERY = "query_params"
    EXTRA = "extras"
    RESPONSE = "response"
    UNDEFINED = "undefined"


@dataclass
class FieldIn:
    name: str
    type_hint: Any
    consumed_by: list["Transformer"] = field(default_factory=list)


@dataclass
class FieldOut:
    name: str | None
    dest: FieldDestination
    type_hint: Any


@runtime_checkable
class Transformer(Protocol):
    @abstractmethod
    def transform_fields(
        self,
        spec: MethodSpec,
        fields_in: Sequence[FieldIn],
    ) -> Sequence[FieldOut]:
        raise NotImplementedError
