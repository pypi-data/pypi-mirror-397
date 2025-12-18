"""
Anthropic Instrumentation - Event-Driven Capture

Instruments Anthropic SDK to automatically capture message generation
as events for detection and analysis.
"""
from typing import Collection, Optional
import logging

from wrapt import wrap_function_wrapper

from evoke.wrappers.base import BaseInstrumentor

logger = logging.getLogger(__name__)


class EvokeAnthropicInstrumentor(BaseInstrumentor):
    """Instrumentor for Anthropic SDK - emits events for model calls"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["anthropic >= 0.3.0"]

    def _instrument(self, **kwargs):
        """Instrument Anthropic SDK"""
        # Wrap messages create
        wrap_function_wrapper(
            "anthropic.resources.messages",
            "Messages.create",
            self._messages_wrapper(),
        )

        # Wrap async messages create
        wrap_function_wrapper(
            "anthropic.resources.messages",
            "AsyncMessages.create",
            self._async_messages_wrapper(),
        )

        logger.debug("Anthropic SDK instrumented")

    def _uninstrument(self, **kwargs):
        """Uninstrument Anthropic SDK"""
        try:
            import anthropic.resources.messages

            # Restore original methods
            if hasattr(anthropic.resources.messages.Messages.create, "__wrapped__"):
                anthropic.resources.messages.Messages.create = (
                    anthropic.resources.messages.Messages.create.__wrapped__
                )
            if hasattr(anthropic.resources.messages.AsyncMessages.create, "__wrapped__"):
                anthropic.resources.messages.AsyncMessages.create = (
                    anthropic.resources.messages.AsyncMessages.create.__wrapped__
                )
        except Exception as e:
            logger.warning(f"Error uninstrumenting Anthropic: {e}")

    def _messages_wrapper(self):
        """Wrapper for messages.create() - emits model call event"""

        def wrapper(wrapped, instance, args, kwargs):
            # Extract request info
            model = kwargs.get("model", "unknown")
            messages = kwargs.get("messages", [])
            system = kwargs.get("system", "")

            # Format input as structured messages
            input_messages = self._format_messages(messages, system)

            try:
                result = wrapped(*args, **kwargs)

                # Extract response as structured messages
                output_messages = self._extract_completion(result)
                tokens_in = None
                tokens_out = None

                if hasattr(result, "usage"):
                    tokens_in = getattr(result.usage, "input_tokens", None)
                    tokens_out = getattr(result.usage, "output_tokens", None)

                # Build metadata
                metadata = {
                    "response_id": getattr(result, "id", None),
                    "response_model": getattr(result, "model", model),
                    "stop_reason": getattr(result, "stop_reason", None),
                }

                # Check for tool use
                tool_uses = self._extract_tool_uses(result)
                if tool_uses:
                    metadata["tool_uses"] = tool_uses

                # Emit event with structured messages
                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=model,
                    provider="anthropic",
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata=metadata,
                )

                return result

            except Exception as e:
                # Emit error event
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": "anthropic"},
                )
                raise

        return wrapper

    def _async_messages_wrapper(self):
        """Wrapper for async messages.create()"""

        async def wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model", "unknown")
            messages = kwargs.get("messages", [])
            system = kwargs.get("system", "")
            input_messages = self._format_messages(messages, system)

            try:
                result = await wrapped(*args, **kwargs)

                output_messages = self._extract_completion(result)
                tokens_in = None
                tokens_out = None

                if hasattr(result, "usage"):
                    tokens_in = getattr(result.usage, "input_tokens", None)
                    tokens_out = getattr(result.usage, "output_tokens", None)

                metadata = {
                    "response_id": getattr(result, "id", None),
                    "response_model": getattr(result, "model", model),
                    "stop_reason": getattr(result, "stop_reason", None),
                }

                tool_uses = self._extract_tool_uses(result)
                if tool_uses:
                    metadata["tool_uses"] = tool_uses

                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=model,
                    provider="anthropic",
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata=metadata,
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": "anthropic"},
                )
                raise

        return wrapper

    # === Helper Methods ===

    @staticmethod
    def _format_messages(messages: list, system: str = "") -> list:
        """Format Anthropic messages as structured list of message dicts"""
        formatted = []

        # Add system message if present
        if system:
            if isinstance(system, str):
                formatted.append({"role": "system", "content": system})
            elif isinstance(system, list):
                # System can be a list of content blocks
                text_parts = []
                for block in system:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif hasattr(block, "text"):
                        text_parts.append(block.text)
                formatted.append({"role": "system", "content": " ".join(text_parts)})

        # Format messages
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")

                # Content can be string or list of content blocks
                if isinstance(content, list):
                    text_parts = []
                    tool_calls = []
                    for block in content:
                        if isinstance(block, dict):
                            if block.get("type") == "text":
                                text_parts.append(block.get("text", ""))
                            elif block.get("type") == "tool_result":
                                # This is a tool response message
                                tool_calls.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.get("tool_use_id", ""),
                                    "content": block.get("content", ""),
                                })
                            elif block.get("type") == "tool_use":
                                tool_calls.append({
                                    "type": "tool_use",
                                    "id": block.get("id", ""),
                                    "name": block.get("name", ""),
                                    "input": block.get("input", {}),
                                })
                        elif hasattr(block, "text"):
                            text_parts.append(block.text)
                    content = " ".join(text_parts)

                    msg_dict = {"role": role, "content": content}
                    if tool_calls:
                        msg_dict["tool_calls"] = tool_calls
                    formatted.append(msg_dict)
                else:
                    formatted.append({"role": role, "content": content})

            elif hasattr(msg, "role") and hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if hasattr(block, "text"):
                            text_parts.append(block.text)
                    content = " ".join(text_parts)
                formatted.append({"role": msg.role, "content": content or ""})

        return formatted

    @staticmethod
    def _extract_completion(result) -> list:
        """Extract completion as structured message list from Anthropic response"""
        if not hasattr(result, "content") or not result.content:
            return []

        text_parts = []
        tool_calls = []

        for block in result.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append({
                    "id": getattr(block, "id", None),
                    "name": getattr(block, "name", None),
                    "arguments": getattr(block, "input", {}),
                })

        msg_dict = {"role": "assistant", "content": " ".join(text_parts)}
        if tool_calls:
            msg_dict["tool_calls"] = tool_calls

        return [msg_dict]

    @staticmethod
    def _extract_tool_uses(result) -> list:
        """Extract tool use blocks from Anthropic response"""
        if not hasattr(result, "content") or not result.content:
            return []

        tool_uses = []
        for block in result.content:
            if hasattr(block, "type") and block.type == "tool_use":
                tool_uses.append({
                    "id": getattr(block, "id", None),
                    "name": getattr(block, "name", None),
                    "input": str(getattr(block, "input", {}))[:500],  # Limit size
                })

        return tool_uses
