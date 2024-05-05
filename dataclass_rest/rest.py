import inspect
from functools import partial
from typing import Any, Dict, Optional, Callable

from .boundmethod import BoundMethod
from .method import Method
from .parse_func import parse_func, DEFAULT_BODY_PARAM


class rest:
    def __init__(
            self,
            url_template: str,
            *,
            method: str,
            body_name: str = DEFAULT_BODY_PARAM,
            additional_params: Optional[Dict[str, Any]] = None,
            method_class: Optional[Callable[..., BoundMethod]] = None,
            send_json: bool = True,
    ):
        if additional_params is None:
            additional_params = {}
        self.url_template = url_template
        self.method = method
        self.body_name = body_name
        self.additional_params = additional_params
        self.method_class = method_class
        self.send_json = send_json

    def __set_name__(self, owner, name):
        for cls in inspect.getmro(owner):
            if cls is owner:
                continue
            func = getattr(cls, name, None)
            if not func:
                continue
            method = self(func)
            setattr(owner, name, method)
            method.__set_name__(owner, name)
            return

    def __call__(self, func: Callable) -> Method:
        method_spec = parse_func(
            func=func,
            body_param_name=self.body_name,
            url_template=self.url_template,
            method=self.method,
            additional_params=self.additional_params,
            is_json_request=self.send_json,
        )
        return Method(method_spec, method_class=self.method_class)


get = partial(rest, method="GET")
post = partial(rest, method="POST")
put = partial(rest, method="PUT")
patch = partial(rest, method="PATCH")
delete = partial(rest, method="DELETE")
