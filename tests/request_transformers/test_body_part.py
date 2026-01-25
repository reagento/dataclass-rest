from typing import Any

import pytest
from adaptix import NameStyle, Retort, name_mapping

from descanso import Dumper
from descanso.request import (
    FieldDestination,
    FieldIn,
    FieldOut,
    HttpRequest,
)
from descanso.request_transformers import BodyPart, BodyPartDump
from tests.request_transformers.utills import consumed_fields


class BodyPartModel:
    pass


class StubDumper(Dumper):
    def dump(self, data: Any, class_: Any) -> Any:
        return ["stub", data, class_]


@pytest.fixture
def fields_in():
    return [
        FieldIn("x", int),
        FieldIn("y", str),
        FieldIn("user_id", int),
        FieldIn("user_name", str),
    ]


@pytest.fixture
def fields_out():
    return [
        FieldOut(
            name="x",
            dest=FieldDestination.BODY_PART,
            type_hint=int,
        ),
        FieldOut(
            name="y",
            dest=FieldDestination.BODY_PART,
            type_hint=str,
        ),
    ]


def test_body_part(fields_in):
    transformer = BodyPart(arg="x")
    assert str(transformer)
    assert transformer.transform_fields([fields_in[0]]) == [
        FieldOut(
            name="x",
            dest=FieldDestination.BODY_PART,
            type_hint=int,
        ),
    ]
    assert consumed_fields([fields_in[0]], transformer) == ["x"]

    request = HttpRequest()
    data = {"x": 123}

    result_request = transformer.transform_request(request, [], [], data)
    assert result_request.body == {"x": 123}

    request.body = {"username": "test"}
    result_request = transformer.transform_request(request, [], [], data)
    assert result_request.body == {"username": "test", "x": 123}


def test_body_part_dump(fields_in, fields_out):
    transformer = BodyPartDump(StubDumper())
    assert str(transformer)
    assert transformer.transform_fields(fields_in) == []
    assert consumed_fields(fields_in, transformer) == []

    request = HttpRequest(body={"x": 1, "y": "test"})
    result = transformer.transform_request(
        request,
        fields_in,
        fields_out,
        {"x": 1, "y": "test"},
    )
    assert isinstance(result.body, list)
    assert result.body[0] == "stub"

    dumped_obj = result.body[1]
    assert dumped_obj.x == 1
    assert dumped_obj.y == "test"

    dumped_class = result.body[2]
    assert dumped_class.__name__ == "StubDataclass"
    assert dumped_class.__annotations__["x"] is int
    assert dumped_class.__annotations__["y"] is str


def test_body_part_dump_with_adaptix(fields_in):
    retort = Retort(recipe=[name_mapping(name_style=NameStyle.CAMEL)])
    transformer = BodyPartDump(retort)

    fields_out_adaptix = [
        FieldOut(
            name="user_id",
            dest=FieldDestination.BODY_PART,
            type_hint=int,
        ),
        FieldOut(
            name="user_name",
            dest=FieldDestination.BODY_PART,
            type_hint=str,
        ),
    ]

    request = HttpRequest(body={"user_id": 1, "user_name": "test"})
    result = transformer.transform_request(
        request,
        fields_in,
        fields_out_adaptix,
        {"user_id": 1, "user_name": "test"},
    )
    assert result.body == {"userId": 1, "userName": "test"}
