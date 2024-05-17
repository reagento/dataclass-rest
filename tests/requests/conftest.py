import pytest
import requests_mock

from dataclass_rest.http import requests

@pytest.fixture
def session():
    return requests.Session()


@pytest.fixture
def mocker(session):
    with requests_mock.Mocker(session=session, case_sensitive=True) as session_mock:
        yield session_mock
