from typing import Optional, Dict, Any

from .parse_func import DEFAULT_BODY_PARAM
from .rest import rest


def get(
        url_template: str,
        *,
        additional_params: Optional[Dict[str, Any]] = None,
):
    return rest(
        url_template,
        method="GET",
        additional_params=additional_params
    )


def delete(
        url_template: str,
        *,
        additional_params: Optional[Dict[str, Any]] = None,
):
    return rest(
        url_template,
        method="DELETE",
        additional_params=additional_params,
    )


def patch(
        url_template: str, *,
        additional_params: Optional[Dict[str, Any]] = None,
        body_name: str = DEFAULT_BODY_PARAM,
):
    return rest(
        url_template,
        method="PATCH",
        body_name=body_name,
        additional_params=additional_params,
    )


def put(
        url_template: str,
        *,
        additional_params: Optional[Dict[str, Any]] = None,
        body_name: str = DEFAULT_BODY_PARAM,
):
    return rest(
        url_template,
        method="PUT",
        body_name=body_name,
        additional_params=additional_params,
    )


def post(
        url_template: str,
        *,
        additional_params: Optional[Dict[str, Any]] = None,
        body_name: str = DEFAULT_BODY_PARAM,
):
    return rest(
        url_template,
        method="POST",
        body_name=body_name,
        additional_params=additional_params,
    )
