import urllib.parse
from typing import Any, Optional

from requests import Session

from .base_client import BaseClient
from .boundmethod import BoundMethod
from .methodspec import HttpRequest


class RequestsBoundMethod(BoundMethod):
    def __call__(self, *args, **kwargs):
        func_args = self._apply_args(*args, **kwargs)
        request = self._create_request(
            url=self._get_url(func_args),
            query_params=self._get_query_params(func_args),
            body=self._get_body(func_args)
        )
        request = self._pre_process_request(request)
        raw_response = self.client.do_request(request)
        response = self._pre_process_response(raw_response)
        response = self._post_process_response(response)
        return response

    def _pre_process_response(self, response: Any) -> Any:
        if not response.ok:
            return self.on_error(response)
        return self.client.response_body_factory.load(
            response.json(), self.method_spec.response_type,
        )


class RequestsClient(BaseClient):
    def __init__(
            self,
            base_url: str,
            session: Optional[Session] = None,
    ):
        super().__init__()
        self.session = session or Session()
        self.base_url = base_url

    def do_request(self, request: HttpRequest) -> Any:
        return self.session.request(
            url=urllib.parse.urljoin(self.base_url, request.url),
            method=request.method,
            json=request.body,
            params=request.query_params,
        )
