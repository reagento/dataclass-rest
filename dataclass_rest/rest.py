from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Dict, Optional, Callable

from .call_transform import transform_call, transform_result
from .method import Method
from .parse_func import parse_func, DEFAULT_BODY_PARAM


def as_sync_rest(
        method_spec: Method,
):
    @wraps(method_spec.func)
    def inner(self, *args, **kwargs):
        args = transform_call(
            client=self,
            method=method_spec,
            args=args,
            kwargs=kwargs,
        )

        response = self.request(
            url=args.url,
            method=method_spec.method,
            params=args.query_params,
            body=args.body,
            # TODO file
        )

        return transform_result(
            client=self, method=method_spec, result=response,
        )

    return inner


def as_async_rest(
        method_spec: Method,
):
    @wraps
    async def inner(self, *args, **kwargs):
        args = transform_call(
            client=self,
            method=method_spec,
            args=args,
            kwargs=kwargs,
        )

        response = await self.request(
            url=args.url,
            params=args.query_params,
            body=args.body,
            # TODO file
        )

        return transform_result(
            client=self, method=method_spec, result=response,
        )

    return inner


def rest(
        url_template: str,
        *,
        method: str,
        body_name: str = DEFAULT_BODY_PARAM,
        additional_params: Optional[Dict[str, Any]] = None,
):
    if additional_params is None:
        additional_params = {}

    def dec(func: Callable):
        method_spec = parse_func(
            func=func,
            body_param_name=body_name,
            url_template=url_template,
            method=method,
            additional_params=additional_params,
        )
        if iscoroutinefunction(func):
            return as_async_rest(method_spec)
        else:
            return as_sync_rest(method_spec)

    return dec
