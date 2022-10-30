from typing import Any

from requests import Session

from .base_client import BaseClient


class Client(BaseClient):
    def __init__(
            self, base_url: str, session: Session,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session

    def request(
            self,
            url: str,
            method: str,
            body: Any,
            params: Any,
    ) -> Any:
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=body,
        )
        response.raise_for_status()

