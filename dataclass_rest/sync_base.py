import logging
from json import JSONDecodeError
from typing import Dict, Type, Optional

from requests import RequestException, Session

from .base import BaseClient, File
from .common import BT, RT
from .errors import ApiError
from .jsonrpc import JsonRpcMixin


class Client(BaseClient[Session]):
    __logger = logging.getLogger(__name__)

    def request(self, *, url: str, method: str,
                params: Optional[Dict] = None, body: Optional[BT] = None,
                body_class: Optional[Type[BT]] = None, file: File = None,
                result_class: Optional[Type[RT]] = None, base_url: Optional[str] = None) -> RT:
        url, body, upload_file = self._prepare_request(
            url=url,
            method=method,
            params=params,
            body=body,
            body_class=body_class,
            file=file,
            result_class=result_class,
            base_url=base_url
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=self._filter_params(params, (result_class, body_class)),
                json=body,
                data=upload_file,
            )
            if not response.ok:
                return self.handle_error(method, response.status_code, response)
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


class JsonRpcClient(Client, JsonRpcMixin):
    pass


__all__ = [
    "Client"
]
