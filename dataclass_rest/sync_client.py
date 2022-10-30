from typing import Any

from requests import Session

from .base_client import BaseClient


class Client(BaseClient):
    def __init__(self, base_url: str, session: Session):
        super().__init__()
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
            url=f"{self.base_url}/{url}",
            params=params,
            json=body,
        )
        response.raise_for_status()
        return response.json()