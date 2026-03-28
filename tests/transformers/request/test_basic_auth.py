import pytest
from kiss_headers import Header as KissHeader
from kiss_headers import Headers

from descanso.fields import (
    FieldDestination,
    FieldIn,
    FieldOut,
)
from descanso.request import (
    HttpRequest,
)
from descanso.transformers.request import BasicAuth
from .utils import consumed_fields


@pytest.mark.parametrize(
    ("transformer", "consumed", "headers", "out"),
    [
        (
            BasicAuth("user", "pass"),
            [],
            Headers(KissHeader("Authorization", "Basic dXNlcjpwYXNz")),
            [FieldOut("Authorization", FieldDestination.HEADER, str)],
        ),
        (
            BasicAuth(login_template="{user}", password_template="{password}"),  # noqa: S106
            ["user", "password"],
            Headers(KissHeader("Authorization", "Basic YWxpY2U6c2VjcmV0")),
            [FieldOut("Authorization", FieldDestination.HEADER, str)],
        ),
        (
            BasicAuth(
                login_template=lambda user: f"{user}_id",
                password_template=lambda password: f"{password}_x",
            ),
            ["user", "password"],
            Headers(
                KissHeader("Authorization", "Basic YWxpY2VfaWQ6c2VjcmV0X3g="),
            ),
            [FieldOut("Authorization", FieldDestination.HEADER, str)],
        ),
    ],
)
def test_basic_auth(spec, transformer, consumed, headers, out):
    fields_in = [FieldIn("user", str), FieldIn("password", str)]
    data_in = {"user": "alice", "password": "secret"}

    fields_out = transformer.transform_fields(spec, fields_in)
    assert str(transformer)
    assert consumed_fields(fields_in, transformer) == consumed
    assert fields_out == out
    req = transformer.transform_request(
        spec,
        HttpRequest(),
        fields_in,
        fields_out,
        data_in,
    )
    assert req == HttpRequest(headers=headers)


def test_basic_auth_non_latin1(spec):
    login = "user\U0001f600"
    password = "päss\U0001f600"  # noqa: S105
    t = BasicAuth(login, password)
    fields_out = t.transform_fields(spec, [])
    req = t.transform_request(spec, HttpRequest(), [], fields_out, {})

    expected = HttpRequest(
        headers=Headers(
            KissHeader("Authorization", "Basic dXNlcvCfmIA6cMOkc3Pwn5iA"),
        ),
    )
    assert req == expected


def test_basic_auth_from_credentials(spec):
    login = "a{}"
    password = "b"  # noqa: S105
    t = BasicAuth.from_credentials(login, password)
    fields_out = t.transform_fields(spec, [])
    req = t.transform_request(spec, HttpRequest(), [], fields_out, {})

    expected = HttpRequest(
        headers=Headers(KissHeader("Authorization", "Basic YXt9OmI=")),
    )
    assert req == expected
