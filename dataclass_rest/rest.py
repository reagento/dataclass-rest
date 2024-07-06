from typing import Any, Dict, Optional, Callable, ParamSpec, TypeVar

from .boundmethod import BoundMethod
from .method import Method
from .parse_func import parse_func, DEFAULT_BODY_PARAM

_P = ParamSpec("_P")
_RT = TypeVar("_RT")


def rest(
        url_template: str,
        *,
        method: str,
        body_name: str = DEFAULT_BODY_PARAM,
        additional_params: Optional[Dict[str, Any]] = None,
        method_class: Optional[Callable[..., BoundMethod]] = None,
        send_json: bool = True,
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
            is_json_request=send_json,
        )
        return Method(method_spec, method_class=method_class)

    return dec


def _rest_method(func: Callable[_P, _RT], method: str) -> Callable[_P, _RT]:
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _RT:
        return func(*args, **kwargs, method=method)

    return wrapper
    

get = _rest_method(rest, method="GET")
post = _rest_method(rest, method="POST")
put = _rest_method(rest, method="PUT")
patch = _rest_method(rest, method="PATCH")
delete = _rest_method(rest, method="DELETE")
