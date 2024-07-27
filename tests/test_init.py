from dataclasses import dataclass

import pytest
from adaptix import NameStyle, Retort, name_mapping
from requests import Session

from dataclass_rest import get
from dataclass_rest.http.aiohttp import AiohttpClient
from dataclass_rest.http.requests import RequestsClient


@dataclass
class Todo:
    id: int


def test_sync():
    class RealClient(RequestsClient):
        def __init__(self):
            super().__init__(
                "https://jsonplaceholder.typicode.com/",
                Session(),
            )

        def _init_request_body_factory(self) -> Retort:
            return Retort(recipe=[
                name_mapping(name_style=NameStyle.CAMEL),
            ])

        @get("todos/{id}")
        def get_todo(self, id: str) -> Todo:
            pass

    assert RealClient()


@pytest.mark.asyncio
async def test_async():
    class RealClient(AiohttpClient):
        def __init__(self):
            super().__init__("https://jsonplaceholder.typicode.com/")

        def _init_request_body_factory(self) -> Retort:
            return Retort(recipe=[
                name_mapping(name_style=NameStyle.CAMEL),
            ])

        @get("todos/{id}")
        async def get_todo(self, id: str) -> Todo:
            pass

    client = RealClient()
    await client.session.close()
