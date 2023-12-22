from inspect import FullArgSpec
from typing import Any, Dict, Type, Callable, List, Optional


class MethodSpec:
    def __init__(
            self,
            func: Callable,
            func_arg_spec: FullArgSpec,
            url_template: Optional[str],
            url_template_func: Optional[Callable[..., str]],
            url_template_func_arg_spec: Optional[FullArgSpec],
            url_template_func_pop_args: Optional[List[str]],
            http_method: str,
            response_type: Type,
            body_param_name: str,
            body_type: Type,
            is_json_request: bool,
            query_params_type: Type,
            file_param_names: List[str],
            additional_params: Dict[str, Any],
    ):
        self.func = func
        self.url_template = url_template
        self.url_template_func = url_template_func
        self.url_template_func_pop_args = url_template_func_pop_args
        self.http_method = http_method
        self.response_type = response_type
        self.body_param_name = body_param_name
        self.body_type = body_type
        self.query_params_type = query_params_type
        self.additional_params = additional_params
        self.is_json_request = is_json_request
        self.file_param_names = file_param_names
        self.func_arg_spec = func_arg_spec
        self.url_template_func_arg_spec = url_template_func_arg_spec
