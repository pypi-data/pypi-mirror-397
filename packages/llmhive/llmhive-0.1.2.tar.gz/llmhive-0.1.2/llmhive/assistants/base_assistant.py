from typing import Any, Iterator, override

from ..assistant import Assistant
from ..caller import CallerFactory, PromptContext
from ..types.prompt import AssistantPrompt, Function, FunctionDefine, Prompt, ToolCall, ToolPrompt, UserPrompt
from ..types.event import ModelEvent, ModelTextEvent
from ..model import ModelInfo


class BaseAssistant(Assistant):
    def __init__(
        self,
        model: ModelInfo,
        system_prompt: str | None = None,
        history: list[dict[str, str]] | None = None,
    ):
        self.history = self._build_history(history)
        self.system_prompt = system_prompt or "You are a helpful assistant."
        self.caller = CallerFactory.create(model)

    def direct_run(
        self,
        prompt: str,
        images: list[str] | None = None,
        is_json=False,
        extra_body: dict[str, Any] | None = None,
    ) -> str:
        result = self.run(prompt=prompt, images=images, is_json=is_json, extra_body=extra_body)
        return "".join(
            chunk.content for chunk in result if isinstance(chunk, ModelTextEvent)
        )


    def simple_run(
        self,
        prompt: str,
        images: list[str] | None = None,
        is_stream=False,
        is_json=False,
        extra_body: dict[str, Any] | None = None,
    ) -> Iterator[str]:
        result = self.run(prompt=prompt, images=images, is_stream=is_stream, is_json=is_json, extra_body=extra_body)
        for chunk in result:
            if isinstance(chunk, ModelTextEvent):
                yield chunk.content


    @override
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
    ) -> Iterator[ModelEvent]:
        if tool_call_id:
            user_prompt = ToolPrompt(role="tool", call_id=tool_call_id, content=prompt)
        elif images:
            user_prompt = UserPrompt(role="user", content=prompt, images=images)
        else:
            user_prompt = UserPrompt(role="user", content=prompt)
        ctx = PromptContext(
            user_prompt=user_prompt,
            system_prompt=self.system_prompt,
            history=self.history,
            is_stream=is_stream,
            is_json=is_json,
            extra_body=extra_body,
            tools=tools,
            enable_thinking=enable_thinking,
        )
        response = self.caller.call(ctx)
        self._add_history(ctx.get_user_prompt())

        def stream_and_record() -> Iterator[ModelEvent]:
            collected: list[str] = []
            tool_calls: list[ToolCall] = []
            try:
                for chunk in response:
                    if isinstance(chunk, ModelTextEvent):
                        collected.append(chunk.content)
                    else:
                        tool_calls.append(
                            ToolCall(
                                id=chunk.call_id,
                                type="function",
                                function=Function(name=chunk.name, arguments=chunk.arguments),
                            )
                        )
                    yield chunk
            finally:
                # 在流关闭时（遍历完或异常中断）执行
                message = AssistantPrompt(role="assistant", content="".join(collected))
                if tool_calls:
                    message["tool_calls"] = tool_calls
                self._add_history(message)

        return stream_and_record()

    def _build_history(self, history: list[dict[str, str]] | None) -> list[Prompt]:
        result = []
        if history:
            for item in history:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    result.append({"role": item["role"], "content": item["content"]})
        return result

    def _add_history(self, prompt: Prompt):
        self.history.append(prompt)
