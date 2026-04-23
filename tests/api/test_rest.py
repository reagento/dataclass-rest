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
        dirty[QueryMask](),
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
        dirty[QueryMask](),
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
        dirty[QueryMask](),
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

    query_mask_a = QueryMask(to_upper, "^a.*$")
    rest = RestBuilder(query_mask_a)

    class Api:
        @rest.get("/", Query("abc"))
        def do_get(self, abc: int, abcqwerty: int, xyz: int) -> Model: ...

    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/"),
        dirty[Method](method="GET"),
        dirty[Query](name_out="abc", original_template=None),
        query_mask_a,
        dirty[QueryMask](),
        dirty[FormQuery](),
    ]
    assert Api.do_get.spec.fields_out == [
        FieldOut(None, FieldDestination.URL, str),
        FieldOut("abc", FieldDestination.QUERY, int),
        FieldOut("ABCQWERTY", FieldDestination.QUERY, int),
        FieldOut("xyz", FieldDestination.QUERY, int),
    ]


def test_multiply_query_masks():
    def to_upper(s: str) -> str:
        return s.upper()

    query_mask_a = QueryMask(to_upper, "^a.*$")
    query_mask_x = QueryMask(to_upper, "^x.*$")
    rest = RestBuilder(query_mask_a)

    class Api:
        @rest.get("/", query_mask_x)
        def do_get(self, abc: int, xyz: str) -> Model: ...

    assert Api.do_get.spec.request_transformers == [
        dirty[Url](original_template="/"),
        dirty[Method](method="GET"),
        query_mask_x,
        query_mask_a,
        dirty[QueryMask](),
        dirty[FormQuery](),
    ]
    assert Api.do_get.spec.fields_out == [
        FieldOut(None, FieldDestination.URL, str),
        FieldOut("XYZ", FieldDestination.QUERY, str),
        FieldOut("ABC", FieldDestination.QUERY, int),
    ]
