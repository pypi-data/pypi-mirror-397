from dataclasses import dataclass, field
import os
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Deque, Iterator

from .types.event import ModelEvent
from .types.prompt import FunctionDefine, Prompt, SystemPrompt, ToolPrompt, UserPrompt
from .model import ModelInfo
from .errors import MissingAPIKeyError
from .limiters.rate_limiter import RateLimitConfig


@dataclass
class PromptContext:
    user_prompt: UserPrompt | ToolPrompt | str
    system_prompt: str
    history: list[Prompt] = field(default_factory=list)
    is_stream: bool = False
    is_json: bool = False
    tools: list[FunctionDefine] = field(default_factory=list)
    extra_body: dict[str, Any] | None = None
    enable_thinking: bool = False

    def get_user_prompt(self) -> UserPrompt | ToolPrompt:
        if isinstance(self.user_prompt, str):
            return {"role": "user", "content": self.user_prompt}
        else:
            return self.user_prompt

    def get_system_prompt(self) -> SystemPrompt:
        return {"role": "system", "content": self.system_prompt}


class Caller(ABC):
    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        rate_limit_config: RateLimitConfig | None = None,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        if rate_limit_config:
            self.rate_limit_config = rate_limit_config
            self.call_timestamps: Deque[float] = deque()  # 存储时间戳

    @abstractmethod
    def call(self, ctx: PromptContext) -> Iterator[ModelEvent]: ...


class CallerFactory:
    @classmethod
    def create(cls, model: ModelInfo, rate_limit_config: RateLimitConfig | None = None) -> Caller:
        if rate_limit_config is None:
            rate_limit_config = model.get_rate_limit_config()
        provider = model.provider.lower()
        match provider:
            case "modelscope":
                from .callers.openai_caller import ModelScopeCaller

                api_key = os.getenv("API_KEY_MODELSCOPE")
                if not api_key:
                    raise MissingAPIKeyError(
                        "ModelScopeCaller requires the API key. Please set the API_KEY_MODELSCOPE environment variable."
                    )
                return ModelScopeCaller(model, api_key=api_key, rate_limit_config=rate_limit_config)
            case "ollama":
                from .callers.ollama_caller import OllamaCaller

                return OllamaCaller(model.name)
            case "xunfei":
                from .callers.openai_caller import XinghuoCaller

                api_key = os.getenv("API_KEY_XINGHUO")
                if not api_key:
                    raise MissingAPIKeyError(
                        "XinghuoCaller requires the API key. Please set the API_KEY_XINGHUO environment variable."
                    )
                return XinghuoCaller(model, api_key=api_key, rate_limit_config=rate_limit_config)
            case "dummy":
                from .callers.dummy_caller import DummyCaller

                return DummyCaller()
            case "google":
                from .callers.gemini_caller import GeminiCaller

                api_key = os.getenv("API_KEY_GEMINI")
                if not api_key:
                    raise MissingAPIKeyError(
                        "GeminiCaller requires the API key. Please set the API_KEY_GEMINI environment variable."
                    )
                return GeminiCaller(model.name, api_key=api_key, rate_limit_config=rate_limit_config)
            case "alibaba":
                from .callers.openai_caller import BailianCaller

                api_key = os.getenv("API_KEY_BAILIAN")
                if not api_key:
                    raise MissingAPIKeyError(
                        "BailianCaller requires the API key. Please set the API_KEY_BAILIAN environment variable."
                    )
                return BailianCaller(model, api_key=api_key, rate_limit_config=rate_limit_config)
            case "tencent":
                from .callers.openai_caller import HunyuanCaller

                api_key = os.getenv("API_KEY_HUNYUAN")
                if not api_key:
                    raise MissingAPIKeyError(
                        "HunyuanCaller requires the API key. Please set the API_KEY_HUNYUAN environment variable."
                    )
                return HunyuanCaller(model, api_key=api_key, rate_limit_config=rate_limit_config)
            case "bytedance":
                from .callers.openai_caller import VolceCaller

                api_key = os.getenv("API_KEY_VOLCE")
                if not api_key:
                    raise MissingAPIKeyError(
                        "VolceCaller requires the API key. Please set the API_KEY_VOLCE environment variable."
                    )
                return VolceCaller(model, api_key=api_key, rate_limit_config=rate_limit_config)
            case "openai":
                from .callers.openai_caller import OpenAICaller

                api_key = os.getenv("API_KEY_OPEANAI")
                if not api_key:
                    raise MissingAPIKeyError(
                        "OpenAICaller requires the API key. Please set the API_KEY_OPEANAI environment variable."
                    )
                return OpenAICaller(model, api_key=api_key, rate_limit_config=rate_limit_config)
            case _:
                raise ValueError(f"Unknown model: {model.name}")
