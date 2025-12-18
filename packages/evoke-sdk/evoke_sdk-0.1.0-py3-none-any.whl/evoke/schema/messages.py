"""
Evoke Schema - Message structures for model conversations
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from evoke.schema.detection import Detection


@dataclass
class ToolCall:
    """
    Tool/function call within a message.
    Follows OpenAI ChatCompletionMessageToolCall structure.
    """
    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    type: str = "function"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "arguments": self.arguments,
            "type": self.type,
        }


@dataclass
class Message:
    """
    A single message in a conversation.
    Follows OpenAI ChatCompletionMessage / OpenTelemetry gen_ai.input.messages structure.
    """
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"role": self.role}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = [
                tc.to_dict() if hasattr(tc, 'to_dict') else tc
                for tc in self.tool_calls
            ]
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            result["name"] = self.name
        return result


@dataclass
class InputData:
    """
    Structured input data for events.
    Structure varies by event_type - use appropriate fields.
    """
    # For model calls - conversation history
    messages: Optional[List[Message]] = None

    # For tool calls
    name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None

    # For data operations
    query: Optional[str] = None
    source: Optional[str] = None
    data: Optional[Any] = None

    # For analysis and simple content
    content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.messages:
            result["messages"] = [m.to_dict() for m in self.messages]
        if self.name is not None:
            result["name"] = self.name
        if self.arguments is not None:
            result["arguments"] = self.arguments
        if self.query is not None:
            result["query"] = self.query
        if self.source is not None:
            result["source"] = self.source
        if self.data is not None:
            result["data"] = self.data
        if self.content is not None:
            result["content"] = self.content
        return result


@dataclass
class OutputData:
    """
    Structured output data for events.
    Structure varies by event_type - use appropriate fields.
    """
    # For model calls - response message(s)
    messages: Optional[List[Message]] = None

    # For tool calls
    result: Optional[Any] = None
    error: Optional[str] = None

    # For retrieval
    documents: Optional[List[Dict[str, Any]]] = None

    # For content analysis
    safe: Optional[bool] = None
    detections: Optional[List["Detection"]] = None

    # For data operations
    count: Optional[int] = None
    affected: Optional[int] = None

    # For simple content output
    content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.messages:
            result["messages"] = [m.to_dict() for m in self.messages]
        if self.result is not None:
            result["result"] = self.result
        if self.error is not None:
            result["error"] = self.error
        if self.documents is not None:
            result["documents"] = self.documents
        if self.safe is not None:
            result["safe"] = self.safe
        if self.detections:
            result["detections"] = [d.to_dict() for d in self.detections]
        if self.count is not None:
            result["count"] = self.count
        if self.affected is not None:
            result["affected"] = self.affected
        if self.content is not None:
            result["content"] = self.content
        return result
