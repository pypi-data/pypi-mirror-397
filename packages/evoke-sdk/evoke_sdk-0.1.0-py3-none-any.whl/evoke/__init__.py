"""
Evoke SDK - AI Detection & Response for Agentic Frameworks

Simple SDK for capturing AI agent events:
- Model calls (OpenAI, Anthropic, etc.) - auto-instrumented
- Tool/function executions - auto-instrumented
- Data source access (databases, APIs, files)
- Agent workflows and reasoning

ONE LINE - that's all you need:

    import evoke
    evoke.init(api_key="evoke_pk_xxx")

    # All model calls and tool executions are now captured automatically!
    response = my_agent.run("What is the weather?")

Security and tracking with @evoke.guard:

    # Basic guard - security monitoring
    @evoke.guard
    def process_request(input: str):
        return agent.run(input)

    # Tool tracking with security
    @evoke.guard(type="tool", category="knowledge_base")
    def search_docs(query: str):
        return search(query)

    # Analyze content directly - SDK makes the safe/unsafe decision
    result = evoke.analyze("Check this content for threats")
    if result.safe:
        proceed_with_action()
    else:
        print(f"Blocked! Severity: {result.severity}")

Identity and context:

    # Set user/org identity for attribution
    evoke.identity(user_id="user_123", org_id="acme", role="analyst")

    # Set custom metadata
    evoke.custom_metadata({"department": "finance", "project": "q4"})

Manual capture (simplified API):

    # Minimal - just a message
    evoke.capture(output="Search completed")

    # With input/output
    evoke.capture(input=query, output=result)

    # Tool call
    evoke.capture(type="tool", name="search", input=query, output=result)
"""

from evoke._version import __version__, SDK_VERSION

# Core initialization and global functions
from evoke.core.client import init, flush, get_system_info

# Session management
from evoke.core.session import (
    session,
    get_current_session,
    end_session,
    identity,
    custom_metadata,
    get_identity,
    get_custom_metadata,
)

# Public functions
from evoke.functions.capture import capture, capture_scope
from evoke.functions import guard, analyze

# Schema (for type hints and manual event creation)
from evoke.schema import (
    Event,
    EventType,
    ModelInfo,
    ToolInfo,
    DataSourceInfo,
    Detection,
    AnalysisResult,
    Identity,
    PolicyConfig,
)

# Detection engine
from evoke.detection import DetectionEngine, get_detection_engine

# Signature sync
from evoke.sync import SignatureManager

__all__ = [
    # Version
    "__version__",
    "SDK_VERSION",
    # Core Functions
    "init",
    "flush",
    "get_system_info",
    # Identity & Context
    "identity",
    "custom_metadata",
    "get_identity",
    "get_custom_metadata",
    # Security & Tracking
    "guard",
    "analyze",
    # Manual Capture
    "capture",
    "capture_scope",
    # Session Management
    "session",
    "get_current_session",
    "end_session",
    # Schema Types
    "Event",
    "EventType",
    "ModelInfo",
    "ToolInfo",
    "DataSourceInfo",
    "Detection",
    "AnalysisResult",
    "Identity",
    "PolicyConfig",
    # Detection
    "DetectionEngine",
    "get_detection_engine",
    # Sync
    "SignatureManager",
]
