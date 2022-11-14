import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, TypeVar, Generic

from dataclass_factory import Schema
from requests import Session

from dataclass_rest import get
from dataclass_rest.http.requests import RequestsClient

T = TypeVar("T")


@dataclass
class Response(Generic[T]):
    response: T


@dataclass
class User:
    id: int
    first_name: str
    last_name: str


class GenderQuery(Enum):
    MALE = 2
    FEMALE = 1
    ANY = 9


@dataclass
class UsersSearchResult:
    count: int
    items: List[User]


class VkClient(RequestsClient):
    def __init__(self, token: str):
        session = Session()
        session.params = {"access_token": token, "v": "5.131"}
        super(VkClient, self).__init__(
            base_url="https://api.vk.com/method/",
            session=session,
        )

    def set_token(self, token: str) -> None:
        self.session.query_params["access_token"] = token

    def _init_request_args_schemas(self):
        schemas = super()._init_request_args_schemas()
        return schemas | {
            int: Schema(serializer=str),
            bool: Schema(serializer=int),
            List[int]: Schema(post_serialize=lambda d: ",".join(d)),
            List[str]: Schema(post_serialize=lambda d: ",".join(d)),
        }

    @get("users.get")
    def get_users(self, user_ids: List[str]) -> Response[List[User]]:
        pass

    @get("users.search")
    def search_users(
            self, q: str, sort: bool = False,
            offset: int = 0, count: int = 20,
            gender: GenderQuery = GenderQuery.ANY,
    ) -> Response[UsersSearchResult]:
        pass


TOKEN = ""


def main():
    logging.basicConfig(level=logging.INFO)
    client = VkClient(TOKEN)
    print(client.get_users(["1", "2"]))
    print(client.search_users(q="tishka17", gender=GenderQuery.MALE))


if __name__ == '__main__':
    main()
