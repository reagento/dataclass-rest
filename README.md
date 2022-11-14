# Dataclass REST

[![PyPI version](https://badge.fury.io/py/dataclass-rest.svg)](https://badge.fury.io/py/dataclass-rest)
[![Build Status](https://travis-ci.org/Tishka17/dataclass_rest.svg?branch=master)](https://travis-ci.org/Tishka17/dataclass_rest)

A modern and simple way to create clients for REST like APIs

## Quickstart


Step 1. Install
```bash
pip install dataclass_rest requests
```


Step 2. Declare models

```python
@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool
```

Step 3. Create and configure client

```python

from requests import Session
from dataclass_rest.http.requests import RequestsClient

class RealClient(RequestsClient):
    def __init__(self):
        super().__init__("https://example.com/api", Session())
```

Step 4. Declare methods using `get`/`post`/`delete`/`patch`/`put` decorators. 
Type hints are required. Body of method is ignored.

Use any method arguments to format URL.
`body` argument is sent as request body with json. Other arguments, not used in URL are passed as query parameters.
`get` and `delete` does not have body.

```python
from typing import Optional, List
from requests import Session
from dataclass_rest import get, post, delete
from dataclass_rest.http.requests import RequestsClient

class RealClient(RequestsClient):
    def __init__(self):
        super().__init__("https://example.com/api", Session())

    @get("todos/{id}")
    def get_todo(self, id: str) -> Todo:
        pass

    @get("todos")
    def list_todos(self, user_id: Optional[int]) -> List[Todo]:
        pass

    @delete("todos/{id}")
    def delete_todo(self, id: int):
        pass

    @post("todos")
    def create_todo(self, body: Todo) -> Todo:
        """Создаем Todo"""
```

## Asyncio

To use async client insted of sync:

1. Install `aiohttp` (instead of `reuests`)
2. Change `dataclass_rest.http.requests.RequestsClient` to `dataclass_rest.http.aiohttp.AiohttpClient`
3. Add `async` keyword to your methods 

## Configuring

* Override `__init_request_body_factory`, `__init_request_args_factory` and _`init_response_body_factory` 
  to provide dataclass factory with required settings  
  (see [datacass_factory](https://github.com/Tishka17/dataclass_factory)).
* You can use different body argument name if you want. Just pass `body_name` to the decorator.
* `request_args_factory` can be configured with scehmas for every argument type.  
    They are awailable as `methodspec.query_params_type` of original method. 
    E.g `RealClient.get_todo.methodspec.query_params_type`
* Custom error handlers can be set using `@youemthod.on_error` decorator in your class
