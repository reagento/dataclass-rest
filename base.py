import logging
from functools import partialmethod, wraps
from inspect import getcallargs, getfullargspec
from json import JSONDecodeError
from typing import Dict, Tuple, Callable, Type, Optional, TypeVar, Sequence, get_type_hints, TypedDict, Any

from dataclass_factory import Factory
from requests import RequestException, Session, Response


class ApiError(Exception):
    pass


class NotFoundError(ApiError):
    pass


RT = TypeVar("RT")
BT = TypeVar("BT")


def get(url_format: str, *, body_name: str = "body"):
    def dec(func):
        args_class = create_args_class(func, body_name)
        hints = get_type_hints(func)
        result_class = hints.get("return")
        body_class = hints.get(body_name)

        @wraps(func)
        def inner(self, *args, **kwargs):
            params = getcallargs(func, self, *args, **kwargs)
            params = self.factory.dump(params, args_class)
            url = url_format.format(**params)
            return self.get(url=url, params=params, body_class=body_class, result_class=result_class)

        return inner

    return dec


def create_args_class(func: Callable, body_name: str):
    s = getfullargspec(func)
    fields = {}
    self_processed = False
    for x in s.args:
        if not self_processed:
            self_processed = True
            continue
        if x == body_name:
            continue
        fields[x] = s.annotations.get(x, Any)
    return TypedDict(f"{func.__name__}_Args", fields)


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
        if body_class:
            body = self.factory.dump(body, body_class)
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=self._filter_params(params, (result_class, body_class)),
                json=body
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
