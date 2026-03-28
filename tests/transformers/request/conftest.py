import pytest

from descanso.method_spec import MethodSpec


@pytest.fixture
def spec() -> MethodSpec:
    return MethodSpec(
        name="method",
        result_type=None,
        doc="",
        func=lambda self: None,
    )
