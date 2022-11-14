from inspect import isclass
from typing import Optional, Callable, Type, Dict

from dataclass_factory import Factory, Schema

from .client_protocol import ClientProtocol, ClientMethodProtocol


class BaseClient(ClientProtocol):
    method_class: Optional[Callable] = None

    def __init__(self):
        self.request_body_factory = self._init_request_body_factory()
        self.request_args_factory = self._init_request_args_factory()
        self.response_body_factory = self._init_response_body_factory()

    def _init_request_body_factory(self) -> Factory:
        return Factory()

    def _init_request_args_factory(self, schemas=None) -> Factory:
        return Factory(schemas=self._init_request_args_schemas())

    def _init_response_body_factory(self) -> Factory:
        return self.request_body_factory

    def _init_request_args_schemas(self) -> Dict[Type, Schema]:
        cls = type(self)
        schemas = {}
        for name in dir(cls):
            attr = getattr(cls, name)
            # skip classes but keep our methods
            # which contain information about query params schema
            if isinstance(attr, ClientMethodProtocol) and not isclass(attr):
                schema = attr.get_query_params_schema()
                if schema:  # skip if not set
                    schemas[attr.get_query_params_type()] = schema
        return schemas
