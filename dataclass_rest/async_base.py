import logging
from json import JSONDecodeError
from typing import Dict, Type, Optional

from aiohttp import ClientError, ClientResponse, ClientSession

from .base import BaseClient, File
from .common import RT, BT
from .errors import ApiError


class AsyncClient(BaseClient[ClientSession]):
    __logger = logging.getLogger(__name__)

    async def request(self, *, url: str, method: str,
                      params: Optional[Dict] = None, body: Optional[BT] = None,
                      file: File = None,
                      body_class: Optional[Type[BT]] = None,
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
            response: ClientResponse = await self.session.request(
                method=method,
                url=url,
                params=self._filter_params(params, (result_class, body_class)),
                json=body,
                data=upload_file
            )
            if (response.status // 100) != 2:
                return self.handle_error(method, response.status, response)
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


__all__ = [
    "AsyncClient"
]
