from dataclasses import dataclass
from typing import Any


@dataclass
class ModelTextEvent:
    """模型生成的普通文本"""
    content: str


@dataclass
class ModelFunctionEvent:
    """模型发起的函数调用"""
    call_id: str
    name: str
    arguments: dict[str, Any]


ModelEvent = ModelTextEvent | ModelFunctionEvent
