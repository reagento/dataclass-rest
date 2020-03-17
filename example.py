from dataclasses import dataclass
from typing import List

from requests import Session

from base import BaseClient


@dataclass
class Joke:
    id: int
    type: str
    setup: str
    punchline: str


class RealClient(BaseClient):
    def __init__(self):
        super().__init__("https://official-joke-api.appspot.com/jokes/programming/", Session())

    def random_jokes(self):
        return self.get(url="random", result_class=List[Joke])


print(RealClient().random_jokes())