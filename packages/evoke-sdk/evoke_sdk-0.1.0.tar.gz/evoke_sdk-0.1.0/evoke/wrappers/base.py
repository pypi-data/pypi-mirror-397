"""
Base Instrumentor - Event-Driven Instrumentation Framework

Provides base class for instrumenting model SDKs and frameworks.
Instrumentors emit Events (not OpenTelemetry spans) for detection and analysis.
"""
from abc import ABC, abstractmethod
from typing import Collection, Optional, Dict, Any, List
import logging

from evoke.schema import ModelInfo, ToolInfo, EventType

logger = logging.getLogger(__name__)


class BaseInstrumentor(ABC):
    """
    Base class for Evoke instrumentors.

    Subclasses should:
    1. Implement instrumentation_dependencies() to list required packages
    2. Implement _instrument() to wrap target methods
    3. Implement _uninstrument() to unwrap methods
    4. Use capture_model_event() and capture_tool_event() helpers to emit events
    """

    def __init__(self):
        self._instrumented = False

    @abstractmethod
    def instrumentation_dependencies(self) -> Collection[str]:
        """
        Return a list of python packages that this instrumentor depends on.

        Example: ["openai >= 1.0.0"]
        """
        pass

    @abstractmethod
    def _instrument(self, **kwargs):
        """
        Instrument the library.

        This method should use wrapt.wrap_function_wrapper to wrap the target methods.
        """
        pass

    @abstractmethod
    def _uninstrument(self, **kwargs):
        """
        Uninstrument the library.

        This method should unwrap any wrapped functions.
        """
        pass

    def instrument(self, **kwargs):
        """
        Public method to instrument the library.
        """
        if self._instrumented:
            logger.warning(f"{self.__class__.__name__} already instrumented")
            return

        self._instrument(**kwargs)
        self._instrumented = True
        logger.debug(f"{self.__class__.__name__} instrumented")

    def uninstrument(self, **kwargs):
        """
        Public method to uninstrument the library.
        """
        if not self._instrumented:
            logger.warning(f"{self.__class__.__name__} not instrumented")
            return

        self._uninstrument(**kwargs)
        self._instrumented = False
        logger.debug(f"{self.__class__.__name__} uninstrumented")

    # === Helper Methods for Detecting Agent Phase ===

    @staticmethod
    def detect_agent_phase(
        finish_reason: Optional[str],
        has_tool_calls: bool,
        messages: Optional[list] = None,
    ) -> EventType:
        """
        Detect the agent phase based on model response characteristics.

        Args:
            finish_reason: The finish_reason from model response (e.g., "stop", "tool_calls")
            has_tool_calls: Whether the response contains tool calls
            messages: The input messages (to check for tool results)

        Returns:
            EventType: AGENT_PLANNING, AGENT_SYNTHESIZING, or MODEL_CALL
        """
        # If the model is selecting tools, it's in planning phase
        if finish_reason == "tool_calls" or has_tool_calls:
            return EventType.AGENT_PLANNING

        # If there are tool results in the input messages, it's synthesizing
        if messages and BaseInstrumentor._has_tool_results_in_messages(messages):
            return EventType.AGENT_SYNTHESIZING

        # Otherwise, it's a direct model call (no agent context)
        return EventType.MODEL_CALL

    @staticmethod
    def _has_tool_results_in_messages(messages: list) -> bool:
        """
        Check if any messages contain tool results.

        This indicates the model is processing the output of a previous tool call,
        which means it's in the "synthesizing" phase.
        """
        if not messages:
            return False

        for msg in messages:
            # Handle dict-style messages
            if isinstance(msg, dict):
                role = msg.get("role", "")
                if role == "tool":
                    return True
                # Also check for tool_call_id which indicates tool response
                if msg.get("tool_call_id"):
                    return True
            # Handle object-style messages
            elif hasattr(msg, "role"):
                if getattr(msg, "role", None) == "tool":
                    return True
                if hasattr(msg, "tool_call_id") and msg.tool_call_id:
                    return True

        return False

    # === Helper Methods for Emitting Events ===

    @staticmethod
    def capture_model_event(
        input_messages: list,
        output_messages: list,
        model_name: str,
        provider: str,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_type: Optional[EventType] = None,
    ):
        """
        Capture a model call event with structured messages.

        Args:
            input_messages: List of input message dicts [{role, content, ...}]
            output_messages: List of output message dicts [{role, content, ...}]
            model_name: Name of the model (gpt-4, claude-3-opus, etc.)
            provider: Provider name (openai, anthropic, etc.)
            tokens_in: Input token count
            tokens_out: Output token count
            metadata: Additional metadata
            event_type: Override event type (AGENT_PLANNING, AGENT_SYNTHESIZING, or MODEL_CALL)
        """
        from evoke.functions.capture import capture

        model_info = ModelInfo(
            name=model_name,
            provider=provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )

        # Default to MODEL_CALL if not specified
        if event_type is None:
            event_type = EventType.MODEL_CALL

        return capture(
            event_type=event_type,
            input={"messages": input_messages},
            output={"messages": output_messages},
            model=model_info,
            metadata=metadata,
        )

    @staticmethod
    def capture_tool_event(
        tool_name: str,
        tool_input: Any,
        tool_output: Any = None,
        category: Optional[str] = None,
        is_external: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Capture a tool call event with structured input/output.

        Args:
            tool_name: Name of the tool
            tool_input: Tool arguments (dict or any serializable object)
            tool_output: Tool result (any serializable object)
            category: Tool category (action, knowledge_base, connector)
            is_external: Whether tool calls external APIs
            metadata: Additional metadata
        """
        from evoke.functions.capture import capture

        tool_info = ToolInfo(
            name=tool_name,
            category=category,
            is_external=is_external,
        )

        # Build structured input
        input_data = {"name": tool_name, "arguments": tool_input}

        # Build structured output
        output_data = None
        if tool_output is not None:
            if isinstance(tool_output, Exception):
                output_data = {"error": str(tool_output)}
            else:
                output_data = {"result": tool_output}

        return capture(
            event_type=EventType.TOOL_CALL,
            input=input_data,
            output=output_data,
            tool=tool_info,
            metadata=metadata,
        )

    @staticmethod
    def capture_error_event(
        error_message: str,
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Capture an error event.

        Args:
            error_message: The error message
            error_type: Type of error (exception class name)
            metadata: Additional metadata
        """
        from evoke.functions.capture import capture

        error_metadata = metadata or {}
        if error_type:
            error_metadata["error_type"] = error_type

        return capture(
            type="error",
            output=error_message,
            metadata=error_metadata,
        )
