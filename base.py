import logging
from functools import partial
from json import JSONDecodeError
from typing import Dict, Any, Tuple, Callable, Type, Optional, TypeVar

from requests import RequestException, Session, Response
from dataclass_factory import Factory


class ApiError(Exception):
    pass


class NotFoundError(ApiError):
    pass


T = TypeVar("T")


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

    def request(self, *, url: str, method: str,
                params: Dict = None, body: Any = None,
                result_class: Optional[Type[T]] = None) -> T:
        url = "%s/%s" % (self.base_url, url)
        self.__logger.debug("Get from: `%s`", url)
        try:
            response = self.session.request(method=method, url=url, params=params, json=self.factory.dump(body))
            if not response.ok:
                return self.handle_error(method, response)
            result = response.json()
            return self.factory.load(result, result_class)
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

    post = partial(request, method="POST")
    get = partial(request, method="GET", body=None)
    delete = partial(request, method="DELETE", body=None)
    patch = partial(request, method="PATCH")
    put = partial(request, method="PUT")


class RealClient(BaseClient):
    def get_challenge(self, username):
        return self.post("webservice.php", json={"operataion": "getchallenge", "username": username})
