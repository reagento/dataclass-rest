from dataclasses import dataclass
from enum import Enum

from adaptix import Retort, NameStyle, name_mapping

from dataclass_rest import patch
from dataclass_rest.http.requests import RequestsClient


class Selection(Enum):
    ONE = "ONE"
    TWO = "TWO"


@dataclass
class RequestBody:
    int_param: int
    selection: Selection


@dataclass
class ResponseBody:
    int_param: int
    selection: Selection


def test_body(session, mocker):
    class Api(RequestsClient):
        def _init_request_body_factory(self) -> Retort:
            return Retort(recipe=[
                name_mapping(name_style=NameStyle.CAMEL),
            ])

        def _init_request_args_factory(self) -> Retort:
            return Retort(recipe=[
                name_mapping(name_style=NameStyle.UPPER_DOT),
            ])

        def _init_response_body_factory(self) -> Retort:
            return Retort(recipe=[
                name_mapping(name_style=NameStyle.LOWER_KEBAB),
            ])

        @patch("/post/")
        def post_x(self, long_param: str, body: RequestBody) -> ResponseBody:
            raise NotImplementedError()

    mocker.patch(
        url="http://example.com/post/",
        text="""{"int-param": 1, "selection": "TWO"}""",
    )
    client = Api(base_url="http://example.com", session=session)
    result = client.post_x(
        long_param="hello", body=RequestBody(int_param=42, selection=Selection.ONE),
    )
    assert result == ResponseBody(int_param=1, selection=Selection.TWO)
    assert mocker.called_once
    assert mocker.request_history[0].json() == {"intParam": 42, "selection": "ONE"}
    assert mocker.request_history[0].query == "LONG.PARAM=hello"
