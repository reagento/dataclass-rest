from dataclasses import dataclass
from typing import Optional, List

from dataclass_factory import Factory, NameStyle, Schema
from requests import Session

from base import BaseClient, get


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


print(RealClient().list_todos(user_id=1))
