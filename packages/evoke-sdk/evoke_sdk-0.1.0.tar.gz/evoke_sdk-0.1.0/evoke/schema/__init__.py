"""
Evoke Schema - Core data structures for event-driven telemetry
"""
from evoke.schema.events import Event, EventType
from evoke.schema.entities import ModelInfo, ToolInfo, DataSourceInfo
from evoke.schema.messages import Message, ToolCall, InputData, OutputData
from evoke.schema.detection import Detection, AnalysisResult
from evoke.schema.identity import Identity, PolicyConfig
from evoke.schema.system_info import SystemInfo, ContainerInfo
from evoke.schema.policy import PolicyMatch

__all__ = [
    # Events
    "Event",
    "EventType",
    # Entities
    "ModelInfo",
    "ToolInfo",
    "DataSourceInfo",
    # Messages
    "Message",
    "ToolCall",
    "InputData",
    "OutputData",
    # Detection
    "Detection",
    "AnalysisResult",
    # Identity
    "Identity",
    "PolicyConfig",
    # System Info
    "SystemInfo",
    "ContainerInfo",
    # Policy
    "PolicyMatch",
]
