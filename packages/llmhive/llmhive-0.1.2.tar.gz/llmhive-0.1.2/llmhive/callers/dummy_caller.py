from typing import Iterator, override

from ..caller import Caller, PromptContext


class DummyCaller(Caller):

    @override
    def __init__(self):
        ...

    @override
    def call(self, ctx: PromptContext) -> Iterator[str]:
        yield "dummy"
