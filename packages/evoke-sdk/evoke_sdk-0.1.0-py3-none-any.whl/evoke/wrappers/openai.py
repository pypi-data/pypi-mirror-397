"""
OpenAI Instrumentation - Event-Driven Capture

Instruments OpenAI SDK to automatically capture chat completions and embeddings
as events for detection and analysis.
"""
from typing import Collection, Optional
from threading import Lock
import logging
import json

from wrapt import wrap_function_wrapper

from evoke.wrappers.base import BaseInstrumentor

logger = logging.getLogger(__name__)


class EvokeOpenAIInstrumentor(BaseInstrumentor):
    """Instrumentor for OpenAI SDK - emits events for model calls"""

    def __init__(self):
        super().__init__()
        # Track captured response IDs to prevent duplicates
        # (sync and async wrappers can both trigger for the same call)
        self._captured_response_ids: set = set()
        self._max_tracked_ids = 1000  # Prevent unbounded memory growth
        self._dedup_lock = Lock()  # Thread-safety for deduplication

    def _should_capture(self, response_id: Optional[str]) -> bool:
        """Thread-safe check if this response should be captured (deduplication)."""
        if response_id is None:
            return True  # Can't dedupe without ID

        with self._dedup_lock:  # Atomic check-and-add
            if response_id in self._captured_response_ids:
                return False  # Already captured
            # Add to tracked set
            self._captured_response_ids.add(response_id)
            # Prevent unbounded growth by clearing old entries
            if len(self._captured_response_ids) > self._max_tracked_ids:
                to_remove = list(self._captured_response_ids)[:self._max_tracked_ids // 2]
                for rid in to_remove:
                    self._captured_response_ids.discard(rid)
            return True

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["openai >= 1.0.0"]

    def _instrument(self, **kwargs):
        """Instrument OpenAI SDK"""
        # Wrap chat completions create
        wrap_function_wrapper(
            "openai.resources.chat.completions",
            "Completions.create",
            self._chat_completions_wrapper(),
        )

        # Wrap async chat completions create
        wrap_function_wrapper(
            "openai.resources.chat.completions",
            "AsyncCompletions.create",
            self._async_chat_completions_wrapper(),
        )

        # Wrap embeddings create
        wrap_function_wrapper(
            "openai.resources.embeddings",
            "Embeddings.create",
            self._embeddings_wrapper(),
        )

        logger.debug("OpenAI SDK instrumented")

    def _uninstrument(self, **kwargs):
        """Uninstrument OpenAI SDK"""
        try:
            import openai.resources.chat.completions
            import openai.resources.embeddings

            # Restore original methods
            if hasattr(openai.resources.chat.completions.Completions.create, "__wrapped__"):
                openai.resources.chat.completions.Completions.create = (
                    openai.resources.chat.completions.Completions.create.__wrapped__
                )
            if hasattr(openai.resources.chat.completions.AsyncCompletions.create, "__wrapped__"):
                openai.resources.chat.completions.AsyncCompletions.create = (
                    openai.resources.chat.completions.AsyncCompletions.create.__wrapped__
                )
            if hasattr(openai.resources.embeddings.Embeddings.create, "__wrapped__"):
                openai.resources.embeddings.Embeddings.create = (
                    openai.resources.embeddings.Embeddings.create.__wrapped__
                )
        except Exception as e:
            logger.warning(f"Error uninstrumenting OpenAI: {e}")

    def _chat_completions_wrapper(self):
        """Wrapper for chat completions - emits model call event with agent phase detection"""

        def wrapper(wrapped, instance, args, kwargs):
            # Extract request info before calling
            model = kwargs.get("model", "unknown")
            messages = kwargs.get("messages", [])

            # Format input as structured message list
            input_messages = self._format_messages(messages)

            # Execute the actual API call
            try:
                result = wrapped(*args, **kwargs)

                # Handle LegacyAPIResponse wrapper (used when raw response is requested)
                # This happens with LangChain and other frameworks
                actual_result = result
                if hasattr(result, 'parse') and callable(result.parse):
                    # It's a LegacyAPIResponse - parse it to get the actual response
                    try:
                        actual_result = result.parse()
                    except Exception:
                        pass
                elif hasattr(result, '_parsed'):
                    # Already parsed, use the parsed result
                    actual_result = result._parsed or result

                # Extract response as structured message list
                output_messages = self._extract_completion(actual_result)
                tokens_in = None
                tokens_out = None

                # Extract token usage (try actual_result first, fallback to result)
                if hasattr(actual_result, "usage") and actual_result.usage:
                    usage = actual_result.usage
                    tokens_in = getattr(usage, "prompt_tokens", None)
                    tokens_out = getattr(usage, "completion_tokens", None)

                    # Some OpenAI responses use different attribute names
                    if tokens_in is None:
                        tokens_in = getattr(usage, "input_tokens", None)
                    if tokens_out is None:
                        tokens_out = getattr(usage, "output_tokens", None)

                # Build metadata
                metadata = {
                    "response_id": getattr(actual_result, "id", None),
                    "response_model": getattr(actual_result, "model", model),
                }

                # Extract finish_reason and tool_calls for phase detection
                finish_reason = None
                has_tool_calls = False

                if hasattr(actual_result, "choices") and actual_result.choices:
                    choice = actual_result.choices[0]
                    if hasattr(choice, "finish_reason"):
                        finish_reason = choice.finish_reason
                        metadata["finish_reason"] = finish_reason
                    if hasattr(choice, "message") and hasattr(choice.message, "tool_calls"):
                        tool_calls = choice.message.tool_calls
                        if tool_calls:
                            has_tool_calls = True
                            metadata["tool_calls"] = self._format_tool_calls(tool_calls)

                # Deduplicate - skip if already captured by async wrapper
                response_id = metadata.get("response_id")
                if not self._should_capture(response_id):
                    return result

                # Detect agent phase based on response characteristics
                event_type = self.detect_agent_phase(
                    finish_reason=finish_reason,
                    has_tool_calls=has_tool_calls,
                    messages=messages,
                )

                # Emit event with detected phase
                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=model,
                    provider="openai",
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata=metadata,
                    event_type=event_type,
                )

                return result

            except Exception as e:
                # Emit error event
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": "openai"},
                )
                raise

        return wrapper

    def _async_chat_completions_wrapper(self):
        """Wrapper for async chat completions with agent phase detection"""

        async def wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model", "unknown")
            messages = kwargs.get("messages", [])
            input_messages = self._format_messages(messages)

            try:
                result = await wrapped(*args, **kwargs)

                # Handle LegacyAPIResponse wrapper (used when raw response is requested)
                # This happens with LangChain and other frameworks
                actual_result = result
                if hasattr(result, 'parse') and callable(result.parse):
                    # It's a LegacyAPIResponse - parse it to get the actual response
                    try:
                        actual_result = result.parse()
                    except Exception:
                        pass
                elif hasattr(result, '_parsed'):
                    # Already parsed, use the parsed result
                    actual_result = result._parsed or result

                output_messages = self._extract_completion(actual_result)
                tokens_in = None
                tokens_out = None

                # Extract token usage
                if hasattr(actual_result, "usage") and actual_result.usage:
                    usage = actual_result.usage
                    tokens_in = getattr(usage, "prompt_tokens", None)
                    tokens_out = getattr(usage, "completion_tokens", None)

                    # Some OpenAI responses use different attribute names
                    if tokens_in is None:
                        tokens_in = getattr(usage, "input_tokens", None)
                    if tokens_out is None:
                        tokens_out = getattr(usage, "output_tokens", None)

                metadata = {
                    "response_id": getattr(actual_result, "id", None),
                    "response_model": getattr(actual_result, "model", model),
                }

                # Extract finish_reason and tool_calls for phase detection
                finish_reason = None
                has_tool_calls = False

                if hasattr(actual_result, "choices") and actual_result.choices:
                    choice = actual_result.choices[0]
                    if hasattr(choice, "finish_reason"):
                        finish_reason = choice.finish_reason
                        metadata["finish_reason"] = finish_reason
                    if hasattr(choice, "message") and hasattr(choice.message, "tool_calls"):
                        tool_calls = choice.message.tool_calls
                        if tool_calls:
                            has_tool_calls = True
                            metadata["tool_calls"] = self._format_tool_calls(tool_calls)

                # Deduplicate - skip if already captured by sync wrapper
                response_id = metadata.get("response_id")
                if not self._should_capture(response_id):
                    return result

                # Detect agent phase based on response characteristics
                event_type = self.detect_agent_phase(
                    finish_reason=finish_reason,
                    has_tool_calls=has_tool_calls,
                    messages=messages,
                )

                # Emit event with detected phase
                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=model,
                    provider="openai",
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata=metadata,
                    event_type=event_type,
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": "openai"},
                )
                raise

        return wrapper

    def _embeddings_wrapper(self):
        """Wrapper for embeddings - emits model call event"""

        def wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model", "text-embedding-ada-002")
            input_data = kwargs.get("input", "")

            # Format input as structured message
            if isinstance(input_data, list):
                input_content = f"[{len(input_data)} inputs]"
            else:
                input_content = str(input_data)[:1000]

            input_messages = [{"role": "user", "content": input_content}]

            try:
                result = wrapped(*args, **kwargs)

                # Extract usage
                tokens_in = None
                if hasattr(result, "usage") and hasattr(result.usage, "total_tokens"):
                    tokens_in = result.usage.total_tokens

                # Format output as structured message
                output_content = f"[{len(result.data)} embeddings]" if hasattr(result, "data") else ""
                output_messages = [{"role": "assistant", "content": output_content}]

                # Emit event
                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=model,
                    provider="openai",
                    tokens_in=tokens_in,
                    tokens_out=0,
                    metadata={"operation": "embeddings"},
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": "openai", "operation": "embeddings"},
                )
                raise

        return wrapper

    # === Helper Methods ===

    @staticmethod
    def _format_messages(messages: list) -> list:
        """Convert OpenAI messages to structured list of dicts"""
        if not messages:
            return []

        formatted = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Handle multi-modal content - extract text parts
                    text_parts = [
                        p.get("text", "") for p in content
                        if isinstance(p, dict) and p.get("type") == "text"
                    ]
                    content = " ".join(text_parts)

                msg_dict = {"role": role, "content": content}

                # Include tool_calls if present
                if msg.get("tool_calls"):
                    msg_dict["tool_calls"] = msg["tool_calls"]
                if msg.get("tool_call_id"):
                    msg_dict["tool_call_id"] = msg["tool_call_id"]

                formatted.append(msg_dict)
            elif hasattr(msg, "role"):
                msg_dict = {
                    "role": getattr(msg, "role", "unknown"),
                    "content": getattr(msg, "content", "") or ""
                }

                # Include tool_calls if present
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": getattr(tc, "id", None),
                            "name": getattr(tc.function, "name", None) if hasattr(tc, "function") else None,
                            "arguments": getattr(tc.function, "arguments", None) if hasattr(tc, "function") else None,
                        }
                        for tc in msg.tool_calls
                    ]
                if hasattr(msg, "tool_call_id") and msg.tool_call_id:
                    msg_dict["tool_call_id"] = msg.tool_call_id

                formatted.append(msg_dict)

        return formatted

    @staticmethod
    def _extract_completion(result) -> list:
        """Extract completion as structured message list from OpenAI response"""
        if result is None:
            return []

        # Try to get choices
        choices = getattr(result, "choices", None)
        if not choices:
            if isinstance(result, dict):
                choices = result.get("choices", [])
            if not choices:
                return []

        # Get first choice
        choice = choices[0]

        # Try to get message
        message = None
        if hasattr(choice, "message"):
            message = choice.message
        elif isinstance(choice, dict):
            message = choice.get("message", {})

        if not message:
            return []

        # Build structured message dict
        msg_dict = {"role": "assistant"}

        # Get content
        if hasattr(message, "content"):
            msg_dict["content"] = message.content or ""
        elif isinstance(message, dict):
            msg_dict["content"] = message.get("content") or ""

        # Include tool_calls if present
        tool_calls = None
        if hasattr(message, "tool_calls"):
            tool_calls = message.tool_calls
        elif isinstance(message, dict):
            tool_calls = message.get("tool_calls")

        if tool_calls:
            msg_dict["tool_calls"] = []
            for tc in tool_calls:
                func = getattr(tc, "function", None) or (tc.get("function") if isinstance(tc, dict) else None)
                if func:
                    tc_dict = {
                        "id": getattr(tc, "id", None) or (tc.get("id") if isinstance(tc, dict) else None),
                        "name": getattr(func, "name", None) or (func.get("name") if isinstance(func, dict) else None),
                        "arguments": getattr(func, "arguments", None) or (func.get("arguments") if isinstance(func, dict) else None),
                    }
                    msg_dict["tool_calls"].append(tc_dict)

        return [msg_dict]

    @staticmethod
    def _format_tool_calls(tool_calls) -> list:
        """Format tool calls for metadata"""
        formatted = []
        for tc in tool_calls:
            if hasattr(tc, "function"):
                formatted.append({
                    "id": getattr(tc, "id", None),
                    "name": getattr(tc.function, "name", None),
                    "arguments": getattr(tc.function, "arguments", None),
                })
        return formatted
