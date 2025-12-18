from typing import Any, List, Literal, Optional, TypeAlias, Union

from pydantic import BaseModel


class MessageContentText(BaseModel):
    type: Literal["text"] = "text"
    text: str


class MessageContentReasoning(BaseModel):
    type: Literal["reasoning"] = "reasoning"
    reasoning: str


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    name: Optional[str] = None
    content: List[MessageContentText]


class DeveloperMessage(BaseModel):
    role: Literal["developer"] = "developer"
    content: List[MessageContentText]


class SystemMessage(BaseModel):
    role: Literal["system"] = "system"
    content: List[MessageContentText]


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    agent_name: Optional[str] = None
    content: Optional[List[Union[MessageContentText, MessageContentReasoning]]] = None
    tool_calls: Optional[List[ToolCall]] = None


class ToolMessage(BaseModel):
    role: Literal["tool"] = "tool"
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    content: List[MessageContentText]


AgentMessage: TypeAlias = Union[
    UserMessage, DeveloperMessage, SystemMessage, AssistantMessage, ToolMessage
]
