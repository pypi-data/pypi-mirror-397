"""
Evoke Schema - Event types and core event structures
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from evoke.schema.identity import Identity
    from evoke.schema.detection import Detection
    from evoke.schema.entities import ModelInfo, ToolInfo, DataSourceInfo
    from evoke.schema.messages import Message, InputData, OutputData
    from evoke.schema.system_info import SystemInfo


class EventType(str, Enum):
    """Types of events captured by the SDK"""
    USER_INPUT = "user_input"
    MODEL_CALL = "model_call"
    AGENT_PLANNING = "agent_planning"
    AGENT_SYNTHESIZING = "agent_synthesizing"
    TOOL_CALL = "tool_call"
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    RETRIEVAL = "retrieval"
    AGENT_RESPONSE = "agent_response"
    AGENT_HANDOFF = "agent_handoff"
    ERROR = "error"
    CONTENT_ANALYSIS = "content_analysis"


@dataclass
class Event:
    """
    A single event in an agent's execution.
    Events form a tree via parent_seq for process flow tracking.
    """
    # Identity & Sequencing
    session_id: str
    seq: int
    parent_seq: Optional[int]
    timestamp: datetime

    # Event Type
    event_type: str

    # Structured Content
    input: Optional["InputData"] = None
    output: Optional["OutputData"] = None

    # Entity References
    model: Optional["ModelInfo"] = None
    tool: Optional["ToolInfo"] = None
    data_source: Optional["DataSourceInfo"] = None

    # Additional Context
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    # Detection Results
    detections: Optional[List["Detection"]] = None

    # Identity (who triggered this event)
    identity: Optional["Identity"] = None

    # System info (where the event originated)
    system_info: Optional["SystemInfo"] = None

    @staticmethod
    def create(
        session_id: str,
        seq: int,
        event_type: str,
        parent_seq: Optional[int] = None,
        **kwargs
    ) -> "Event":
        """Factory method to create an event with auto-generated timestamp"""
        return Event(
            session_id=session_id,
            seq=seq,
            parent_seq=parent_seq,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "session_id": self.session_id,
            "seq": self.seq,
            "parent_seq": self.parent_seq,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "metadata": self.metadata,
            "custom_metadata": self.custom_metadata,
        }

        if self.input:
            result["input"] = self.input.to_dict()
        if self.output:
            result["output"] = self.output.to_dict()
        if self.model:
            result["model"] = self.model.to_dict()
        if self.tool:
            result["tool"] = self.tool.to_dict()
        if self.data_source:
            result["data_source"] = self.data_source.to_dict()
        if self.detections:
            result["detections"] = [d.to_dict() for d in self.detections]
        if self.identity:
            result["identity"] = self.identity.to_dict()
        if self.system_info:
            result["system_info"] = self.system_info.to_dict()

        return result
