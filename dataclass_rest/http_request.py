from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HttpRequest:
    json_body: Any
    query_params: Dict
    url: str
    method: str
