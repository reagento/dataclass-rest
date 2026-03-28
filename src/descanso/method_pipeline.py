from dataclasses import dataclass
from typing import ParamSpec, TypeVar

from .fields import FieldIn, FieldOut
from .method_spec import MethodSpec
from .request import RequestTransformer
from .response import ResponseTransformer

_MethodResultT = TypeVar("_MethodResultT")
_MethodParamSpec = ParamSpec("_MethodParamSpec")


@dataclass
class MethodPipeline(MethodSpec[_MethodParamSpec, _MethodResultT]):
    fields_in: list[FieldIn]
    fields_out: list[FieldOut]
    request_transformers: list[RequestTransformer]
    response_transformers: list[ResponseTransformer]
