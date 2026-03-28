from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import (
    IO,
    Any,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

from kiss_headers import Headers

from .fields import FieldIn, FieldOut, Transformer
from .method_spec import MethodSpec

T = TypeVar("T")
KeyValue: TypeAlias = tuple[str, T]
KeyValueList: TypeAlias = list[KeyValue[T]]


@dataclass
class FileData:
    contents: str | IO | None | bytes
    content_type: str | None = None
    filename: str | None = None


@dataclass
class HttpRequest:
    body: Any = None
    files: KeyValueList[FileData] = field(default_factory=list)
    query_params: KeyValueList[Any] = field(default_factory=list)
    headers: Headers = field(default_factory=Headers)
    extras: KeyValueList[Any] = field(default_factory=list)
    url: str = ""
    method: str = "GET"


@runtime_checkable
class RequestTransformer(Transformer, Protocol):
    @abstractmethod
    def transform_fields(
        self,
        spec: MethodSpec,
        fields_in: Sequence[FieldIn],
    ) -> Sequence[FieldOut]:
        raise NotImplementedError

    @abstractmethod
    def transform_request(
        self,
        spec: MethodSpec,
        request: HttpRequest,
        fields_in: Sequence[FieldIn],
        fields_out: Sequence[FieldOut],
        data: dict[str, Any],
    ) -> HttpRequest:
        raise NotImplementedError


class BaseRequestTransformer(RequestTransformer):
    def transform_fields(
        self,
        spec: MethodSpec,
        fields_in: Sequence[FieldIn],
    ) -> Sequence[FieldOut]:
        return []

    def transform_request(
        self,
        spec: MethodSpec,
        request: HttpRequest,
        fields_in: Sequence[FieldIn],
        fields_out: Sequence[FieldOut],
        data: dict[str, Any],
    ) -> HttpRequest:
        return request

    def __or__(self, other: RequestTransformer) -> "PipeRequestTransformer":
        return PipeRequestTransformer(self, other)

    def __ror__(self, other: RequestTransformer) -> "PipeRequestTransformer":
        return PipeRequestTransformer(other, self)


class PipeRequestTransformer(BaseRequestTransformer):
    def __init__(self, *others: RequestTransformer) -> None:
        self.others = others

    def transform_fields(
        self,
        spec: MethodSpec,
        fields_in: Sequence[FieldIn],
    ) -> Sequence[FieldOut]:
        res: list[FieldOut] = []
        for other in self.others:
            res.extend(other.transform_fields(spec, fields_in))
        return res

    def transform_request(
        self,
        spec: MethodSpec,
        request: HttpRequest,
        fields_in: Sequence[FieldIn],
        fields_out: Sequence[FieldOut],
        data: dict[str, Any],
    ) -> HttpRequest:
        for other in self.others:
            request = other.transform_request(
                spec,
                request,
                fields_in,
                fields_out,
                data,
            )
        return request
