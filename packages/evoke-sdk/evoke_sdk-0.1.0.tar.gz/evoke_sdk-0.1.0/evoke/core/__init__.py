"""
Evoke Core - SDK initialization, session management, and event transport
"""
from evoke.core.client import init, flush, get_system_info
from evoke.core.session import (
    session,
    get_current_session,
    end_session,
    identity,
    custom_metadata,
    get_identity,
    get_custom_metadata,
    get_policy_config,
    set_policy_config,
)
from evoke.core.transport import EventTransport, get_transport, set_transport
from evoke.core.config import Config, is_initialized, set_initialized

__all__ = [
    # Client
    "init",
    "flush",
    "get_system_info",
    # Session
    "session",
    "get_current_session",
    "end_session",
    "identity",
    "custom_metadata",
    "get_identity",
    "get_custom_metadata",
    "get_policy_config",
    "set_policy_config",
    # Transport
    "EventTransport",
    "get_transport",
    "set_transport",
    # Config
    "Config",
    "is_initialized",
    "set_initialized",
]
