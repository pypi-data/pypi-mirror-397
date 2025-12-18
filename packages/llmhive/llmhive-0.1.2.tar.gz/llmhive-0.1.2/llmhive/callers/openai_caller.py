import base64
import json
from typing import Any, Iterator, cast, override

from ..types.event import ModelFunctionEvent, ModelTextEvent
from ..types.prompt import FunctionDefine, Prompt
from ..model import ModelInfo
from ..caller import Caller, ModelEvent, PromptContext
from ..errors import MissingDependencyError
from ..limiters.rate_limiter import RateLimitConfig, rate_limited

try:
    from openai import OpenAI, Stream
    from openai.types.chat.chat_completion_message_tool_call_param import Function
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionContentPartParam,
        ChatCompletionMessageParam,
        ChatCompletionFunctionToolParam,
        ChatCompletionMessageFunctionToolCall,
        ChatCompletionMessageFunctionToolCallParam,
        ChatCompletionAssistantMessageParam,
    )
    from openai.types.shared_params.function_definition import FunctionDefinition
except ImportError as e:
    raise MissingDependencyError(
        "OpenAICompatibleCaller requires `openai`. Please install it with: pip install llmhive[openai]"
    ) from e


class OpenAICaller(Caller):
    def __init__(
        self,
        model: ModelInfo,
        api_key: str,
        base_url="https://api.openai.com/v1/responses",
        rate_limit_config: RateLimitConfig | None = None,
        extra_body: dict[str, Any] | None = None,
    ):
        super().__init__(model.name, base_url, api_key, rate_limit_config)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        self.extra_body = extra_body

    @override
    @rate_limited
    def call(self, ctx: PromptContext) -> Iterator[ModelEvent]:
        if self.client is None:
            raise ValueError("OpenAIClient is not initialized properly.")
        openai_messages: list[ChatCompletionMessageParam] = [cast(ChatCompletionMessageParam, ctx.get_system_prompt())]
        if ctx.history:
            openai_messages.extend([self._build_message_content(m) for m in ctx.history])
        extra_body = self.extra_body or {}
        tools = self._generate_function_list(ctx.tools) if ctx.tools else []
        extra_body["thinking"] = {"type": "enabled" if ctx.enable_thinking else "disabled"}
        if ctx.extra_body:
            extra_body.update(ctx.extra_body)

        params = {
            "messages": openai_messages,
            "model": self.model,
            "n": 1,
            "stream": ctx.is_stream,
            "extra_body": extra_body,
        }

        if tools:
            params["tools"] = tools

        # print(openai_messages)

        response = self.client.chat.completions.create(**params)

        if ctx.is_stream:
            stream = cast(Stream[ChatCompletionChunk], response)
            for chunk in stream:
                choice = chunk.choices[0]
                delta = choice.delta
                if delta.content:
                    yield ModelTextEvent(content=delta.content)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.id and tc.function and tc.function.name:
                            yield ModelFunctionEvent(
                                call_id=tc.id,
                                name=tc.function.name,
                                arguments=json.loads(tc.function.arguments) if tc.function.arguments else {},
                            )
        else:
            completion = cast(ChatCompletion, response)
            message = completion.choices[0].message
            if message.tool_calls:
                for tc in message.tool_calls:
                    if isinstance(tc, ChatCompletionMessageFunctionToolCall):
                        yield ModelFunctionEvent(
                            call_id=tc.id,
                            name=tc.function.name,
                            arguments=json.loads(tc.function.arguments) if tc.function.arguments else {},
                        )
            if message.content:
                yield ModelTextEvent(content=message.content)

    def _build_message_content(self, prompt: Prompt) -> ChatCompletionMessageParam:
        role = prompt["role"]
        match role:
            case "user":
                content: list[ChatCompletionContentPartParam] = []
                if "images" in prompt:
                    for image_path in prompt.get("images", []):
                        with open(image_path, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                            content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                }
                            )
                content.append({"type": "text", "text": prompt["content"]})
                return {"content": content, "role": "user"}
            case "assistant":
                message = ChatCompletionAssistantMessageParam(role="assistant")
                tool_calls = prompt.get("tool_calls")
                if tool_calls:
                    message["tool_calls"] = [
                        ChatCompletionMessageFunctionToolCallParam(
                            id=t["id"],
                            type=t["type"],
                            function=Function(
                                name=t["function"]["name"], arguments=json.dumps(t["function"]["arguments"])
                            ),
                        )
                        for t in tool_calls
                    ]
                if prompt.get("content"):
                    message["content"] = prompt["content"]
                return message
            case "tool":
                return {
                    "content": prompt["content"],
                    "role": "tool",
                    "tool_call_id": prompt.get("call_id", ""),
                }
            case _:
                raise ValueError(f"Unknown message role: {prompt['role']}")

    def _generate_function_list(self, tools: list[FunctionDefine]) -> list[ChatCompletionFunctionToolParam]:
        func_list = []
        for tool in tools:
            func_info = cast(FunctionDefinition, tool)
            func_list.append(
                {
                    "type": "function",
                    "function": func_info,
                }
            )
        return func_list


class BailianCaller(OpenAICaller):
    TURBO = "qwen-turbo"
    FREE = "qwen2.5-1.5b-instruct"

    def __init__(
        self,
        model: ModelInfo,
        api_key: str,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        super().__init__(
            model,
            api_key,
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
            rate_limit_config,
        )


class HunyuanCaller(OpenAICaller):
    TURBO = "hunyuan-turbo"
    FREE = "hunyuan-lite"

    def __init__(
        self,
        model: ModelInfo,
        api_key: str,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        super().__init__(
            model,
            api_key,
            "https://api.hunyuan.cloud.tencent.com/v1",
            rate_limit_config,
        )


class XinghuoCaller(OpenAICaller):
    FREE = "lite"

    def __init__(
        self,
        model: ModelInfo,
        api_key: str,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        super().__init__(model, api_key, "https://spark-api-open.xf-yun.com/v1", rate_limit_config)


class ModelScopeCaller(OpenAICaller):
    QWEN2_5_CODER_32B = "Qwen/Qwen2.5-Coder-32B-Instruct"
    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3-0324"
    QWEN3_8B = "Qwen/Qwen3-8B"
    QWEN3_14B = "Qwen/Qwen3-14B"

    def __init__(
        self,
        model: ModelInfo,
        api_key: str,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        super().__init__(model, api_key, "https://api-inference.modelscope.cn/v1/", rate_limit_config)


class VolceCaller(OpenAICaller):
    def __init__(
        self,
        model: ModelInfo,
        api_key: str,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        super().__init__(
            model,
            api_key,
            "https://ark.cn-beijing.volces.com/api/v3",
            rate_limit_config,
            {"max_tokens": model.max_output_tokens},
        )
