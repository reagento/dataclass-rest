from typing import Any

from dirty_equals import Contains

from descanso import Loader, RestBuilder
from descanso.client import Dumper
from descanso.fields import FieldDestination, FieldOut
from descanso.transformers.request import (
    Body,
    BodyModelDump,
    FormQuery,
    JsonDump,
    Method,
    Query,
    QueryMask,
    QueryModelDump,
    Skip,
    Url,
)
from descanso.transformers.response import BodyModelLoad, ErrorRaiser, JsonLoad
from .utils import dirty


class Model:
    pass


def test_get_with_query():
    rest = RestBuilder()

    class Api:
        @rest.get("/foo")
        def do_get(self, x: int) -> Model:
            """Hello"""

    assert Api.do_get.spec.name == "do_get"
    assert Api.do_get.spec.doc == "Hello"
    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/foo"),
        dirty[Method](method="GET"),
        dirty[Query](name_out="x", original_template=None),
        dirty[FormQuery](),
    ]
    assert Api.do_get.spec.response_transformers == [
        dirty[ErrorRaiser](),
        dirty[JsonLoad](),
    ]


def test_post_with_url_body():
    rest = RestBuilder()

    class Api:
        @rest.post("/foo{x}")
        def do_post(self, x: int, body: str) -> Model:
            """Hello"""

    assert Api.do_post.spec.request_transformers == [
        dirty[Url](original_template="/foo{x}"),
        dirty[Method](method="POST"),
        dirty[Body](arg="body"),
        dirty[JsonDump](),
        dirty[FormQuery](),
    ]
    assert Api.do_post.spec.response_transformers == [
        dirty[ErrorRaiser](),
        dirty[JsonLoad](),
    ]


def test_methods():
    rest = RestBuilder()

    class Api:
        @rest.get("/")
        def do_get(self) -> None: ...

        @rest.post("/")
        def do_post(self) -> None: ...

        @rest.delete("/")
        def do_delete(self) -> None: ...

        @rest.put("/")
        def do_put(self) -> None: ...

        @rest.patch("/")
        def do_patch(self) -> None: ...

    assert Api.do_get.spec.request_transformers == Contains(
        dirty[Method](method="GET"),
    )
    assert Api.do_post.spec.request_transformers == Contains(
        dirty[Method](method="POST"),
    )
    assert Api.do_delete.spec.request_transformers == Contains(
        dirty[Method](method="DELETE"),
    )
    assert Api.do_put.spec.request_transformers == Contains(
        dirty[Method](method="PUT"),
    )
    assert Api.do_patch.spec.request_transformers == Contains(
        dirty[Method](method="PATCH"),
    )


class StubConverter(Dumper, Loader):
    def dump(self, data: Any, class_: Any) -> Any: ...

    def load(self, data: Any, class_: Any) -> Any: ...


def test_params():
    req_additional = Skip("0")
    resp_additional = ErrorRaiser(codes=[200])
    query_param_dumper = StubConverter()
    query_param_post_dump = Skip("1")
    request_body_dumper = StubConverter()
    response_body_loader = StubConverter()
    request_body_post_dump = Skip("2")
    error_raiser = ErrorRaiser(codes=[400])
    response_body_pre_load = ErrorRaiser(codes=[500])
    rest = RestBuilder(
        req_additional,
        resp_additional,
        query_param_dumper=query_param_dumper,
        query_param_post_dump=query_param_post_dump,
        request_body_dumper=request_body_dumper,
        response_body_loader=response_body_loader,
        request_body_post_dump=request_body_post_dump,
        body_name="x",
        error_raiser=error_raiser,
        response_body_pre_load=response_body_pre_load,
    )

    class Api:
        @rest.get("/")
        def do_get(self, x: int, body: str) -> Model: ...

    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/"),
        dirty[Method](method="GET"),
        req_additional,
        dirty[Body](arg="x"),
        dirty[BodyModelDump](dumper=request_body_dumper),
        request_body_post_dump,
        dirty[Query](name_out="body", original_template=None),
        dirty[QueryModelDump](dumper=query_param_dumper),
        query_param_post_dump,
    ]
    assert Api.do_get.spec.response_transformers == [
        resp_additional,
        error_raiser,
        response_body_pre_load,
        dirty[BodyModelLoad](type_hint=Model, loader=response_body_loader),
    ]


def test_override_params():
    error_raiser = ErrorRaiser(codes=[400])
    response_body_pre_load = ErrorRaiser(codes=[500])
    response_body_pre_load2 = ErrorRaiser(codes=[502])
    rest = RestBuilder(
        error_raiser=error_raiser,
        response_body_pre_load=response_body_pre_load,
    )

    class Api:
        @rest.get("/", response_body_pre_load=response_body_pre_load2)
        def do_get(self, x: int, body: str) -> Model: ...

    assert Api.do_get.spec.response_transformers == [
        error_raiser,
        response_body_pre_load2,
    ]


def test_query_mask():
    def to_upper(s: str) -> str:
        return s.upper()

    query_mask = QueryMask(to_upper, "^u.*$")
    rest = RestBuilder(default_query=query_mask)

    class Api:
        @rest.get("/")
        def do_get(self, user_id: int, phone_number: str) -> Model: ...

    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/"),
        dirty[Method](method="GET"),
        dirty[QueryMask](regex="^u.*$", name_style=to_upper),
        dirty[Query](name_out="phone_number", original_template=None),
        dirty[FormQuery](),
    ]
    assert Api.do_get.spec.fields_out == [
        FieldOut(None, FieldDestination.URL, str),
        FieldOut("USER_ID", FieldDestination.QUERY, int),
        FieldOut("phone_number", FieldDestination.QUERY, str),
    ]


def test_multiply_query_masks():
    def to_upper(s: str) -> str:
        return s.upper()

    query_mask = QueryMask(to_upper, "^u.*$")
    rest = RestBuilder(default_query=query_mask)

    class Api:
        @rest.get("/", QueryMask(to_upper, "^p.*$"))
        def do_get(self, user_id: int, phone_number: str) -> Model: ...

    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/"),
        dirty[Method](method="GET"),
        dirty[QueryMask](regex="^p.*$", name_style=to_upper),
        dirty[QueryMask](regex="^u.*$", name_style=to_upper),
        dirty[FormQuery](),
    ]
    assert Api.do_get.spec.fields_out == [
        FieldOut(None, FieldDestination.URL, str),
        FieldOut("PHONE_NUMBER", FieldDestination.QUERY, str),
        FieldOut("USER_ID", FieldDestination.QUERY, int),
    ]


def test_query_mask_override():
    def to_upper(s: str) -> str:
        return s.upper()

    def to_title(s: str) -> str:
        return s.title()

    query_mask = QueryMask(to_upper, "^a.*$")
    rest = RestBuilder(default_query=query_mask)

    class Api:
        @rest.get("/", QueryMask(to_title, "^a.*$"))
        def do_get(self, abc: str) -> Model: ...

    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/"),
        dirty[Method](method="GET"),
        dirty[QueryMask](regex="^a.*$", name_style=to_title),
        dirty[QueryMask](regex="^a.*$", name_style=to_upper),
        dirty[FormQuery](),
    ]
    assert Api.do_get.spec.fields_out == [
        FieldOut(None, FieldDestination.URL, str),
        FieldOut("Abc", FieldDestination.QUERY, str),
    ]
