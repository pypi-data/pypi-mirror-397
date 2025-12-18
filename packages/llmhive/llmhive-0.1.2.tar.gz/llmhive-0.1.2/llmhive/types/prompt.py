from typing import Any, Literal, NotRequired, TypedDict


class FunctionDefine(TypedDict):
    """函数定义"""
    name: str
    description: str
    parameters: NotRequired[dict[str, Any]]


class ToolDefine(TypedDict):
    """工具定义"""
    type: Literal["function"]
    function: FunctionDefine


class Function(TypedDict):
    name: str
    arguments: dict[str, Any]


class ToolCall(TypedDict):
    """模型发起的函数调用"""
    id: str
    type: Literal["function"]
    function: Function


class UserPrompt(TypedDict):
    role: Literal["user"]
    content: str
    images: NotRequired[list[str]]


class SystemPrompt(TypedDict):
    role: Literal["system"]
    content: str


class AssistantPrompt(TypedDict):
    role: Literal["assistant"]
    content: str
    tool_calls: NotRequired[list[ToolCall]]


class ToolPrompt(TypedDict):
    role: Literal["tool"]
    call_id: str
    content: str
    name: NotRequired[str]


Prompt = UserPrompt | SystemPrompt | AssistantPrompt | ToolPrompt
