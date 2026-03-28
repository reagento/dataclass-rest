import inspect
from collections.abc import Callable, Sequence
from typing import Any, get_type_hints

from .method_pipeline import MethodPipeline
from .method_spec import MethodSpec
from .request import FieldIn, FieldOut, RequestTransformer
from .response import ResponseTransformer


def get_func_fields(func: Callable, *, is_in_class) -> list[FieldIn]:
    signature = inspect.signature(func)
    hints = get_type_hints(func)
    fields = [
        FieldIn(
            name=arg.name,
            type_hint=hints.get(arg.name, Any),
            consumed_by=[],
        )
        for arg in signature.parameters.values()
    ]
    if is_in_class:
        del fields[0]
    return fields


def get_result_type(func: Callable) -> Any:
    hints = get_type_hints(func)
    return hints.get("return", Any)


def make_method_pipeline(
    func: Callable,
    *,
    transformers: Sequence[RequestTransformer | ResponseTransformer],
    is_in_class: bool,
) -> MethodPipeline:
    spec = MethodSpec(
        func=func,
        name=func.__name__,
        doc=func.__doc__,
        result_type=get_result_type(func),
    )
    fields_in = get_func_fields(func, is_in_class=is_in_class)
    fields_out: list[FieldOut] = []
    for tr in transformers:
        fields_out.extend(tr.transform_fields(spec, fields_in))

    return MethodPipeline(
        name=spec.name,
        doc=spec.doc,
        result_type=spec.result_type,
        func=spec.func,
        fields_in=fields_in,
        fields_out=fields_out,
        request_transformers=[
            tr for tr in transformers if isinstance(tr, RequestTransformer)
        ],
        response_transformers=[
            tr for tr in transformers if isinstance(tr, ResponseTransformer)
        ],
    )
