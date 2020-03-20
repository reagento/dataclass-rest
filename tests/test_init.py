from dataclasses import dataclass

from dataclass_factory import Factory, NameStyle, Schema
from requests import Session

from dataclass_rest import get
from dataclass_rest.async_base import AsyncClient
from dataclass_rest.sync_base import Client

@dataclass
class Todo:
    id: int


def test_sync():
    class RealClient(Client):
        def __init__(self):
            super().__init__("https://jsonplaceholder.typicode.com/", Session())

        def _init_factory(self):
            return Factory(default_schema=Schema(name_style=NameStyle.camel_lower))

        @get("todos/{id}")
        def get_todo(self, id: str) -> Todo:
            pass

    assert RealClient()


def test_async():
    class RealClient(AsyncClient):
        def __init__(self):
            super().__init__("https://jsonplaceholder.typicode.com/", Session())

        def _init_factory(self):
            return Factory(default_schema=Schema(name_style=NameStyle.camel_lower))

        @get("todos/{id}")
        async def get_todo(self, id: str) -> Todo:
            pass

    assert RealClient()
