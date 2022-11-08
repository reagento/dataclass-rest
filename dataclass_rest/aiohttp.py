from typing import Any

from aiohttp.client import ClientResponse

from dataclass_rest.boundmethod import AsyncMethod


class AiohttpMethod(AsyncMethod):
    async def _response_body(self, response: ClientResponse) -> Any:
        return await response.json()

    async def _response_ok(self, response: ClientResponse) -> bool:
        return response.ok
