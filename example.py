import logging
from dataclasses import dataclass
from typing import Optional, List, BinaryIO, Any

from dataclass_factory import Factory, NameStyle, Schema
from requests import Session

from dataclass_rest import get, post, delete
from dataclass_rest.decorators import file
from dataclass_rest.sync_base import Client


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


class RealClient(Client):
    def __init__(self):
        super().__init__("https://jsonplaceholder.typicode.com/", Session())

    def _init_factory(self):
        return Factory(default_schema=Schema(name_style=NameStyle.camel_lower))

    @get("todos/{id}")
    def get_todo(self, id: str) -> Todo:
        pass

    @get("todos")
    def list_todos(self, user_id: Optional[int]) -> List[Todo]:
        pass

    @delete("todos/{id}")
    def delete_todo(self, id: int):
        pass

    @post("todos")
    def create_todo(self, body: Todo) -> Todo:
        """Созадем Todo"""

    @get("get", base_url="https://httpbin.org/")
    def get_httpbin(self):
        """Используемый другой base_url"""

    @file("post", base_url="https://httpbin.org/")
    def upload_image(self, f: BinaryIO):
        """Заргужаем картинку"""


logging.basicConfig(level=logging.DEBUG)
client = RealClient()
print(client.list_todos(user_id=1))
print(client.get_todo(id="1"))
print(client.delete_todo(1))
print(client.create_todo(Todo(123456789, 111222333, "By Tishka17", False)))
