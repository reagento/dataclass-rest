from typing import Callable

from .boundmethod import BoundMethod
from .methodspec import MethodSpec


class Method:
    def __init__(
            self,
            method_spec: MethodSpec,
            method_class: Callable[..., BoundMethod],
    ):
        self.method_spec = method_spec
        self.method_class = method_class

    def __get__(self, instance, objtype=None) -> BoundMethod:
        return self.method_class(
            method_spec=self.method_spec,
            client=instance,
            on_error=self.on_error,
        )

    def on_error(self, func) -> "Method":
        self.on_error = func
        return self
