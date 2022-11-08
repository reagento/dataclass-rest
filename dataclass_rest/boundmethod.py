from inspect import getcallargs
from typing import Dict, Any, Callable, Optional

from .base_client import ClientProtocol
from .methodspec import MethodSpec, HttpRequest


class BoundMethod:
    def __init__(
            self,
            method_spec: MethodSpec,
            client: ClientProtocol,
            on_error: Optional[Callable[[Any], Any]],
    ):
        self.method_spec = method_spec
        self.client = client
        self.on_error = on_error

    def _apply_args(self, *args, **kwargs) -> Dict:
        return getcallargs(
            self.method_spec.func, self.client, *args, **kwargs,
        )

    def _get_url(self, args) -> str:
        return self.method_spec.url_template.format(**args)

    def _get_body(self, args) -> Any:
        python_body = args.get(self.method_spec.body_param_name)
        return self.client.request_body_factory.dump(
            python_body, self.method_spec.body_type,
        )

    def _get_query_params(self, args) -> Any:
        return self.client.request_args_factory.dump(
            args, self.method_spec.query_params_type,
        )

    def _create_request(
            self,
            url: str,
            query_params: Any,
            body: Any,
    ) -> HttpRequest:
        return HttpRequest(
            method=self.method_spec.http_method,
            query_params=query_params,
            body=body,
            url=url,
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def _pre_process_request(self, request: HttpRequest) -> HttpRequest:
        return request

    def _pre_process_response(self, response: Any) -> Any:
        raise NotImplementedError

    def _post_process_response(self, response: Any) -> Any:
        return response
