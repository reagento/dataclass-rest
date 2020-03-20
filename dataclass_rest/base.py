import logging
from typing import Dict, Type, Optional, Tuple, Callable, Sequence, Any, Generic

from dataclass_factory import Factory

from .common import BT, RT, SessionType
from .errors import ApiError, NotFoundError


class BaseClient(Generic[SessionType]):
    __logger = logging.getLogger(__name__)

    def __init__(self, base_url: str, session: SessionType):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.error_handlers: Dict[Tuple[str, int], Callable] = {
            ("", 404): self._handle_404
        }
        self.factory = self._init_factory()
        self.args_factory = self._init_args_factory() or self.factory

    def _init_factory(self):
        return Factory()

    def add_handler(self, handler: Callable, status_code: int, method: str = ""):
        self.error_handlers[(method, status_code)] = handler

    def _init_args_factory(self):
        return

    def _handle_404(self, response: Any):
        raise NotFoundError

    def handle_error(self, method: str, status_code: int, response: Any):
        handler = self.error_handlers.get((method, status_code))
        if not handler:
            handler = self.error_handlers.get(("", status_code))
        if not handler:
            raise ApiError(str(response))  # TODO: save status_code in error

    def _filter_params(self, params: Optional[Dict], skip: Sequence = None):
        if not params:
            return params
        return {
            k: v
            for k, v in params.items()
            if v != self or (skip and v in skip)
        }

    def request(self, *, url: str, method: str,
                params: Optional[Dict] = None, body: Optional[BT] = None,
                body_class: Optional[Type[BT]] = None,
                result_class: Optional[Type[RT]] = None):
        raise NotImplementedError
