import logging
from functools import partialmethod
from json import JSONDecodeError
from typing import Dict, Tuple, Callable, Type, Optional, TypeVar, Sequence

from dataclass_factory import Factory
from requests import RequestException, Session, Response


class ApiError(Exception):
    pass


class NotFoundError(ApiError):
    pass


RT = TypeVar("RT")
BT = TypeVar("BT")


class BaseClient:
    __logger = logging.getLogger(__name__)

    def __init__(self, base_url: str, session: Session):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.error_handlers: Dict[Tuple[str, int], Callable] = {
            ("", 404): self._handle_404
        }
        self.factory = self._init_factory()

    def _init_factory(self):
        return Factory()

    def _handle_404(self, repsonse: Response):
        raise NotFoundError

    def handle_error(self, method: str, response: Response):
        handler = self.error_handlers.get((method, response.status_code))
        if not handler:
            handler = self.error_handlers.get(("", response.status_code))
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

    def request(self, *, url: str, method: str,
                params: Optional[Dict] = None, body: Optional[BT] = None,
                body_class: Optional[Type[BT]] = None,
                result_class: Optional[Type[RT]] = None) -> RT:
        url = "%s/%s" % (self.base_url, url)
        self.__logger.debug("Sending requests to `%s`", url)
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=self._filter_params(params, (result_class, body_class)),
                json=self.factory.dump(body, body_class)
            )
            if not response.ok:
                return self.handle_error(method, response)
            result = response.json()
            if result_class:
                return self.factory.load(result, result_class)
            return result
        except RequestException as error:
            self.__logger.error(
                "RequestException when connecting with url: `%s`, error: `%s`",
                url, error
            )
            raise ApiError("RequestException") from error
        except JSONDecodeError as error:
            self.__logger.error(
                "Cannot decode response for url: `%s`, error: `%s`",
                url, error
            )
            raise ApiError("Cannot decode response") from error

    post = partialmethod(request, method="POST")
    get = partialmethod(request, method="GET", body=None)
    delete = partialmethod(request, method="DELETE", body=None)
    patch = partialmethod(request, method="PATCH")
    put = partialmethod(request, method="PUT")
