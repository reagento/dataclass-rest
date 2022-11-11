import urllib.parse
from typing import Any, Optional

from requests import Session, Response

from ..base_client import BaseClient
from ..boundmethod import SyncMethod
from ..http_request import HttpRequest


class RequestsMethod(SyncMethod):

    def _response_ok(self, response: Response) -> bool:
        return response.ok

    def _response_body(self, response: Response) -> Any:
        return response.json()


class RequestsClient(BaseClient):
    method_class = RequestsMethod

    def __init__(
            self,
            base_url: str,
            session: Optional[Session] = None,
    ):
        super().__init__()
        self.session = session or Session()
        self.base_url = base_url

    def do_request(self, request: HttpRequest) -> Any:
        if request.is_json_request:
            json = request.data
            data = None
        else:
            json = None
            data = request.data
        return self.session.request(
            url=urllib.parse.urljoin(self.base_url, request.url),
            method=request.method,
            json=json,
            params=request.query_params,
            data=data,
        )
