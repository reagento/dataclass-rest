import logging
from dataclasses import dataclass
from typing import Optional, List

from dataclass_factory import Factory, NameStyle, Schema

from dataclass_rest import get, post, delete, File
from dataclass_rest.http.requests import RequestsClient


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


class RealClient(RequestsClient):
    def __init__(self):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com/",
        )

    def _init_request_body_factory(self) -> Factory:
        return Factory(default_schema=Schema(name_style=NameStyle.camel_lower))

    @get("todos/{id}")
    def get_todo(self, id: str) -> Todo:
        pass

    @get("todos")
    def list_todos(self, user_id: Optional[int]) -> List[Todo]:
        pass

    @list_todos.query_params_schema
    def list_todos(self) -> Optional[Schema]:
        # here we can customize Schema generation for query params
        return None

    @delete("todos/{id}")
    def delete_todo(self, id: int):
        pass

    @post("todos")
    def create_todo(self, body: Todo) -> Todo:
        """Созадем Todo"""

    @get("https://httpbin.org/get")
    def get_httpbin(self):
        """Используемый другой base_url"""

    @post("https://httpbin.org/post")
    def upload_image(self, file: File):
        """Заргужаем картинку"""


logging.basicConfig(level=logging.INFO)
client = RealClient()
print(client.list_todos(user_id=1))
print(client.get_todo(id="1"))
print(client.delete_todo(1))
print(client.create_todo(Todo(123456789, 111222333, "By Tishka17", False)))
print(client.get_httpbin())
print(client.upload_image(File(open("example.py", "rb"))))
