"""
LiteLLM Instrumentation - Universal Model Provider Coverage

Instruments LiteLLM to automatically capture model calls across 100+ providers:
- OpenAI, Anthropic, Cohere, Mistral, Groq, Together AI
- Azure OpenAI, AWS Bedrock, Google Vertex AI
- Ollama, vLLM, HuggingFace
- And many more

LiteLLM provides a unified interface, so instrumenting it once covers all providers.
"""
from typing import Collection, Optional
import logging

from wrapt import wrap_function_wrapper

from evoke.wrappers.base import BaseInstrumentor

logger = logging.getLogger(__name__)


class EvokeLiteLLMInstrumentor(BaseInstrumentor):
    """Instrumentor for LiteLLM - covers 100+ model providers with one integration"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["litellm >= 1.0.0"]

    def _instrument(self, **kwargs):
        """Instrument LiteLLM"""
        # Wrap the main completion function
        try:
            wrap_function_wrapper(
                "litellm",
                "completion",
                self._completion_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument litellm.completion: {e}")

        # Wrap async completion
        try:
            wrap_function_wrapper(
                "litellm",
                "acompletion",
                self._async_completion_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument litellm.acompletion: {e}")

        # Wrap text completion (for older-style APIs)
        try:
            wrap_function_wrapper(
                "litellm",
                "text_completion",
                self._text_completion_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument litellm.text_completion: {e}")

        # Wrap embedding
        try:
            wrap_function_wrapper(
                "litellm",
                "embedding",
                self._embedding_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument litellm.embedding: {e}")

        logger.debug("LiteLLM instrumented")

    def _uninstrument(self, **kwargs):
        """Uninstrument LiteLLM"""
        try:
            import litellm

            if hasattr(litellm.completion, "__wrapped__"):
                litellm.completion = litellm.completion.__wrapped__
            if hasattr(litellm.acompletion, "__wrapped__"):
                litellm.acompletion = litellm.acompletion.__wrapped__
            if hasattr(litellm.text_completion, "__wrapped__"):
                litellm.text_completion = litellm.text_completion.__wrapped__
            if hasattr(litellm.embedding, "__wrapped__"):
                litellm.embedding = litellm.embedding.__wrapped__
        except Exception as e:
            logger.warning(f"Error uninstrumenting LiteLLM: {e}")

    def _completion_wrapper(self):
        """Wrapper for litellm.completion() - works with all providers"""

        def wrapper(wrapped, instance, args, kwargs):
            # Extract request info
            model = kwargs.get("model", args[0] if args else "unknown")
            messages = kwargs.get("messages", [])

            # Extract provider from model string (e.g., "ollama/llama3" -> "ollama")
            provider = self._extract_provider(model)

            # Format input as structured messages
            input_messages = self._format_messages(messages)

            try:
                result = wrapped(*args, **kwargs)

                # Extract response as structured messages
                output_messages = self._extract_completion(result)
                tokens_in, tokens_out = self._extract_tokens(result)

                # Build metadata
                metadata = {
                    "response_id": getattr(result, "id", None),
                    "response_model": getattr(result, "model", model),
                    "litellm_model": model,  # Original model string
                }

                # Check for tool calls
                tool_calls = self._extract_tool_calls(result)
                if tool_calls:
                    metadata["tool_calls"] = tool_calls

                # Emit event with structured messages
                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=self._extract_model_name(model),
                    provider=provider,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata=metadata,
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": provider},
                )
                raise

        return wrapper

    def _async_completion_wrapper(self):
        """Wrapper for litellm.acompletion()"""

        async def wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model", args[0] if args else "unknown")
            messages = kwargs.get("messages", [])
            provider = self._extract_provider(model)
            input_messages = self._format_messages(messages)

            try:
                result = await wrapped(*args, **kwargs)

                output_messages = self._extract_completion(result)
                tokens_in, tokens_out = self._extract_tokens(result)

                metadata = {
                    "response_id": getattr(result, "id", None),
                    "response_model": getattr(result, "model", model),
                    "litellm_model": model,
                }

                tool_calls = self._extract_tool_calls(result)
                if tool_calls:
                    metadata["tool_calls"] = tool_calls

                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=self._extract_model_name(model),
                    provider=provider,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata=metadata,
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": provider},
                )
                raise

        return wrapper

    def _text_completion_wrapper(self):
        """Wrapper for litellm.text_completion()"""

        def wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model", args[0] if args else "unknown")
            prompt = kwargs.get("prompt", "")
            provider = self._extract_provider(model)

            # Format input as structured message
            if isinstance(prompt, list):
                input_content = "\n".join(prompt)
            else:
                input_content = str(prompt)

            input_messages = [{"role": "user", "content": input_content}]

            try:
                result = wrapped(*args, **kwargs)

                # Extract completion text
                output_content = ""
                if hasattr(result, "choices") and result.choices:
                    choice = result.choices[0]
                    output_content = getattr(choice, "text", "") or ""

                output_messages = [{"role": "assistant", "content": output_content}]

                tokens_in, tokens_out = self._extract_tokens(result)

                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=self._extract_model_name(model),
                    provider=provider,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    metadata={"litellm_model": model, "mode": "text_completion"},
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": provider},
                )
                raise

        return wrapper

    def _embedding_wrapper(self):
        """Wrapper for litellm.embedding()"""

        def wrapper(wrapped, instance, args, kwargs):
            model = kwargs.get("model", args[0] if args else "unknown")
            input_data = kwargs.get("input", "")
            provider = self._extract_provider(model)

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
                if hasattr(result, "usage"):
                    tokens_in = getattr(result.usage, "total_tokens", None)
                    if tokens_in is None:
                        tokens_in = getattr(result.usage, "prompt_tokens", None)

                # Count embeddings
                embedding_count = 0
                if hasattr(result, "data"):
                    embedding_count = len(result.data)

                output_messages = [{"role": "assistant", "content": f"[{embedding_count} embeddings]"}]

                self.capture_model_event(
                    input_messages=input_messages,
                    output_messages=output_messages,
                    model_name=self._extract_model_name(model),
                    provider=provider,
                    tokens_in=tokens_in,
                    tokens_out=0,
                    metadata={"litellm_model": model, "mode": "embedding"},
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"model": model, "provider": provider, "mode": "embedding"},
                )
                raise

        return wrapper

    # === Helper Methods ===

    @staticmethod
    def _extract_provider(model: str) -> str:
        """
        Extract provider from LiteLLM model string.

        Examples:
            "gpt-4" -> "openai"
            "ollama/llama3" -> "ollama"
            "huggingface/meta-llama/Llama-2" -> "huggingface"
            "bedrock/anthropic.claude-v2" -> "bedrock"
            "azure/gpt-4" -> "azure"
        """
        if "/" in model:
            return model.split("/")[0].lower()

        # Default provider detection for models without prefix
        model_lower = model.lower()
        if model_lower.startswith("gpt") or model_lower.startswith("o1"):
            return "openai"
        elif model_lower.startswith("claude"):
            return "anthropic"
        elif model_lower.startswith("command"):
            return "cohere"
        elif model_lower.startswith("mistral") or model_lower.startswith("mixtral"):
            return "mistral"
        elif model_lower.startswith("llama"):
            return "meta"
        elif model_lower.startswith("gemini"):
            return "google"

        return "unknown"

    @staticmethod
    def _extract_model_name(model: str) -> str:
        """
        Extract just the model name without provider prefix.

        Examples:
            "ollama/llama3" -> "llama3"
            "gpt-4" -> "gpt-4"
        """
        if "/" in model:
            parts = model.split("/")
            return "/".join(parts[1:])  # Everything after first /
        return model

    @staticmethod
    def _format_messages(messages: list) -> list:
        """Format messages as structured list of message dicts"""
        if not messages:
            return []

        formatted = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Handle multi-modal content
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
            elif hasattr(msg, "role") and hasattr(msg, "content"):
                msg_dict = {"role": msg.role, "content": msg.content or ""}
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": getattr(tc, "id", None),
                            "name": getattr(tc.function, "name", None) if hasattr(tc, "function") else None,
                            "arguments": getattr(tc.function, "arguments", None) if hasattr(tc, "function") else None,
                        }
                        for tc in msg.tool_calls
                    ]
                formatted.append(msg_dict)

        return formatted

    @staticmethod
    def _extract_completion(result) -> list:
        """Extract completion as structured message list from response"""
        if not hasattr(result, "choices") or not result.choices:
            return []

        choice = result.choices[0]
        if not hasattr(choice, "message"):
            return []

        message = choice.message
        msg_dict = {"role": "assistant", "content": getattr(message, "content", None) or ""}

        # Include tool_calls if present
        if hasattr(message, "tool_calls") and message.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": getattr(tc, "id", None),
                    "name": getattr(tc.function, "name", None) if hasattr(tc, "function") else None,
                    "arguments": getattr(tc.function, "arguments", None) if hasattr(tc, "function") else None,
                }
                for tc in message.tool_calls
            ]

        return [msg_dict]

    @staticmethod
    def _extract_tokens(result) -> tuple:
        """Extract token counts from response"""
        tokens_in = None
        tokens_out = None

        if hasattr(result, "usage") and result.usage:
            usage = result.usage
            # Try different attribute names
            tokens_in = getattr(usage, "prompt_tokens", None)
            if tokens_in is None:
                tokens_in = getattr(usage, "input_tokens", None)

            tokens_out = getattr(usage, "completion_tokens", None)
            if tokens_out is None:
                tokens_out = getattr(usage, "output_tokens", None)

        return tokens_in, tokens_out

    @staticmethod
    def _extract_tool_calls(result) -> list:
        """Extract tool calls from response"""
        if not hasattr(result, "choices") or not result.choices:
            return []

        choice = result.choices[0]
        if not hasattr(choice, "message"):
            return []

        message = choice.message
        if not hasattr(message, "tool_calls") or not message.tool_calls:
            return []

        tool_calls = []
        for tc in message.tool_calls:
            if hasattr(tc, "function"):
                tool_calls.append({
                    "id": getattr(tc, "id", None),
                    "name": getattr(tc.function, "name", None),
                    "arguments": getattr(tc.function, "arguments", None),
                })
        return tool_calls

    @staticmethod
    def _format_tool_calls_as_text(tool_calls: list) -> str:
        """Format tool calls as readable text for output field"""
        parts = []
        for tc in tool_calls:
            name = tc.get("name", "unknown")
            args = tc.get("arguments", "{}")
            parts.append(f"[tool_call: {name}({args})]")
        return " ".join(parts)
