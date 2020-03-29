from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Type
from uuid import uuid4

from dataclass_factory import Factory
from typing_extensions import Literal

PT = TypeVar("PT")
RT = TypeVar("RT")


@dataclass
class JsonRpcRequest(Generic[PT]):
    id: int
    params: PT
    method: str
    jsonrpc: Literal["2.0"] = "2.0"


@dataclass
class JsonRpcResponse(Generic[RT]):
    id: int
    result: RT
    jsonrpc: Literal["2.0"] = "2.0"


@dataclass
class JsonRpcError:
    code: int
    message: str
    data: str


@dataclass
class JsonRpcErrorResponse:
    id: int
    error: JsonRpcError
    jsonrpc: Literal["2.0"] = "2.0"


class JsonRPCException(Exception):
    pass


class JsonRpcErrorException(JsonRPCException):
    def __init__(self, error: JsonRpcError):
        self.error = error


class JsonRpcMixin():
    factory: Factory

    def request_id(self) -> int:
        return uuid4().int

    def create_request(self, method: str, params: Any) -> JsonRpcRequest:
        return JsonRpcRequest(id=self.request_id(), method=method, params=params)

    def process_response(self, request, resp, result_class: Type[RT]) -> RT:
        if resp.get("error"):
            raise JsonRpcErrorException(self.factory.load(resp, JsonRpcErrorResponse).error)
        result: JsonRpcResponse[RT] = self.factory.load(resp, JsonRpcResponse[result_class])
        if result.id != request.id:
            raise JsonRPCException("invalid id")
        return result.result
