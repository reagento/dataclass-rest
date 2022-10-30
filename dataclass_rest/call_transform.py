from inspect import getcallargs
from typing import Any, Tuple, Dict

from .base_client import ClientProtocol
from .method import Method, Args


def transform_call(
        client: ClientProtocol,
        method: Method,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
) -> Args:
    params = getcallargs(method.func, client, *args, **kwargs)
    url = method.url_template.format(**params)
    body = params.get(method.body_param_name)
    serialized_params = client.request_args_factory.dump(
        params, method.query_params_type,
    )
    serialized_body = client.request_body_factory.dump(
        body, method.body_type,
    )
    return Args(
        query_params=serialized_params,
        body=serialized_body,
        url=url,
        additional_params=method.additional_params,
    )


def transform_result(
        client: ClientProtocol,
        method: Method,
        result: Any,
) -> Any:
    return client.response_body_factory.load(
        result, method.response_type,
    )
