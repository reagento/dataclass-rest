from dataclasses import dataclass
from typing import Any, Dict, Type, Callable


class MethodSpec:
    def __init__(
            self,
            func: Callable,
            url_template: str,
            http_method: str,
            response_type: Type,
            body_param_name: str,
            body_type: Type,
            query_params_type: Type,
            additional_params: Dict[str, Any],
    ):
        self.func = func
        self.url_template = url_template
        self.http_method = http_method
        self.response_type = response_type
        self.body_param_name = body_param_name
        self.body_type = body_type
        self.query_params_type = query_params_type
        self.additional_params = additional_params


@dataclass
class HttpRequest:
    body: Any
    query_params: Dict
    url: str
    method: str
