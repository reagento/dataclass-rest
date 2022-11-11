from dataclasses import dataclass
from typing import Any, Dict, Union, IO, Optional


@dataclass
class File:
    contents: Union[str, IO, None]
    content_type: Optional[str] = None
    filename: str = None


@dataclass
class HttpRequest:
    is_json_request: bool
    data: Any
    files: Dict[str, File]
    query_params: Dict
    url: str
    method: str
