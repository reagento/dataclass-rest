from functools import wraps
from inspect import getcallargs, iscoroutinefunction
from typing import cast, Optional, BinaryIO

try:
    from .async_base import AsyncClient

    has_async = True
except ImportError:
    has_async = False
from .base import BaseClient
from .common import create_args_class, F, get_method_classes, get_skipped


# TODO: make wrap() function/class-wrapper for wrapping functions
def rest(url_format: str, *, method: str, body_name: str, base_url: str = ""):
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
                                body_class=body_class, result_class=result_class, base_url=base_url)

        if iscoroutinefunction(func) and has_async:
            @wraps(func)
            async def async_inner(self: AsyncClient, *args, **kwargs):
                return await inner(self, *args, **kwargs)

            return cast(F, async_inner)
        return cast(F, inner)

    return dec


def get(url_format: str, base_url: str = ""):
    return rest(url_format, method="GET", body_name="", base_url=base_url)


def delete(url_format: str, base_url: str = ""):
    return rest(url_format, method="DELETE", body_name="", base_url=base_url)


def patch(url_format: str, body_name: str = "body", base_url: str = ""):
    return rest(url_format, method="PATCH", body_name=body_name, base_url=base_url)


def put(url_format: str, body_name: str = "body", base_url: str = ""):
    return rest(url_format, method="PUT", body_name=body_name, base_url=base_url)


def post(url_format: str, body_name: str = "body", base_url: str = ""):
    return rest(url_format, method="POST", body_name=body_name, base_url=base_url)


# TODO: make wrap() function/class-wrapper for wrapping functions
def multipart(url_format: str, *, method: str, body_name: str, file_name: Optional[str] = None, base_url: str = ""):
    def dec(func):
        skipped = get_skipped(url_format, body_name)
        func.args_class = create_args_class(func, skipped)

        @wraps(func)
        def inner(self: BaseClient, *args, **kwargs):
            params = getcallargs(func, self, *args, **kwargs)
            url = url_format.format(**params)
            binary_stream = params.get(body_name)
            if not isinstance(binary_stream, BinaryIO):
                raise TypeError(f"{body_name} exptected to be BinaryIO expected, {type(binary_stream)} got")

            field_name = file_name  # field_name is multipart form field name
            if not field_name:  # if user does not provide default filename
                field_name = getattr(binary_stream, 'name')  # we will use filename from file descriptor
                if not field_name:
                    raise ValueError("File must have name")

            return self.request(url=url, method=method, file=(field_name, binary_stream), base_url=base_url)

        if iscoroutinefunction(func) and has_async:
            @wraps(func)
            async def async_inner(self: AsyncClient, *args, **kwargs):
                return await inner(self, *args, **kwargs)

            return cast(F, async_inner)
        return cast(F, inner)

    return dec


def file(url_format: str, body_name: str = "file", base_url: str = ""):
    return multipart(url_format, method="POST", body_name=body_name, base_url=base_url)
