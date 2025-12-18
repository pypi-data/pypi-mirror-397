"""
LangChain Instrumentation - Event-Driven Capture

Instruments LangChain to capture:
- Agent execution
- Chain execution
- Tool calls
"""
from typing import Collection
import logging

from wrapt import wrap_function_wrapper

from evoke.wrappers.base import BaseInstrumentor
from evoke.schema import EventType

logger = logging.getLogger(__name__)


class EvokeLangChainInstrumentor(BaseInstrumentor):
    """Instrumentor for LangChain framework - emits events for chains and tools"""

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["langchain >= 0.1.0"]

    def _instrument(self, **kwargs):
        """Instrument LangChain"""
        # Instrument Chain.invoke (base method for all chains)
        try:
            wrap_function_wrapper(
                "langchain.chains.base",
                "Chain.invoke",
                self._chain_invoke_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument Chain.invoke: {e}")

        # Instrument tools if langchain_core is available
        try:
            wrap_function_wrapper(
                "langchain_core.tools",
                "BaseTool.invoke",
                self._tool_invoke_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument BaseTool.invoke: {e}")

        try:
            wrap_function_wrapper(
                "langchain_core.tools",
                "BaseTool._run",
                self._tool_run_wrapper(),
            )
        except Exception as e:
            logger.debug(f"Could not instrument BaseTool._run: {e}")

        logger.debug("LangChain instrumented")

    def _uninstrument(self, **kwargs):
        """Uninstrument LangChain"""
        try:
            from langchain.chains.base import Chain
            if hasattr(Chain.invoke, "__wrapped__"):
                Chain.invoke = Chain.invoke.__wrapped__
        except Exception:
            pass

        try:
            from langchain_core.tools import BaseTool
            if hasattr(BaseTool.invoke, "__wrapped__"):
                BaseTool.invoke = BaseTool.invoke.__wrapped__
            if hasattr(BaseTool._run, "__wrapped__"):
                BaseTool._run = BaseTool._run.__wrapped__
        except Exception:
            pass

    def _chain_invoke_wrapper(self):
        """Wrapper for Chain.invoke() - emits agent reasoning event"""

        def wrapper(wrapped, instance, args, kwargs):
            from evoke.functions.capture import capture

            # Get chain name
            chain_name = type(instance).__name__

            # Format input as structured data
            input_data = None
            if args:
                input_data = self._serialize_data(args[0])
            elif kwargs:
                input_data = self._serialize_data(kwargs)

            try:
                result = wrapped(*args, **kwargs)

                # Format output as structured data
                output_data = self._serialize_data(result)

                # Emit event with structured input/output
                capture(
                    event_type=EventType.AGENT_REASONING,
                    input={"data": input_data},
                    output={"data": output_data},
                    metadata={
                        "chain_name": chain_name,
                        "framework": "langchain",
                    },
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"chain_name": chain_name, "framework": "langchain"},
                )
                raise

        return wrapper

    def _tool_invoke_wrapper(self):
        """Wrapper for BaseTool.invoke() - emits tool call event"""

        def wrapper(wrapped, instance, args, kwargs):
            tool_name = getattr(instance, "name", "unknown_tool")
            tool_description = getattr(instance, "description", "")

            # Get tool source location (where the tool function is defined)
            # This is needed because tools run in thread pools, so the call stack
            # doesn't contain user code - we need to inspect the tool function itself
            source_info = self._get_tool_source_info(instance)

            # Capture structured input (the actual arguments)
            tool_input = None
            if args:
                tool_input = self._serialize_data(args[0])

            try:
                result = wrapped(*args, **kwargs)

                # Capture structured output (the actual result)
                tool_output = self._serialize_data(result)

                # Emit event with structured input/output
                self.capture_tool_event(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_output=tool_output,
                    category="langchain_tool",
                    metadata={
                        **source_info,
                        "description": tool_description[:200] if tool_description else None,
                        "framework": "langchain",
                    },
                )

                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"tool_name": tool_name, "framework": "langchain"},
                )
                raise

        return wrapper

    def _tool_run_wrapper(self):
        """Wrapper for BaseTool._run() - captures internal tool execution"""

        def wrapper(wrapped, instance, args, kwargs):
            # This is the internal execution - we capture it separately
            # in case invoke is not called directly
            tool_name = getattr(instance, "name", "unknown_tool")

            try:
                result = wrapped(*args, **kwargs)
                return result

            except Exception as e:
                self.capture_error_event(
                    error_message=str(e),
                    error_type=type(e).__name__,
                    metadata={"tool_name": tool_name, "framework": "langchain", "method": "_run"},
                )
                raise

        return wrapper

    @staticmethod
    def _get_tool_source_info(tool_instance) -> dict:
        """
        Get the source file and line number where a tool function is defined.

        This is needed because LangChain tools run in thread pools, so the call
        stack doesn't contain user code. We inspect the tool function directly.
        """
        import inspect

        try:
            # Try to get the underlying function from the tool
            func = None

            # LangChain @tool decorator stores the function in .func
            if hasattr(tool_instance, "func") and callable(tool_instance.func):
                func = tool_instance.func
            # Some tools use _run method
            elif hasattr(tool_instance, "_run") and callable(tool_instance._run):
                func = tool_instance._run
            # Try coroutine for async tools
            elif hasattr(tool_instance, "coroutine") and callable(tool_instance.coroutine):
                func = tool_instance.coroutine

            if func:
                source_file = inspect.getsourcefile(func)
                source_lines = inspect.getsourcelines(func)
                if source_file and source_lines:
                    return {
                        "caller_function": func.__name__,
                        "caller_file": source_file,
                        "caller_line": source_lines[1],  # Line number where function starts
                    }
        except Exception:
            pass

        return {}

    @staticmethod
    def _serialize_data(obj, max_str_length: int = 2000):
        """Safely serialize object to JSON-compatible format while preserving structure"""
        import json

        if obj is None:
            return None

        # Already a dict or list - try to keep structure
        if isinstance(obj, dict):
            try:
                # Test if it's JSON serializable
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # Contains non-serializable values, convert to string representation
                return {k: EvokeLangChainInstrumentor._serialize_data(v, max_str_length) for k, v in obj.items()}

        if isinstance(obj, (list, tuple)):
            try:
                json.dumps(obj)
                return list(obj)
            except (TypeError, ValueError):
                return [EvokeLangChainInstrumentor._serialize_data(item, max_str_length) for item in obj]

        # Primitives
        if isinstance(obj, (str, int, float, bool)):
            if isinstance(obj, str) and len(obj) > max_str_length:
                return obj[:max_str_length] + "..."
            return obj

        # Try to get dict representation for objects
        if hasattr(obj, "dict") and callable(obj.dict):
            try:
                return obj.dict()
            except Exception:
                pass

        if hasattr(obj, "__dict__"):
            try:
                result = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
                json.dumps(result)
                return result
            except (TypeError, ValueError):
                pass

        # Fallback to string
        try:
            s = str(obj)
            if len(s) > max_str_length:
                return s[:max_str_length] + "..."
            return s
        except Exception:
            return "<unable to serialize>"
