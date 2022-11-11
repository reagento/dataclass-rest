import urllib.parse
from typing import Any, Optional, Tuple

from requests import Session, Response

from ..base_client import BaseClient
from ..boundmethod import SyncMethod
from ..http_request import HttpRequest, File


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

    def _prepare_file(self, fieldname: str, file: File) -> Tuple:
        return (file.filename or fieldname, file.contents, file.content_type)

    def do_request(self, request: HttpRequest) -> Any:
        if request.is_json_request:
            json = request.data
            data = None
        else:
            json = None
            data = request.data

        files = {
            name: self._prepare_file(name, file)
            for name, file in request.files.items()
        }

        return self.session.request(
            url=urllib.parse.urljoin(self.base_url, request.url),
            method=request.method,
            json=json,
            params=request.query_params,
            data=data,
            files=files,
        )
