"""
Evoke Functions - Event capture API

The capture() function is the core way events are recorded manually.
It automatically handles session creation, sequencing, parent tracking,
and collects caller context via inspect.
"""
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager
import inspect
import logging

from evoke.schema import (
    Event,
    EventType,
    ModelInfo,
    ToolInfo,
    InputData,
    OutputData,
    Message,
)
from evoke.core.session import get_or_create_session, get_identity

logger = logging.getLogger(__name__)

# Paths to skip when finding user code (SDK and common libraries)
SKIP_PATHS = [
    '/evoke/',           # Evoke SDK
    '/site-packages/',   # Installed packages
    '/langchain',        # LangChain
    '/openai/',          # OpenAI SDK
    '/anthropic/',       # Anthropic SDK
    '/litellm/',         # LiteLLM
    # Python standard library paths
    '/python3.',         # Linux/macOS Python stdlib
    '/Python.framework/',# macOS Python framework
    '/concurrent/',      # concurrent.futures (thread pools)
    '/threading.',       # threading module
    '/asyncio/',         # asyncio module
    '<frozen',           # Frozen/built-in modules
]

# Event type mapping from string to EventType enum
TYPE_MAPPING = {
    "model": EventType.MODEL_CALL,
    "tool": EventType.TOOL_CALL,
    "user_input": EventType.USER_INPUT,
    "agent_response": EventType.AGENT_RESPONSE,
    "error": EventType.ERROR,
    "data_read": EventType.DATA_READ,
    "data_write": EventType.DATA_WRITE,
}


def get_caller_info(skip_frames: int = 2) -> Dict[str, Any]:
    """
    Get information about the calling context using inspect.

    Walks up the call stack to find the first frame in user code,
    skipping SDK internals and common library paths.
    """
    try:
        frame = inspect.currentframe()

        # Skip initial frames
        for _ in range(skip_frames):
            if frame is not None:
                frame = frame.f_back

        # Walk up the stack until we find user code
        while frame is not None:
            filename = frame.f_code.co_filename

            if not any(skip in filename for skip in SKIP_PATHS):
                info = inspect.getframeinfo(frame)
                return {
                    "caller_function": info.function,
                    "caller_file": info.filename,
                    "caller_line": info.lineno,
                }

            frame = frame.f_back

    except Exception:
        pass

    return {}


def convert_to_input_data(value: Any) -> Optional[InputData]:
    """Convert various input formats to InputData object."""
    if value is None:
        return None
    if isinstance(value, InputData):
        return value
    if isinstance(value, dict):
        messages = None
        if "messages" in value:
            messages = [
                Message(**m) if isinstance(m, dict) else m
                for m in value["messages"]
            ]
        return InputData(
            messages=messages,
            name=value.get("name"),
            arguments=value.get("arguments"),
            query=value.get("query"),
            source=value.get("source"),
            data=value.get("data"),
            content=value.get("content"),
        )
    if isinstance(value, str):
        return InputData(content=value)
    return None


def convert_to_output_data(value: Any) -> Optional[OutputData]:
    """Convert various output formats to OutputData object."""
    if value is None:
        return None
    if isinstance(value, OutputData):
        return value
    if isinstance(value, dict):
        messages = None
        if "messages" in value:
            messages = [
                Message(**m) if isinstance(m, dict) else m
                for m in value["messages"]
            ]
        return OutputData(
            messages=messages,
            result=value.get("result"),
            error=value.get("error"),
            documents=value.get("documents"),
            safe=value.get("safe"),
            count=value.get("count"),
            affected=value.get("affected"),
            content=value.get("content"),
        )
    if isinstance(value, str):
        return OutputData(content=value)
    return None


def resolve_event_type(type_str: str) -> str:
    """Convert type param to EventType value string."""
    if type_str in TYPE_MAPPING:
        return TYPE_MAPPING[type_str].value
    return type_str


def capture(
    input: Optional[Union[str, Dict, InputData]] = None,
    output: Optional[Union[str, Dict, OutputData]] = None,
    type: str = "custom",
    name: Optional[str] = None,
    provider: Optional[str] = None,
    category: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    event_type: Optional[Union[str, EventType]] = None,
    model: Optional[ModelInfo] = None,
    tool: Optional[ToolInfo] = None,
) -> Event:
    """
    Capture an event with simplified API.

    This function automatically:
    - Creates a session if none exists
    - Assigns sequence number
    - Links to parent event
    - Collects caller context (function, file, line)
    - Sends to transport for delivery

    Args:
        input: What went in - str, dict, or InputData
        output: What came out - str, dict, or OutputData
        type: Event type - "model", "tool", "user_input", etc.
        name: Name for the event
        provider: Model provider (for type="model")
        category: Tool category (for type="tool")
        metadata: Internal/system key-value pairs
        custom_metadata: Customer-controlled key-value pairs
        event_type: Alternative way to specify event type
        model: ModelInfo object
        tool: ToolInfo object

    Returns:
        The created Event object
    """
    # Resolve event type
    resolved_type = type
    if event_type is not None:
        if isinstance(event_type, EventType):
            resolved_type = event_type.value
        else:
            resolved_type = event_type

    # Handle model info
    model_info = model
    if model is not None:
        if provider is None:
            provider = model.provider
        if name is None:
            name = model.name
        resolved_type = "model"

    # Handle tool info
    tool_info = tool
    if tool is not None:
        if category is None:
            category = tool.category
        if name is None:
            name = tool.name
        resolved_type = "tool"

    # Convert input/output to structured types
    input_data = convert_to_input_data(input)
    output_data = convert_to_output_data(output)

    # Get or create session
    ctx = get_or_create_session()

    # Get sequence number
    seq = ctx.next_seq()
    parent_seq = ctx.current_parent()

    # Auto-collect caller info
    caller_info = get_caller_info(skip_frames=2)

    # Auto-derive name from caller function if not provided
    event_name = name or caller_info.get("caller_function", "unknown")

    # Resolve event type to string value
    if isinstance(resolved_type, str) and resolved_type in TYPE_MAPPING:
        final_event_type = TYPE_MAPPING[resolved_type].value
    elif isinstance(resolved_type, EventType):
        final_event_type = resolved_type.value
    else:
        final_event_type = resolved_type

    # Build entity objects based on type
    if model_info is None and resolved_type == "model":
        model_info = ModelInfo(
            name=event_name,
            provider=provider or "custom",
        )
    if tool_info is None and resolved_type == "tool":
        tool_info = ToolInfo(
            name=event_name,
            category=category,
        )

    # Build metadata
    event_metadata = {
        **caller_info,
        "event_name": event_name,
        **(metadata or {}),
    }

    # Build custom_metadata
    event_custom_metadata = {
        **ctx.current_custom_metadata(),
        **(custom_metadata or {}),
    }

    # Get current identity
    current_identity = get_identity()

    # Get cached system info
    from evoke.core.system_info import get_cached_system_info
    cached_system_info = get_cached_system_info()

    # Create event
    event = Event.create(
        session_id=ctx.session_id,
        seq=seq,
        event_type=final_event_type,
        parent_seq=parent_seq,
        input=input_data,
        output=output_data,
        model=model_info,
        tool=tool_info,
        metadata=event_metadata,
        custom_metadata=event_custom_metadata,
        identity=current_identity,
        system_info=cached_system_info,
    )

    # Send to transport
    try:
        from evoke.core.transport import get_transport
        transport = get_transport()
        if transport:
            transport.send(event)
    except ImportError:
        logger.debug("Transport not available - event not sent")

    logger.debug(f"Captured event: {final_event_type} seq={seq} parent={parent_seq}")

    return event


@contextmanager
def session_scope():
    """
    Context manager for establishing session context WITHOUT emitting events.

    Use this when you want child events (from auto-instrumentation) to be
    grouped under the same session, but don't want to emit a boundary event.
    """
    ctx = get_or_create_session()
    seq = ctx.next_seq()
    ctx.push_event(seq)

    try:
        yield
    finally:
        ctx.pop_event()


@contextmanager
def capture_scope(
    input: Optional[Union[str, Dict, InputData]] = None,
    type: str = "custom",
    name: Optional[str] = None,
    provider: Optional[str] = None,
    category: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for capturing events with nested children.

    Use this when you want child events to be linked to this event.
    The context manager yields a callback to set the output when done.
    """
    ctx = get_or_create_session()

    seq = ctx.next_seq()
    parent_seq = ctx.current_parent()

    caller_info = get_caller_info(skip_frames=3)
    event_name = name or caller_info.get("caller_function", "unknown")
    event_type = resolve_event_type(type)

    # Build entity objects
    model_info = None
    tool_info = None

    if type == "model":
        model_info = ModelInfo(name=event_name, provider=provider or "custom")
    elif type == "tool":
        tool_info = ToolInfo(name=event_name, category=category)

    # Build metadata
    event_metadata = {
        **caller_info,
        "event_name": event_name,
        **(metadata or {}),
    }

    event_custom_metadata = {
        **ctx.current_custom_metadata(),
        **(custom_metadata or {}),
    }

    current_identity = get_identity()
    input_data = convert_to_input_data(input)

    # Get cached system info
    from evoke.core.system_info import get_cached_system_info
    cached_system_info = get_cached_system_info()

    # Create event
    event = Event.create(
        session_id=ctx.session_id,
        seq=seq,
        event_type=event_type,
        parent_seq=parent_seq,
        input=input_data,
        model=model_info,
        tool=tool_info,
        metadata=event_metadata,
        custom_metadata=event_custom_metadata,
        identity=current_identity,
        system_info=cached_system_info,
    )

    ctx.push_event(seq)

    if custom_metadata:
        ctx.push_custom_metadata(custom_metadata)

    def set_output(output: Union[str, Dict, OutputData]):
        event.output = convert_to_output_data(output)

    try:
        yield set_output
    finally:
        if custom_metadata:
            ctx.pop_custom_metadata()

        ctx.pop_event()

        try:
            from evoke.core.transport import get_transport
            transport = get_transport()
            if transport:
                transport.send(event)
        except ImportError:
            pass

        logger.debug(f"Captured scoped event: {event_type} seq={seq}")
