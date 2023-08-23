import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, List, Any

import aiohttp
from adaptix import Retort, NameStyle, name_mapping
from aiohttp import ClientSession

from dataclass_rest import get, delete, post, File
from dataclass_rest.http.aiohttp import AiohttpClient


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


class RealAsyncClient(AiohttpClient):
    def __init__(self, session: ClientSession):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com/",
            session=session,
        )

    def _init_request_body_factory(self) -> Retort:
        return Retort(recipe=[
            name_mapping(name_style=NameStyle.CAMEL),
        ])

    @get("todos/{id}")
    async def get_todo(self, id: str) -> Todo:
        pass

    @get("todos")
    async def list_todos(self, user_id: Optional[int]) -> List[Todo]:
        pass

    @delete("todos/{id}")
    async def delete_todo(self, id: int):
        pass

    @post("todos")
    async def create_todo(self, body: Todo) -> Todo:
        """Созадем Todo"""

    @get("https://httpbin.org/get")
    def get_httpbin(self) -> Any:
        """Используемый другой base_url"""

    @post("https://httpbin.org/post")
    def upload_image(self, file: File):
        """Загружаем картинку"""


async def main():
    async with aiohttp.ClientSession() as session:
        logging.basicConfig(level=logging.DEBUG)
        client = RealAsyncClient(session)
        print(RealAsyncClient.list_todos.method_spec)
        print()
        print(await client.list_todos(user_id=1))
        print(await client.get_todo(id="1"))
        print(await client.delete_todo(1))
        print(await client.create_todo(
            Todo(123456789, 111222333, "By Tishka17", False)))

        print(await client.upload_image(
            File(open("async_example.py", "rb"))
        ))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
