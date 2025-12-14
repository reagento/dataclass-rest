from inspect import getcallargs
from typing import (
    Any,
)

from .client import (
    AsyncClient,
    AsyncResponseWrapper,
    BaseClient,
    SyncClient,
    SyncResponseWrapper,
)
from .method_pipeline import MethodPipeline
from .request import HttpRequest
from .response import HttpResponse


def make_request(
    client: BaseClient,
    spec: MethodPipeline,
    args: dict[str, Any],
) -> HttpRequest:
    request = HttpRequest()
    for transformer in spec.request_transformers:
        transformer.transform_request(
            spec,
            request,
            spec.fields_in,
            spec.fields_out,
            args,
        )
    for transformer in client.request_transformers:
        transformer.transform_request(
            request,
            spec.fields_in,
            spec.fields_out,
            args,
        )
    return request


def make_response_sync(
    client: BaseClient,
    spec: MethodPipeline,
    request: HttpRequest,
    response: SyncResponseWrapper,
    args: dict[str, Any],
) -> Any:
    loaded = False
    for transformer in spec.response_transformers:
        if not loaded and transformer.need_response_body(response):
            response.load_body()
            loaded = True
        response = transformer.transform_response(
            spec,
            spec.fields_in,
            spec.fields_out,
            args,
            request,
            response,
        )
    for transformer in client.response_transformers:
        if not loaded and transformer.need_response_body(response):
            response.load_body()
            loaded = True
        response = transformer.transform_response(
            spec,
            spec.fields_in,
            spec.fields_out,
            args,
            request,
            response,
        )
    return response.body


async def make_response_async(
    client: BaseClient,
    spec: MethodPipeline,
    request: HttpRequest,
    response: AsyncResponseWrapper,
    args: dict[str, Any],
) -> Any:
    loaded = False
    for transformer in spec.response_transformers:
        if not loaded and transformer.need_response_body(response):
            await response.aload_body()
            loaded = True
        response = transformer.transform_response(
            spec,
            spec.fields_in,
            spec.fields_out,
            args,
            request,
            response,
        )
    for transformer in client.response_transformers:
        if not loaded and transformer.need_response_body(response):
            await response.aload_body()
            loaded = True
        response = transformer.transform_response(
            spec,
            spec.fields_in,
            spec.fields_out,
            args,
            request,
            response,
        )
    return response.body


def need_response_body(
    spec: MethodPipeline,
    response: HttpResponse,
) -> bool:
    for transformer in spec.response_transformers:
        if transformer.need_response_body(response):
            return True
    return False


class BoundSyncMethod:
    __slots__ = ("_client", "_spec")

    def __init__(self, spec: MethodPipeline, client: SyncClient) -> None:
        self._spec = spec
        self._client = client

    def __call__(self, *args, **kwargs):
        args = getcallargs(self._spec.func, self._client, *args, **kwargs)
        request = make_request(self._client, self._spec, args)
        with self._client.send_request(request) as response:
            return make_response_sync(
                self._client,
                self._spec,
                request,
                response,
                args,
            )


class BoundAsyncMethod:
    __slots__ = ("_client", "_spec")

    def __init__(self, spec: MethodPipeline, client: AsyncClient) -> None:
        self._spec = spec
        self._client = client

    async def __call__(self, *args, **kwargs):
        args = getcallargs(self._spec.func, self._client, *args, **kwargs)
        request = make_request(self._client, self._spec, args)
        async with self._client.asend_request(request) as response:
            return await make_response_async(
                self._client,
                self._spec,
                request,
                response,
                args,
            )
