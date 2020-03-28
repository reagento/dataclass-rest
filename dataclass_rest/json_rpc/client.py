from json import JSONDecodeError
from typing import Optional, Type, Dict, Tuple, Any, BinaryIO, Generic
from dataclasses import dataclass

from requests import RequestException, Session

from ..base import BaseClient, File
from ..common import BT, RT, PT, new_id
from ..errors import ApiError


@dataclass
class Error:
    code: int
    message: str
    data: str

@dataclass
class JSONRPCError:
    jsonrpc: str
    error: Error
    id: int

@dataclass
class JSONQuery(Generic[PT]):
    jsonrpc: Optional[str] = "2.0"
    method: Optional[str] = None
    params: Optional[PT] = None
    id: Optional[int] = None


@dataclass
class JSONRPCResult(Generic[PT]):
    jsonrpc: str
    result: RT
    id: int


class JSONRPCClient(BaseClient[Session]):
    def _init_json_query(self):
        return JSONQuery

    def _prepare_request(self, method: str,
                         url: Optional[str] = None,
                         params: Optional[Dict] = None,
                         body: Optional[BT] = None,
                         body_class: Optional[Type[BT]] = None,
                         file: File = None,
                         result_class: Optional[Type[RT]] = None,
                         base_url: Optional[str] = None) -> Tuple[str, Any, Optional[Dict[str, BinaryIO]]]:
        return self.factory.dump(body, type(body))

    def create_request(self, json_rpc_method: str, params):
        request = self._init_json_query()
        return request("2.0", method=json_rpc_method, params=params, id=new_id())

    def request(self, *, url: Optional[str] = None, method: str,
                params: Optional[Dict] = None, body: Optional[BT] = None, file: File = None,
                body_class: Optional[Type[BT]] = None,
                result_class: Optional[Type[RT]] = None, base_url: Optional[str] = None):
        body = self._prepare_request(
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
                url=self.base_url,
                json=body,
            )
            if not response.ok:
                return self.handle_error(method, response.status_code, response)
            result = response.json()
            if result_class:
                try:
                    return self.factory.load(result, result_class)
                except TypeError:
                    return self.factory.load(result, JSONRPCError)
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
