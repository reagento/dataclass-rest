from dataclasses import dataclass
from typing import List, Optional

from dataclass_factory import Factory, Schema, NameStyle
from requests import Session

from base import BaseClient


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

    def list_todos(self, userId: Optional[int]):
        return self.get(url="todos", params=locals(), result_class=List[Todo])

    def get_todo(self, id: int):
        return self.get(url=f"todos/{id}", result_class=Todo)

    def delete_todo(self, id: int):
        return self.delete(url=f"todos/{id}")

    def create_todo(self, todo: Todo):
        return self.post(url=f"todos", body=todo, body_class=Todo, result_class=Todo)


client = RealClient()
print(client.get_todo(1))
print(client.delete_todo(1))
print(client.create_todo(Todo(123456789, 111222333, "By Tishka17", False)))
print(client.list_todos(userId=1))
