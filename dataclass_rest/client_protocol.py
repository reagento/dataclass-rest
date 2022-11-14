from typing import Protocol, Any, Optional, Callable, Type, runtime_checkable

from dataclass_factory import Factory, Schema

from .http_request import HttpRequest


@runtime_checkable
class ClientMethodProtocol(Protocol):
    def get_query_params_schema(self) -> Optional[Schema]:
        raise NotImplementedError

    def get_query_params_type(self) -> Type:
        raise NotImplementedError


class ClientProtocol(Protocol):
    request_body_factory: Factory
    request_args_factory: Factory
    response_body_factory: Factory
    method_class: Optional[Callable]

    def do_request(
            self, request: HttpRequest,
    ) -> Any:
        raise NotImplementedError
