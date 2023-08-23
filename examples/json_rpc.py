import logging
from dataclasses import dataclass
from typing import Any, List
from uuid import uuid4

from adaptix import Retort, name_mapping, NameStyle
from requests import Response

from dataclass_rest import post
from dataclass_rest.exceptions import ApiException
from dataclass_rest.http.requests import RequestsMethod, RequestsClient
from dataclass_rest.http_request import HttpRequest


class JsonRPCError(ApiException):
    pass


def jsonrpc(method: str):
    return post("", additional_params={"jsonrpc_method": method})


class JsonRPCMethod(RequestsMethod):
    def _pre_process_request(self, request: HttpRequest) -> HttpRequest:
        request.is_json_request = True
        request.data = {
            "method": self.method_spec.additional_params["jsonrpc_method"],
            "jsonrpc": "2.0",
            "params": request.data,
            "id": str(uuid4()),
        }
        return request

    def _response_body(self, response: Response) -> Any:
        json_body = super()._response_body(response)
        if error := json_body.get("error"):
            raise JsonRPCError(error)
        return json_body.get("result")


class JsonRPC(RequestsClient):
    method_class = JsonRPCMethod


# client
@dataclass
class Transaction:
    block_hash: str
    block_number: str
    from_: str
    chain_id: str
    transaction_index: str


class MyClient(JsonRPC):
    def __init__(self):
        super().__init__("https://rpc.ankr.com/eth_goerli")

    def _init_request_body_factory(self) -> Retort:
        return Retort(
            debug_path=True,
            strict_coercion=False,
            recipe=[
                name_mapping(name_style=NameStyle.CAMEL),
            ],
        )

    @jsonrpc("eth_getTransactionByHash")
    def get_transaction_by_hash(self, body: List[str]) -> Transaction:
        pass

    @jsonrpc("net_version")
    def net_version(self) -> int:
        pass

    @jsonrpc("eth_blockNumber")
    def eth_block_number(self) -> str:
        pass


logging.basicConfig(level=logging.INFO)
c = MyClient()
transaction = c.get_transaction_by_hash(
    ["0xa072d781efc021514a91ea1972ff14e4b1288060db05dc087ebf01204c30d76b"],
)
print("Transaction: ", transaction)
print("Net version: ", c.net_version())
print("Block number:", c.eth_block_number())
