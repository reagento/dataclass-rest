from typing import Protocol, Any

from dataclass_factory import Factory


class BaseClient(Protocol):
    request_body_factory: Factory
    request_args_factory: Factory
    response_body_factory: Factory

    def request(
            self,
            url: str,
            method: str,
            body: Any,
            params: Any,
    ) -> Any:
        raise NotImplementedError
