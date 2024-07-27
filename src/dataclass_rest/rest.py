from functools import partial
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


get = partial(rest, method="GET")
post = partial(rest, method="POST")
put = partial(rest, method="PUT")
patch = partial(rest, method="PATCH")
delete = partial(rest, method="DELETE")
