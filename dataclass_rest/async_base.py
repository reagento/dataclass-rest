import logging
from json import JSONDecodeError
from typing import Dict, Type, Optional

from aiohttp import ClientError, ClientResponse, ClientSession

from .base import BaseClient
from .common import RT, BT
from .errors import ApiError


class AsyncClient(BaseClient[ClientSession]):
    __logger = logging.getLogger(__name__)

    async def request(self, *, url: str, method: str,
                      params: Optional[Dict] = None, body: Optional[BT] = None,
                      body_class: Optional[Type[BT]] = None,
                      result_class: Optional[Type[RT]] = None) -> RT:
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
