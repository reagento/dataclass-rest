from functools import partial
from inspect import iscoroutinefunction
from typing import Any, Dict, Optional, Callable

from .boundmethod import BoundMethod
from .method import Method
from .parse_func import parse_func, DEFAULT_BODY_PARAM


def rest(
        url_template: str,
        *,
        method: str,
        body_name: str = DEFAULT_BODY_PARAM,
        additional_params: Optional[Dict[str, Any]] = None,
        method_class: Optional[Callable[..., BoundMethod]] = None
) -> Callable[[Callable], Method]:
    if additional_params is None:
        additional_params = {}

    def dec(func: Callable) -> Method:
        method_spec = parse_func(
            func=func,
            body_param_name=body_name,
            url_template=url_template,
            method=method,
            additional_params=additional_params,
        )
        if method_class:
            return Method(method_spec, method_class=method_class)
        elif iscoroutinefunction(func):
            from .requests import RequestsBoundMethod
            return Method(method_spec, method_class=RequestsBoundMethod)
        else:
            from .aiohttp import AiohttpBoundMethod
            return Method(method_spec, method_class=AiohttpBoundMethod)

    return dec


get = partial(rest, method="GET")
post = partial(rest, method="POST")
put = partial(rest, method="PUT")
patch = partial(rest, method="PATCH")
delete = partial(rest, method="DELETE")
