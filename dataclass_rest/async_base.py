import logging
from functools import wraps
from inspect import getcallargs
from json import JSONDecodeError
from typing import Dict, Tuple, Callable, Type, Optional, Sequence, Awaitable, cast

from aiohttp import ClientSession, ClientError, ClientResponse
from dataclass_factory import Factory

from .common import RT, BT, F, create_args_class, get_method_classes, get_skipped
from .errors import ApiError, NotFoundError


class AsyncBaseClient:
    __logger = logging.getLogger(__name__)

    def __init__(self, base_url: str, session: ClientSession):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.error_handlers: Dict[Tuple[str, int], Callable] = {
            ("", 404): self._handle_404
        }
        self.factory = self._init_factory()
        self.params_factory = self._init_params_factory() or self.factory

    def _init_factory(self):
        return Factory()

    def _init_params_factory(self):
        return

    def _handle_404(self, response: ClientResponse):
        raise NotFoundError

    def handle_error(self, method: str, response: ClientResponse):
        handler = self.error_handlers.get((method, response.status))
        if not handler:
            handler = self.error_handlers.get(("", response.status))
        if not handler:
            raise ApiError(str(response))

    def _filter_params(self, params: Optional[Dict], skip: Sequence = None):
        if not params:
            return params
        return {
            k: v
            for k, v in params.items()
            if v != self or (skip and v in skip)
        }

    async def request(self, *, url: str, method: str,
                      params: Optional[Dict] = None, body: Optional[BT] = None,
                      body_class: Optional[Type[BT]] = None,
                      result_class: Optional[Type[RT]] = None) -> Awaitable[RT]:
        url = "%s/%s" % (self.base_url, url)
        self.__logger.debug("Sending requests to `%s` wtih %s", url, params)
        if body_class:
            body = self.factory.dump(body, body_class)
        try:
            response: ClientResponse = await self.session.request(
                method=method,
                url=url,
                params=self._filter_params(params, (result_class, body_class)),
                json=body
            )
            if not response.status:
                return self.handle_error(method, response)
            result = await response.json()
            if result_class:
                return self.factory.load(result, result_class)
            return result
        except ClientError as error:
            self.__logger.error(
                "ClientError when connecting with url: `%s`, error: `%s`",
                url, error
            )
            raise ApiError("ClientError") from error
        except JSONDecodeError as error:
            self.__logger.error(
                "Cannot decode response for url: `%s`, error: `%s`",
                url, error
            )
            raise ApiError("Cannot decode response") from error
