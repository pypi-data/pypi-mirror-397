from typing import Iterator, cast, override

from ..types.event import ModelFunctionEvent, ModelTextEvent
from ..types.prompt import FunctionDefine, Prompt, ToolCall
from ..caller import Caller, ModelEvent, PromptContext
from ..errors import MissingDependencyError
from ..limiters.rate_limiter import RateLimitConfig, rate_limited

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    raise MissingDependencyError(
        "GeminiCaller requires `google-genai`. Please install it with: pip install llmhive[gemini]"
    ) from e


class GeminiCaller(Caller):
    def __init__(
        self,
        model: str,
        api_key: str,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        super().__init__(model, api_key=api_key, rate_limit_config=rate_limit_config)
        self.client = genai.Client(api_key=api_key)

    @override
    @rate_limited
    def call(self, ctx: PromptContext) -> Iterator[ModelEvent]:
        system_prompt = ctx.system_prompt
        user_prompt = ctx.get_user_prompt()
        tools = self._generate_function_list(ctx.tools) if ctx.tools else None
        thinking_config = (
            types.ThinkingConfig(thinking_budget=-1) if ctx.enable_thinking else types.ThinkingConfig(thinking_budget=0)
        )
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json" if ctx.is_json else None,
            tools=tools,
            thinking_config=thinking_config,
        )
        params = {
            "model": self.model,
            "config": config,
        }
        if ctx.history:
            params["history"] = self._build_gemini_history(ctx.history)
        # print(f"Gemini Caller Params: {params["history"]}")
        chat = self.client.chats.create(**params)
        gemini_messages = self._build_user_message_part(user_prompt["content"], user_prompt.get("images"))
        # print(f"Sending message to Gemini: {gemini_messages}")
        if ctx.is_stream:
            for chunk in chat.send_message_stream(message=gemini_messages):
                if chunk.function_calls:
                    for fn in chunk.function_calls:
                        if fn.name:
                            yield ModelFunctionEvent(
                                call_id=fn.id or "",
                                name=fn.name,
                                arguments=fn.args if fn.args else {},
                            )
                if chunk.text:
                    yield ModelTextEvent(content=chunk.text)
        else:
            response = chat.send_message(message=gemini_messages)
            # print(response.function_calls)
            # print(response.text)
            # print(response.parts)
            if response.function_calls:
                for fn in response.function_calls:
                    if fn.name:
                        yield ModelFunctionEvent(
                            call_id=fn.id or "",
                            name=fn.name,
                            arguments=fn.args if fn.args else {},
                        )
            else:
                yield ModelTextEvent(content=response.text or "")

    def _build_message_content(self, prompt: Prompt) -> types.Content:
        role = prompt["role"]
        match role:
            case "user":
                parts = self._build_user_message_part(prompt["content"], prompt.get("images"))
                new_role = "user"
            case "tool":
                parts = self._build_tool_message_part(prompt["content"])
                new_role = "user"
            case "assistant":
                parts = self._build_assistant_message_part(prompt["content"], prompt.get("tool_calls"))
                new_role = "model"
            case _:
                raise ValueError(f"Unknown message role: {prompt['role']}")
        return types.Content(
            role=new_role,
            parts=parts,
        )

    def _build_gemini_history(self, messages: list[Prompt]) -> list[types.Content]:
        return [self._build_message_content(message) for message in messages]

    def _build_user_message_part(self, content: str, images: list[str] | None = None) -> list[types.Part]:
        if images:
            image_url = images[0]
            with open(image_url, "rb") as f:
                image_bytes = f.read()
            return [
                types.Part(text=content),
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            ]
        return [types.Part(text=content)]

    def _build_tool_message_part(self, content: str, name: str | None = "tool") -> list[types.Part]:
        return [
            types.Part.from_function_response(
                name=name or "tool",
                response={"result": content},
            )
        ]

    def _build_assistant_message_part(
        self, content: str | None = None, tool_calls: list[ToolCall] | None = None
    ) -> list[types.Part]:
        r = []
        if content:
            r.append(types.Part(text=content))
        if tool_calls:
            for call in tool_calls:
                name = call["function"]["name"]
                arguments = call["function"]["arguments"]
                r.append(
                    types.Part.from_function_call(
                        name=name,
                        args=arguments,
                    )
                )
        return r

    def _generate_function_list(self, tools: list[FunctionDefine]) -> list[types.Tool]:
        func_list = []
        for tool in tools:
            func_info = cast(types.FunctionDeclaration, tool)
            func_list.append(func_info)
        return [types.Tool(function_declarations=func_list)]
