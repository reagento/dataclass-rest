# Dataclass REST

A modern way to create clients for REST like APIs

## Quickstart


Step 1. Install
```bash
pip install dataclass_rest
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
from dataclass_rest import BaseClient

class RealClient(BaseClient):
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
from dataclass_rest import BaseClient, get, post, delete

class RealClient(BaseClient):
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


## Configuring

* Override `_init_factory` or `_init_params_factory` to provide dataclass factory with required settings (see [datacass_factory](https://github.com/Tishka17/dataclass_factory)).
* You can use different body argument name if you want. Just pass `body_name` to the decorator.