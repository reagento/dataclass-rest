import logging
from typing import Optional
from dataclasses import dataclass


from dataclass_rest.json_rpc import JSONRPCClient, JSONQuery, get
from requests import Session
from dataclass_factory import Factory


@dataclass
class MyJSONQuery(JSONQuery):
    auth: Optional[str] = None


@dataclass
class LoginR:
    token: str


@dataclass
class LoginB:
    user: str
    password: str


class RealClient(JSONRPCClient):
    def __init__(self):
        super().__init__("http://10.0.1.80/api_jsonrpc.php", Session())

    def _init_factory(self):
        return Factory()

    def _init_json_query(self):
        return MyJSONQuery

    @get("user.login")
    def user_login(self, body: LoginB) -> LoginR:
        pass


logging.basicConfig(level=logging.DEBUG)
client = RealClient()
print(client.user_login(LoginB(user="admin", password="admin")))