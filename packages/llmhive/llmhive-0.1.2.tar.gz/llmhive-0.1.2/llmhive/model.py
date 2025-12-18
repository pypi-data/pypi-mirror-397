from dataclasses import dataclass

from .limiters.rate_limiter import RateLimitConfig


@dataclass(frozen=True)
class ModelInfo:
    name: str
    provider: str
    max_input_tokens: int = 0
    max_output_tokens: int = 0
    rpm: int = 0  # requests per minute
    tpmin: int = 0  # tokens per minute

    def get_rate_limit_config(self) -> RateLimitConfig | None:
        if self.rpm == 0:
            return None
        return RateLimitConfig(max_calls=self.rpm, time_window=60)


class OpenAI:
    GPT_3_5_TURBO = ModelInfo(name="gpt-3.5-turbo", provider="openai")
    GPT_4 = ModelInfo(name="gpt-4", provider="openai")
    GPT_4O = ModelInfo(name="gpt-4o", provider="openai")
    GPT_4_TURBO = ModelInfo(name="gpt-4-turbo", provider="openai")


class Gemini:
    GEMINI_2_5_FLASH = ModelInfo(name="gemini-2.5-flash", provider="google", max_input_tokens=1048576, max_output_tokens=65536)
    GEMINI_2_0_FLASH = ModelInfo(name="gemini-2.0-flash", provider="google", max_input_tokens=1048576, max_output_tokens=8192)


class ModelScope:
    QWEN_3_VL_235B_A22B_INSTRUCT = ModelInfo(name="Qwen/Qwen3-VL-235B-A22B-Instruct", provider="modelscope", max_output_tokens=32000)
    QWEN_3_NEXT_80B_A3B_INSTRUCT = ModelInfo(name="Qwen/Qwen3-Next-80B-A3B-Instruct", provider="modelscope", max_output_tokens=32000)


class Volce:
    DOUBAO_SEED_1_6 = ModelInfo(name="doubao-seed-1-6-250615", provider="bytedance", max_input_tokens=224000, max_output_tokens=32000, rpm=30000)
    DOUBAO_SEED_1_6_FLASH = ModelInfo(name="doubao-seed-1-6-flash-250828", provider="bytedance", max_input_tokens=224000, max_output_tokens=32000, rpm=30000)
    DOUBAO_SEED_1_6_VISION = ModelInfo(name="doubao-seed-1-6-vision-250815", provider="bytedance", max_input_tokens=224000, max_output_tokens=4000, rpm=30000)


class Model:
    OPENAI = OpenAI
    GEMINI = Gemini
    VOLCE = Volce
    MODELSCOPE = ModelScope

    @classmethod
    def of(cls, name: str, provider: str | None = None) -> ModelInfo:
        for provider_name, provider_cls in vars(cls).items():
            # 过滤掉非 ProviderClass 的属性，例如 __module__, __doc__ 等。
            if not isinstance(provider_cls, type):
                continue
            if provider and provider_name.lower() != provider.lower():
                continue
            for model_name, model_cls in vars(provider_cls).items():
                if not isinstance(model_cls, ModelInfo):
                    continue
                if name.lower() != model_cls.name.lower():
                    continue
                return model_cls
        raise ValueError(f"Model not found for name='{name}' provider='{provider}'")
