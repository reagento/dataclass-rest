from functools import wraps
from inspect import getcallargs, iscoroutinefunction
from typing import cast

try:
    from .async_base import AsyncClient

    has_async = True
except ImportError:
    has_async = False
from .base import BaseClient
from .common import create_args_class, F, get_method_classes, get_skipped


def rest(url_format: str, *, method: str, body_name: str):
    def dec(func):
        result_class, body_class = get_method_classes(func, body_name)
        skipped = get_skipped(url_format, body_name)
        func.args_class = create_args_class(func, skipped)

        @wraps(func)
        def inner(self: BaseClient, *args, **kwargs):
            params = getcallargs(func, self, *args, **kwargs)
            url = url_format.format(**params)
            body = params.get(body_name)
            serialized_params = self.args_factory.dump(params, func.args_class)
            return self.request(url=url, method=method,
                                body=body, params=serialized_params,
                                body_class=body_class, result_class=result_class)

        if iscoroutinefunction(func) and has_async:
            @wraps(func)
            async def async_inner(self: AsyncClient, *args, **kwargs):
                return await inner(self, *args, **kwargs)

            return cast(F, async_inner)
        return cast(F, inner)

    return dec


def get(url_format: str):
    return rest(url_format, method="GET", body_name="")


def delete(url_format: str):
    return rest(url_format, method="DELETE", body_name="")


def patch(url_format: str, body_name: str = "body"):
    return rest(url_format, method="PATCH", body_name=body_name)


def put(url_format: str, body_name: str = "body"):
    return rest(url_format, method="PUT", body_name=body_name)


def post(url_format: str, body_name: str = "body"):
    return rest(url_format, method="POST", body_name=body_name)
