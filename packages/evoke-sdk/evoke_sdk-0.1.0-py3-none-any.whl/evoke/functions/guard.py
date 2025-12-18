"""
Evoke Functions - Guard decorator for tracking and protecting functions
"""
from functools import wraps
from typing import Optional, Callable, Dict, Any
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


def safe_str(obj: Any, max_length: int = 2000) -> str:
    """Safely convert object to string with length limit."""
    try:
        if obj is None:
            return "None"
        elif isinstance(obj, (str, int, float, bool)):
            s = str(obj)
        elif isinstance(obj, (list, tuple)):
            if len(obj) > 10:
                s = f"[{len(obj)} items]"
            else:
                s = str(obj)
        elif isinstance(obj, dict):
            try:
                s = json.dumps(obj, default=str)
            except Exception:
                s = str(obj)
        else:
            s = str(obj)

        if len(s) > max_length:
            return s[:max_length] + "..."
        return s
    except Exception:
        return "<unable to serialize>"


def format_args(args: tuple, kwargs: dict) -> str:
    """Format function arguments for capture."""
    parts = []
    if args:
        for i, arg in enumerate(args):
            parts.append(f"arg{i}={safe_str(arg)}")
    if kwargs:
        for k, v in kwargs.items():
            parts.append(f"{k}={safe_str(v)}")
    return ", ".join(parts) if parts else ""

# Save reference to builtin type() before it gets shadowed by parameter name
_builtin_type = type


def guard(
    _func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    capture: bool = True,
    category: Optional[str] = None,
    is_external: Optional[bool] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
):
    """
    Unified decorator for tracking and protecting functions.

    This decorator marks functions for security monitoring and captures events
    by default. Set capture=False to disable event emission for specific functions.

    Args:
        name: Optional name for the event (defaults to function name)
        type: Function type - "tool", "model", "agent", or None (default guard)
        capture: If True, emit events to the platform (default: True)
        category: Tool category (when type="tool")
        is_external: Whether tool calls external APIs (when type="tool")
        provider: Model provider (when type="model")
        model: Model name (when type="model")
        metadata: Internal/system metadata to include with events
        custom_metadata: Customer-controlled metadata

    Examples:
        @evoke.guard
        def process_request(request: str):
            return agent.run(request)

        @evoke.guard(capture=True, name="customer_support")
        def handle_query(query: str):
            return agent.run(query)

        @evoke.guard(type="tool", category="knowledge_base")
        def search_docs(query: str):
            return search(query)
    """

    def decorator(func: Callable) -> Callable:
        guard_name = name or func.__name__

        def _get_capture_params():
            """Get parameters for capture_scope based on guard type."""
            if type == "tool":
                return {
                    "type": "tool",
                    "name": guard_name,
                    "category": category,
                }
            elif type == "model" or type == "agent":
                return {
                    "type": "model",
                    "name": model or guard_name,
                    "provider": provider or "custom",
                }
            else:
                return {"type": "custom", "name": guard_name}

        def _format_result(result: Any) -> str:
            return safe_str(result)

        @wraps(func)
        def wrapper(*args, **kwargs):
            from evoke.functions.capture import capture_scope, session_scope
            from evoke.core.session import get_policy_config

            if not capture:
                with session_scope():
                    return func(*args, **kwargs)

            policy = get_policy_config()

            if policy and policy.mode == "off":
                return func(*args, **kwargs)

            # Use raw first arg as input when available
            if args:
                input_str = str(args[0])[:10000]
            elif kwargs:
                # Use first kwarg value
                input_str = str(list(kwargs.values())[0])[:10000]
            else:
                input_str = ""

            capture_params = _get_capture_params()

            event_metadata = {
                "guard_name": guard_name,
                "guard_type": type,
                "policy_mode": policy.mode if policy else "monitor",
                **(metadata or {}),
            }

            with capture_scope(
                input=input_str,
                metadata=event_metadata,
                custom_metadata=custom_metadata,
                **capture_params,
            ) as set_output:
                try:
                    result = func(*args, **kwargs)
                    output_str = _format_result(result)
                    set_output(output_str)
                    return result
                except Exception as e:
                    set_output(f"Error: {_builtin_type(e).__name__}: {str(e)}")
                    raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from evoke.functions.capture import capture_scope, session_scope
            from evoke.core.session import get_policy_config

            if not capture:
                with session_scope():
                    return await func(*args, **kwargs)

            policy = get_policy_config()

            if policy and policy.mode == "off":
                return await func(*args, **kwargs)

            # Use raw first arg as input when available
            if args:
                input_str = str(args[0])[:10000]
            elif kwargs:
                # Use first kwarg value
                input_str = str(list(kwargs.values())[0])[:10000]
            else:
                input_str = ""

            capture_params = _get_capture_params()

            event_metadata = {
                "guard_name": guard_name,
                "guard_type": type,
                "policy_mode": policy.mode if policy else "monitor",
                **(metadata or {}),
            }

            with capture_scope(
                input=input_str,
                metadata=event_metadata,
                custom_metadata=custom_metadata,
                **capture_params,
            ) as set_output:
                try:
                    result = await func(*args, **kwargs)
                    output_str = _format_result(result)
                    set_output(output_str)
                    return result
                except Exception as e:
                    set_output(f"Error: {_builtin_type(e).__name__}: {str(e)}")
                    raise

        # Mark function as guarded
        wrapper.__evoke_guard__ = True
        wrapper.__evoke_guard_name__ = guard_name
        wrapper.__evoke_guard_type__ = type
        wrapper.__evoke_guard_capture__ = capture

        if asyncio.iscoroutinefunction(func):
            async_wrapper.__evoke_guard__ = True
            async_wrapper.__evoke_guard_name__ = guard_name
            async_wrapper.__evoke_guard_type__ = type
            async_wrapper.__evoke_guard_capture__ = capture
            return async_wrapper
        return wrapper

    if _func is not None:
        return decorator(_func)
    return decorator
