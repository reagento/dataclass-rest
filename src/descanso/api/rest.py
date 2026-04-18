from collections.abc import Awaitable, Callable
from typing import (
    Any,
    Concatenate,
    ParamSpec,
    TypedDict,
    TypeVar,
    overload,
)

from descanso.client import Dumper, Loader
from descanso.fields import FieldDestination, FieldOut
from descanso.method_pipeline import MethodPipeline
from descanso.request import RequestTransformer
from descanso.response import HttpResponse, ResponseTransformer
from descanso.signature import make_method_pipeline
from descanso.transformers.request import (
    Body,
    BodyModelDump,
    FormQuery,
    JsonDump,
    Method,
    Query,
    QueryMask,
    QueryModelDump,
)
from descanso.transformers.response import (
    BodyModelLoad,
    ErrorRaiser,
    JsonLoad,
    KeepResponse,
)
from descanso.typing_compat import Unpack
from .builder_base import (
    DEFAULT_BODY_PARAM,
    Decorator,
    Transformer,
    UrlSrc,
    url_transformer,
)
from .method_descriptor import MethodBinder

_MethodResultT = TypeVar("_MethodResultT")
_MethodParamSpec = ParamSpec("_MethodParamSpec")


class BuilderParams(TypedDict, total=False):
    body_name: str

    query_param_dumper: Dumper | None
    request_body_dumper: Dumper | None
    request_body_post_dump: RequestTransformer | None
    query_param_post_dump: RequestTransformer | None
    default_query: QueryMask | None

    response_body_loader: Loader | None
    response_body_pre_load: ResponseTransformer | None
    error_raiser: ResponseTransformer | None


class RestBuilder(Decorator):
    def __init__(
        self,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> None:
        self.transformers = transformers
        self.params = params

    def with_params(
        self,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> "RestBuilder":
        return RestBuilder(
            *transformers,
            *self.transformers,
            **(self.params | params),
        )

    def get(
        self,
        url: UrlSrc,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> "RestBuilder":
        return self.with_params(
            url_transformer(url),
            Method("GET"),
            *transformers,
            **params,
        )

    def post(
        self,
        url: UrlSrc,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> "RestBuilder":
        return self.with_params(
            url_transformer(url),
            Method("POST"),
            *transformers,
            **params,
        )

    def put(
        self,
        url: UrlSrc,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> "RestBuilder":
        return self.with_params(
            url_transformer(url),
            Method("PUT"),
            *transformers,
            **params,
        )

    def patch(
        self,
        url: UrlSrc,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> "RestBuilder":
        return self.with_params(
            url_transformer(url),
            Method("PATCH"),
            *transformers,
            **params,
        )

    def delete(
        self,
        url: UrlSrc,
        *transformers: Transformer,
        **params: Unpack[BuilderParams],
    ) -> "RestBuilder":
        return self.with_params(
            url_transformer(url),
            Method("DELETE"),
            *transformers,
            **params,
        )

    def _add_request_transformer(
        self,
        pipeline: MethodPipeline,
        transformer: RequestTransformer,
    ):
        pipeline.request_transformers.append(transformer)
        pipeline.fields_out.extend(
            transformer.transform_fields(pipeline, pipeline.fields_in),
        )

    def _get_body_field(self, pipeline: MethodPipeline) -> FieldOut | None:
        for field in pipeline.fields_out:
            if field.dest is FieldDestination.BODY:
                return field
        return None

    def _add_default_request_body_transformers(self, pipeline: MethodPipeline):
        default_body_name = self.params.get("body_name", DEFAULT_BODY_PARAM)

        body_out = self._get_body_field(pipeline)
        for field in pipeline.fields_in:
            if field.consumed_by:
                continue
            if not body_out and field.name == default_body_name:
                self._add_request_transformer(pipeline, Body(field.name))

        if self._get_body_field(pipeline):
            dumper = self.params.get("request_body_dumper")
            if dumper:
                self._add_request_transformer(pipeline, BodyModelDump(dumper))

            post_dump = self.params.get("request_body_post_dump", ...)
            if post_dump is ...:
                self._add_request_transformer(pipeline, JsonDump())
            elif post_dump:
                self._add_request_transformer(pipeline, post_dump)

    def _add_default_query_transformers(self, pipeline: MethodPipeline):
        if query_mask := self.params.get("default_query"):
            self._add_request_transformer(pipeline, query_mask)
        for field in pipeline.fields_in:
            if field.consumed_by:
                continue
            self._add_request_transformer(pipeline, Query(field.name))

        if dumper := self.params.get("query_param_dumper"):
            self._add_request_transformer(pipeline, QueryModelDump(dumper))
        query_post_dump = self.params.get("query_param_post_dump", ...)
        if query_post_dump is ...:
            self._add_request_transformer(pipeline, FormQuery())
        elif query_post_dump:
            self._add_request_transformer(pipeline, query_post_dump)
        return []

    def _add_default_response_transformers(
        self,
        pipeline: MethodPipeline,
    ) -> None:
        error_raiser = self.params.get("error_raiser", ...)
        if error_raiser is ...:
            pipeline.response_transformers.append(ErrorRaiser())
        elif error_raiser:
            pipeline.response_transformers.append(error_raiser)

        pre_loader = self.params.get("response_body_pre_load", ...)
        if pre_loader is ...:
            pipeline.response_transformers.append(JsonLoad())
        elif pre_loader:
            pipeline.response_transformers.append(pre_loader)

        loader = self.params.get("response_body_loader")
        if pipeline.result_type is HttpResponse:
            pipeline.response_transformers.append(
                KeepResponse(need_body=False),
            )
        elif (
            loader
            and pipeline.result_type is not Any
            and pipeline.result_type is not object
        ):
            pipeline.response_transformers.append(
                BodyModelLoad(pipeline.result_type, loader=loader),
            )

    @overload
    def __call__(
        self,
        func: Callable[
            Concatenate[Any, _MethodParamSpec],
            Awaitable[_MethodResultT],
        ],
    ) -> MethodBinder[_MethodParamSpec, _MethodResultT]: ...

    @overload
    def __call__(
        self,
        func: Callable[Concatenate[Any, _MethodParamSpec], _MethodResultT],
    ) -> MethodBinder[_MethodParamSpec, _MethodResultT]: ...

    def __call__(
        self,
        func: Callable[Concatenate[Any, _MethodParamSpec], Any],
    ) -> MethodBinder[_MethodParamSpec, _MethodResultT]:
        pipeline = make_method_pipeline(
            func,
            transformers=self.transformers,
            is_in_class=True,
        )
        self._add_default_request_body_transformers(pipeline)
        self._add_default_query_transformers(pipeline)
        self._add_default_response_transformers(pipeline)
        return MethodBinder(pipeline)
