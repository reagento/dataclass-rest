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


client = RealClient()
print(client.get_todo(1))
print(client.delete_todo(1))
print(client.list_todos(userId=1))
