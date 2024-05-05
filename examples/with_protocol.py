import logging
from dataclasses import dataclass
from typing import Optional, List, Protocol

from adaptix import Retort, name_mapping, NameStyle

from dataclass_rest import get
from dataclass_rest.http.requests import RequestsClient


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


class Client(Protocol):
    def get_todo(self, id: str) -> Todo:
        pass

    def list_todos(self, user_id: Optional[int]) -> List[Todo]:
        pass


class RealClient(RequestsClient, Client):
    def __init__(self):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com/",
        )

    def _init_request_body_factory(self) -> Retort:
        return Retort(recipe=[
            name_mapping(name_style=NameStyle.CAMEL),
        ])

    get_todo = get("todos/{id}")
    list_todos = get("todos")


logging.basicConfig(level=logging.INFO)
client = RealClient()

print(client.list_todos(user_id=1))
print(client.get_todo(id="1"))
