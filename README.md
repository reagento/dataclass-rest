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
from dataclass_rest.sync_base import BaseClient

class RealClient(Client):
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
from dataclass_rest.sync_base import Client

class RealClient(Client):
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
        """Созадем Todo"""
```

## Asyncio

To use async client insted of sync:

1. Install `aiohttp` (instead of `reuests`)
2. Change `dataclass_rest.sync_base.Client` to `dataclass_rest.async_base.AsyncClient`
3. Add `async` keyword to your methods 

## Configuring

* Override `_init_factory` or `_init_args_factory` to provide dataclass factory with required settings  
    (see [datacass_factory](https://github.com/Tishka17/dataclass_factory)).
* You can use different body argument name if you want. Just pass `body_name` to the decorator.
* `args_factory` can be configured with scehmas for every argument type.  
    They are awailable as `args_class` of original method. E.g `RealClient.get_todo.args_class`
* Custom error handlers can be set adding them to `error_handlers` using `add_handler` method
 
