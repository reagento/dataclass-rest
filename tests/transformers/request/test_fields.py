from typing import Any

import pytest
from kiss_headers import Header as KissHeader
from kiss_headers import Headers

from descanso.fields import (
    FieldDestination,
    FieldIn,
    FieldOut,
)
from descanso.request import (
    FileData,
    HttpRequest,
)
from descanso.transformers.request import (
    Body,
    Extra,
    File,
    Header,
    Method,
    Query,
    QueryMask,
    Skip,
    Url,
)
from .utils import consumed_fields


def query_int(i: int) -> int:
    return i + 1


@pytest.fixture
def fields_in():
    return [
        FieldIn("i", int),
        FieldIn("s", str),
        FieldIn("a", Any),
        FieldIn("user_id", int),
        FieldIn("first_name", str),
    ]


@pytest.fixture
def data_in():
    return {
        "i": 1,
        "s": "hello",
        "a": "any",
        "user_id": 123,
        "first_name": "John",
    }


@pytest.mark.parametrize(
    ("transformer", "consumed", "body", "out"),
    [
        (
            Body("unknown"),
            [],
            None,
            [],
        ),
        (
            Body("i"),
            ["i"],
            1,
            [FieldOut(None, FieldDestination.BODY, int)],
        ),
        (
            Body("s"),
            ["s"],
            "hello",
            [FieldOut(None, FieldDestination.BODY, str)],
        ),
    ],
)
def test_body(spec, transformer, consumed, body, out, fields_in, data_in):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(body=body)


@pytest.mark.parametrize(
    ("transformer", "consumed", "extras", "out"),
    [
        (
            Extra("i"),
            ["i"],
            [("i", 1)],
            [FieldOut("i", FieldDestination.EXTRA, int)],
        ),
        (
            Extra("x", "stub"),
            [],
            [("x", "stub")],
            [FieldOut("x", FieldDestination.EXTRA, str)],
        ),
        (
            Extra("x", "{s}{i}"),
            ["i", "s"],
            [("x", "hello1")],
            [FieldOut("x", FieldDestination.EXTRA, str)],
        ),
        (
            Extra("y", query_int),
            ["i"],
            [("y", 2)],
            [FieldOut("y", FieldDestination.EXTRA, int)],
        ),
    ],
)
def test_extra(spec, transformer, consumed, extras, out, fields_in, data_in):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(extras=extras)


@pytest.mark.parametrize(
    ("transformer", "consumed", "headers", "out"),
    [
        (
            Header("i"),
            ["i"],
            Headers(KissHeader("i", "1")),
            [FieldOut("i", FieldDestination.HEADER, int)],
        ),
        (
            Header("x", "stub"),
            [],
            Headers(KissHeader("x", "stub")),
            [FieldOut("x", FieldDestination.HEADER, str)],
        ),
        (
            Header("x", "{s}{i}"),
            ["i", "s"],
            Headers(KissHeader("x", "hello1")),
            [FieldOut("x", FieldDestination.HEADER, str)],
        ),
        (
            Header("y", query_int),
            ["i"],
            Headers(KissHeader("y", "2")),
            [FieldOut("y", FieldDestination.HEADER, int)],
        ),
    ],
)
def test_header(spec, transformer, consumed, headers, out, fields_in, data_in):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(headers=headers)


@pytest.mark.parametrize(
    ("transformer", "consumed", "params", "out"),
    [
        (
            Query("i"),
            ["i"],
            [("i", 1)],
            [FieldOut("i", FieldDestination.QUERY, int)],
        ),
        (
            Query("x", "stub"),
            [],
            [("x", "stub")],
            [FieldOut("x", FieldDestination.QUERY, str)],
        ),
        (
            Query("x", "{s}{i}"),
            ["i", "s"],
            [("x", "hello1")],
            [FieldOut("x", FieldDestination.QUERY, str)],
        ),
        (
            Query("y", query_int),
            ["i"],
            [("y", 2)],
            [FieldOut("y", FieldDestination.QUERY, int)],
        ),
    ],
)
def test_query(spec, transformer, consumed, params, out, fields_in, data_in):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(query_params=params)


def snake_to_camel(u: str) -> str:
    s = u.split("_")
    return s[0] + "".join(x.title() for x in s[1:])


@pytest.mark.parametrize(
    ("transformer", "consumed", "params", "out"),
    [
        (
            QueryMask("user_id|first_name", name_style=snake_to_camel),
            ["user_id", "first_name"],
            [("userId", 123), ("firstName", "John")],
            [
                FieldOut("userId", FieldDestination.QUERY, int),
                FieldOut("firstName", FieldDestination.QUERY, str),
            ],
        ),
        (
            QueryMask(name_style=lambda n: n.upper()),
            ["i", "s", "a", "user_id", "first_name"],
            [
                ("I", 1),
                ("S", "hello"),
                ("A", "any"),
                ("USER_ID", 123),
                ("FIRST_NAME", "John"),
            ],
            [
                FieldOut("I", FieldDestination.QUERY, int),
                FieldOut("S", FieldDestination.QUERY, str),
                FieldOut("A", FieldDestination.QUERY, Any),
                FieldOut("USER_ID", FieldDestination.QUERY, int),
                FieldOut("FIRST_NAME", FieldDestination.QUERY, str),
            ],
        ),
    ],
)
def test_query_mask(
    spec, transformer, consumed, params, out, fields_in, data_in
):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(query_params=params)


@pytest.mark.parametrize(
    ("transformer", "consumed", "out"),
    [
        (
            Skip(),
            [],
            [],
        ),
        (
            Skip("s"),
            ["s"],
            [],
        ),
    ],
)
def test_skip(spec, transformer, consumed, out, fields_in, data_in):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest()


@pytest.mark.parametrize(
    ("template", "url", "consumed"),
    [
        ("/", "/", []),
        ("/{i}/{s}", "/1/hello", ["i", "s"]),
        (lambda a: f"/{a}", "/any", ["a"]),
    ],
)
def test_url(spec, template, url, consumed, fields_in, data_in):
    transformer = Url(template)
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == [FieldOut(None, FieldDestination.URL, str)]
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(url=url)


@pytest.mark.parametrize(
    ("transformer", "consumed", "files", "out"),
    [
        (
            File("s"),
            ["s"],
            [("s", FileData("hello", filename=None, content_type=None))],
            [FieldOut("s", FieldDestination.FILE, str)],
        ),
        (
            File("s", filefield="file"),
            ["s"],
            [("file", FileData("hello", filename=None, content_type=None))],
            [FieldOut("file", FieldDestination.FILE, str)],
        ),
        (
            File("s", filefield="file", filename="a.b"),
            ["s"],
            [("file", FileData("hello", filename="a.b", content_type=None))],
            [FieldOut("file", FieldDestination.FILE, str)],
        ),
        (
            File(
                "s",
                filefield="file",
                filename="a.b",
                content_type="text/plain",
            ),
            ["s"],
            [
                (
                    "file",
                    FileData(
                        "hello",
                        filename="a.b",
                        content_type="text/plain",
                    ),
                ),
            ],
            [FieldOut("file", FieldDestination.FILE, str)],
        ),
    ],
)
def test_file(spec, transformer, consumed, files, out, fields_in, data_in):
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(files=files)


def test_pipe(spec, fields_in, data_in):
    query_transformer = Query("i")
    query_transformer2 = Query("s")
    body_transformer = Body("i")
    transformer = query_transformer | query_transformer2 | body_transformer
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert fields_out == [
        FieldOut("i", FieldDestination.QUERY, int),
        FieldOut("s", FieldDestination.QUERY, str),
        FieldOut(None, FieldDestination.BODY, int),
    ]
    assert consumed_fields(fields_in, query_transformer) == ["i"]
    assert consumed_fields(fields_in, query_transformer2) == ["s"]
    assert consumed_fields(fields_in, body_transformer) == ["i"]
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(
        body=1,
        query_params=[
            ("i", 1),
            ("s", "hello"),
        ],
    )


def test_method(spec, fields_in, data_in):
    transformer = Method("GET")
    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == []
    assert fields_out == []
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(method="GET")
