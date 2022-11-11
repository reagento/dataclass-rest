from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HttpRequest:
    is_json_request: bool
    data: Any
    query_params: Dict
    url: str
    method: str
