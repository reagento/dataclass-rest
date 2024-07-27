from dataclasses import dataclass
from typing import List, Optional

import requests
import requests_mock

from dataclass_rest import get, post
from dataclass_rest.http.requests import RequestsClient


def test_methods(session: requests.Session, mocker: requests_mock.Mocker):
    class Api(RequestsClient):
        @get("/get")
        def get_x(self) -> List[int]:
            raise NotImplementedError

        @post("/post")
        def post_x(self) -> List[int]:
            raise NotImplementedError

    mocker.get("http://example.com/get", text="[1,2]", complete_qs=True)
    mocker.post("http://example.com/post", text="[1,2,3]", complete_qs=True)
    client = Api(base_url="http://example.com", session=session)
    assert client.get_x() == [1, 2]
    assert client.post_x() == [1, 2, 3]


def test_path_params(session: requests.Session, mocker: requests_mock.Mocker):
    class Api(RequestsClient):
        @post("/post/{id}")
        def post_x(self, id) -> List[int]:
            raise NotImplementedError

    mocker.post("http://example.com/post/1", text="[1]", complete_qs=True)
    mocker.post("http://example.com/post/2", text="[1,2]", complete_qs=True)
    client = Api(base_url="http://example.com", session=session)
    assert client.post_x(1) == [1]
    assert client.post_x(2) == [1, 2]


def test_query_params(session: requests.Session, mocker: requests_mock.Mocker):
    class Api(RequestsClient):
        @post("/post/{id}")
        def post_x(self, id: str, param: Optional[int]) -> List[int]:
            raise NotImplementedError

    mocker.post(
        url="http://example.com/post/x?",
        text="[0]", complete_qs=True,
    )
    mocker.post(
        url="http://example.com/post/x?param=1",
        text="[1]", complete_qs=True,
    )
    mocker.post(
        url="http://example.com/post/x?param=2",
        text="[1,2]", complete_qs=True,
    )
    client = Api(base_url="http://example.com", session=session)
    assert client.post_x("x", None) == [0]
    assert client.post_x("x", 1) == [1]
    assert client.post_x("x", 2) == [1, 2]


@dataclass
class RequestBody:
    x: int
    y: str


def test_body(session: requests.Session, mocker: requests_mock.Mocker):
    class Api(RequestsClient):
        @post("/post/")
        def post_x(self, body: RequestBody) -> None:
            raise NotImplementedError

    mocker.post(
        url="http://example.com/post/",
        text="null", complete_qs=True,
    )
    client = Api(base_url="http://example.com", session=session)
    assert client.post_x(RequestBody(x=1, y="test")) is None
    assert mocker.called_once
    assert mocker.request_history[0].json() == {"x": 1, "y": "test"}
