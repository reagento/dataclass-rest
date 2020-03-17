from dataclasses import dataclass
from typing import Optional, List

from dataclass_factory import Factory, NameStyle, Schema
from requests import Session

from base import BaseClient, get, post, delete


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


class RealClient(BaseClient):
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
        pass


client = RealClient()
print(client.list_todos(user_id=1))
print(client.get_todo(id="1"))
print(client.delete_todo(1))
print(client.create_todo(Todo(123456789, 111222333, "By Tishka17", False)))
