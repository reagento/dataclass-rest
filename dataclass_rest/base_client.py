from typing import Protocol, Any, Optional, Callable

from dataclass_factory import Factory

from .http_request import HttpRequest


class ClientProtocol(Protocol):
    request_body_factory: Factory
    request_args_factory: Factory
    response_body_factory: Factory
    method_class: Optional[Callable]

    def do_request(
            self, request: HttpRequest,
    ) -> Any:
        raise NotImplementedError


class BaseClient(ClientProtocol):
    method_class: Optional[Callable] = None

    def __init__(self):
        self.request_body_factory = self._init_request_body_factory()
        self.request_args_factory = self._init_request_args_factory()
        self.response_body_factory = self._init_response_body_factory()

    def _init_request_body_factory(self) -> Factory:
        return Factory()

    def _init_request_args_factory(self) -> Factory:
        return self.request_body_factory

    def _init_response_body_factory(self) -> Factory:
        return self.request_body_factory
