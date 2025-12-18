from typing import Any, Iterator, Protocol

from .types.event import ModelEvent
from .types.prompt import FunctionDefine


class Assistant(Protocol):
    def run(
        self,
        prompt: str,
        images: list[str] | None = None,
        is_stream=False,
        is_json=False,
        enable_thinking: bool = False,
        extra_body: dict[str, Any] | None = None,
        tools: list[FunctionDefine] = [],
        tool_call_id: str | None = None,
    ) -> Iterator[ModelEvent]: ...
