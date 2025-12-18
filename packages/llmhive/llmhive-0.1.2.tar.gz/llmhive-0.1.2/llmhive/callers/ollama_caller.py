import base64
from typing import Any, Iterator, cast, override

from ..limiters.rate_limiter import rate_limited
from ..caller import Caller, ModelEvent, PromptContext
from ..message import Message
from ..errors import MissingDependencyError

try:
    from ollama import chat
    from ollama import ChatResponse
except ImportError as e:
    raise MissingDependencyError(
        "OllamaCaller requires `ollama`. Please install it with: pip install llmhive[ollama]"
    ) from e


class OllamaCaller(Caller):
    QWEN_3_1_7B = "qwen3:1.7b"
    QWEN_3_8B = "qwen3:8b"
    QWEN_2_5_7B = "qwen2.5:7b"
    GEMMA_12B = "gemma3:12b"
    SOLAR_7B = "solar10:7b"
    DEEPSEEK_R1_14B = "deepseek-r1:14b"
    MINICPM_8B = "minicpm-v:8b"

    @override
    @rate_limited
    def call(self, ctx: PromptContext) -> Iterator[ModelEvent]:
        ollama_messages: list[dict[str, Any]] = []
        ollama_messages.append(self._build_message_content(ctx.get_system_prompt()))
        if ctx.history:
            ollama_messages.extend([self._build_message_content(message) for message in ctx.history])
        ollama_messages.append(self._build_message_content(ctx.get_user_prompt()))
        response = chat(
            model=self.model,
            messages=ollama_messages,
            options={
                "num_ctx": 32768,
            },
            stream=ctx.is_stream,
        )
        if ctx.is_stream:
            stream = cast(Iterator[ChatResponse], response)
            for chunk in stream:
                data = chunk.message.content
                if data:
                    yield data
        else:
            completion = cast(ChatResponse, response)
            yield completion.message.content or ""

    def _build_message_content(self, message: Message) -> dict[str, Any]:
        if message.images:
            images = []
            for image_path in message.images:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                    images.append(base64_image)
            return {"role": message.role, "content": message.content, "images": images}
        return {"role": message.role, "content": message.content}
