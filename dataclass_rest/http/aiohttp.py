import urllib.parse
from typing import Any, Optional

from aiohttp.client import ClientResponse, ClientSession

from ..base_client import BaseClient
from ..boundmethod import AsyncMethod
from ..http_request import HttpRequest


class AiohttpMethod(AsyncMethod):
    async def _release_raw_response(self, response: ClientResponse) -> None:
        await response.release()

    async def _response_body(self, response: ClientResponse) -> Any:
        return await response.json()

    async def _response_ok(self, response: ClientResponse) -> bool:
        return response.ok


class AiohttpClient(BaseClient):
    method_class = AiohttpMethod

    def __init__(
            self,
            base_url: str,
            session: Optional[ClientSession] = None,
    ):
        super().__init__()
        self.session = session or ClientSession()
        self.base_url = base_url

    async def do_request(self, request: HttpRequest) -> Any:
        return await self.session.request(
            url=urllib.parse.urljoin(self.base_url, request.url),
            method=request.method,
            json=request.json_body,
            params=request.query_params,
        )
