from inspect import getcallargs, iscoroutinefunction
from functools import wraps
from typing import cast

try:
    from .async_base import AsyncClient

    has_async = True
except ImportError:
    has_async = False

from ..common import create_args_class, F, get_method_classes, get_skipped
from .client import JSONRPCClient


def rest(json_rpc_method: str, *, method: str, body_name: str):
    def dec(func):
        result_class, body_class = get_method_classes(func, body_name)

        @wraps(func)
        def inner(self: JSONRPCClient, *args, **kwargs):
            params = getcallargs(func, self, *args, **kwargs)
            body = params.get(body_name)
            body = self.create_request(json_rpc_method, body)
            return self.request(method=method,
                                body=body,
                                body_class=body_class, result_class=result_class)

        if iscoroutinefunction(func) and has_async:
            @wraps(func)
            async def async_inner(self: AsyncClient, *args, **kwargs):
                return await inner(self, *args, **kwargs)

            return cast(F, async_inner)
        return cast(F, inner)

    return dec


def get(json_rpc_method: str, body_name: str = "body"):
    return rest(json_rpc_method, method="GET", body_name=body_name)


def delete(json_rpc_method: str, body_name: str = "body"):
    return rest(json_rpc_method, method="DELETE", body_name=body_name)


def patch(json_rpc_method: str, body_name: str = "body"):
    return rest(json_rpc_method, method="PATCH", body_name=body_name)


def put(json_rpc_method: str, body_name: str = "body"):
    return rest(json_rpc_method, method="PUT", body_name=body_name)


def post(json_rpc_method: str, body_name: str = "body"):
    return rest(json_rpc_method, method="POST", body_name=body_name)
