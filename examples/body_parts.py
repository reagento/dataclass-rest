import logging
from dataclasses import dataclass

from adaptix import NameStyle, Retort, name_mapping
from requests import Session

from descanso import RestBuilder
from descanso.http.requests import RequestsClient
from descanso.request_transformers import BodyPart


@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool


retort = Retort(
    recipe=[
        name_mapping(name_style=NameStyle.CAMEL),
    ],
)
rest = RestBuilder(
    request_body_dumper=retort,
    response_body_loader=retort,
    query_param_dumper=Retort(),
)


class RealClient(RequestsClient):
    def __init__(self):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com/",
            session=Session(),
        )

    @rest.post(
        "todos",
        BodyPart("id"),
        BodyPart("user_id"),
        BodyPart("title"),
        BodyPart("completed"),
    )
    async def create_todo(
        self,
        id: int,
        user_id: int,
        title: str,
        completed: bool,
    ) -> Todo:
        """POST method"""
        raise NotImplementedError


logging.basicConfig(level=logging.INFO)
client = RealClient()
print(
    client.create_todo(
        id=123456789,
        user_id=111222333,
        title="By Tishka17",
        completed=False,
    ),
)
