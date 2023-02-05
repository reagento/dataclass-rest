import json
import logging
from typing import Optional, List

from pydantic import BaseModel, parse_obj_as
from pydantic.json import pydantic_encoder

from dataclass_rest import get, post, delete
from dataclass_rest.client_protocol import FactoryProtocol
from dataclass_rest.http.requests import RequestsClient


class PydanticFactory:
    def load(self, data, type):
        return parse_obj_as(type, data)

    def dump(self, data, type_):
        # There is no way to serialize data to simple types using pydantic,
        # so we encode it to json and then decode back
        return json.loads(json.dumps(data, default=pydantic_encoder))


def to_camel(string: str) -> str:
    words = string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


class Todo(BaseModel):
    id: int
    user_id: int
    title: str
    completed: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class RealClient(RequestsClient):
    def __init__(self):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com/",
        )

    def _init_request_body_factory(self) -> FactoryProtocol:
        return PydanticFactory()

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
        """Create Todo"""

    @get("https://httpbin.org/get")
    def get_httpbin(self):
        """Request with different base_url"""


logging.basicConfig(level=logging.INFO)
client = RealClient()
print(client.list_todos(user_id=1))
print(client.get_todo(id="1"))
print(client.delete_todo(1))
print(client.create_todo(Todo(
    id=123456789, user_id=111222333, title="By Tishka17", completed=False,
)))
print(client.get_httpbin())
