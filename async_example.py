import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, List, get_type_hints

import aiohttp
from dataclass_factory import Factory, NameStyle, Schema

from dataclass_rest.async_base import AsyncBaseClient, async_get, async_delete, async_post


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


class RealAsyncClient(AsyncBaseClient):
    def __init__(self, client: aiohttp.ClientSession):
        super().__init__("https://jsonplaceholder.typicode.com/", client)

    def _init_factory(self):
        return Factory(default_schema=Schema(name_style=NameStyle.camel_lower))

    @async_get("todos/{id}")
    async def get_todo(self, id: str) -> Todo:
        pass

    @async_get("todos")
    async def list_todos(self, user_id: Optional[int]) -> List[Todo]:
        pass

    @async_delete("todos/{id}")
    async def delete_todo(self, id: int):
        pass

    @async_post("todos")
    async def create_todo(self, body: Todo) -> Todo:
        """Созадем Todo"""


async def main():
    async with aiohttp.ClientSession() as client:
        logging.basicConfig(level=logging.DEBUG)
        client = RealAsyncClient(client)
        print(get_type_hints(RealAsyncClient.list_todos.args_class))
        print()
        print(await client.list_todos(user_id=1))
        print(await client.get_todo(id="1"))
        print(await client.delete_todo(1))
        print(await client.create_todo(Todo(123456789, 111222333, "By Tishka17", False)))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
