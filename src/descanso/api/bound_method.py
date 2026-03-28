from inspect import getcallargs
from typing import (
    Any,
)

from descanso.client import (
    AsyncClient,
    AsyncResponseWrapper,
    BaseClient,
    SyncClient,
    SyncResponseWrapper,
)
from descanso.method_pipeline import MethodPipeline
from descanso.request import HttpRequest
from descanso.response import HttpResponse


def make_request(
    client: BaseClient,
    pipeline: MethodPipeline,
    args: dict[str, Any],
) -> HttpRequest:
    request = HttpRequest()
    for transformer in pipeline.request_transformers:
        transformer.transform_request(
            pipeline,
            request,
            pipeline.fields_in,
            pipeline.fields_out,
            args,
        )
    for transformer in client.request_transformers:
        transformer.transform_request(
            request,
            pipeline.fields_in,
            pipeline.fields_out,
            args,
        )
    return request


def make_response_sync(
    client: BaseClient,
    pipeline: MethodPipeline,
    request: HttpRequest,
    response: SyncResponseWrapper,
    args: dict[str, Any],
) -> Any:
    loaded = False
    for transformer in pipeline.response_transformers:
        if not loaded and transformer.need_response_body(response):
            response.load_body()
            loaded = True
        response = transformer.transform_response(
            pipeline,
            pipeline.fields_in,
            pipeline.fields_out,
            args,
            request,
            response,
        )
    for transformer in client.response_transformers:
        if not loaded and transformer.need_response_body(response):
            response.load_body()
            loaded = True
        response = transformer.transform_response(
            pipeline,
            pipeline.fields_in,
            pipeline.fields_out,
            args,
            request,
            response,
        )
    return response.body


async def make_response_async(
    client: BaseClient,
    pipeline: MethodPipeline,
    request: HttpRequest,
    response: AsyncResponseWrapper,
    args: dict[str, Any],
) -> Any:
    loaded = False
    for transformer in pipeline.response_transformers:
        if not loaded and transformer.need_response_body(response):
            await response.aload_body()
            loaded = True
        response = transformer.transform_response(
            pipeline,
            pipeline.fields_in,
            pipeline.fields_out,
            args,
            request,
            response,
        )
    for transformer in client.response_transformers:
        if not loaded and transformer.need_response_body(response):
            await response.aload_body()
            loaded = True
        response = transformer.transform_response(
            pipeline,
            pipeline.fields_in,
            pipeline.fields_out,
            args,
            request,
            response,
        )
    return response.body


def need_response_body(
    pipeline: MethodPipeline,
    response: HttpResponse,
) -> bool:
    for transformer in pipeline.response_transformers:
        if transformer.need_response_body(response):
            return True
    return False


class BoundSyncMethod:
    __slots__ = ("_client", "_pipeline")

    def __init__(self, pipeline: MethodPipeline, client: SyncClient) -> None:
        self._pipeline = pipeline
        self._client = client

    def __call__(self, *args, **kwargs):
        args = getcallargs(self._pipeline.func, self._client, *args, **kwargs)
        request = make_request(self._client, self._pipeline, args)
        with self._client.send_request(request) as response:
            return make_response_sync(
                self._client,
                self._pipeline,
                request,
                response,
                args,
            )


class BoundAsyncMethod:
    __slots__ = ("_client", "_pipeline")

    def __init__(self, pipeline: MethodPipeline, client: AsyncClient) -> None:
        self._pipeline = pipeline
        self._client = client

    async def __call__(self, *args, **kwargs):
        args = getcallargs(self._pipeline.func, self._client, *args, **kwargs)
        request = make_request(self._client, self._pipeline, args)
        async with self._client.asend_request(request) as response:
            return await make_response_async(
                self._client,
                self._pipeline,
                request,
                response,
                args,
            )
