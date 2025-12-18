"""
Evoke Core - Session and context management

Sessions are created automatically when the first event is captured.
Users can optionally use explicit session boundaries for more control.
"""
from contextvars import ContextVar
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import uuid
import logging

from evoke.schema import Identity, PolicyConfig

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """
    Thread-local session context for tracking events.
    Manages session_id, sequence numbers, parent-child relationships,
    and custom_metadata propagation for nested events.
    """
    session_id: str
    seq_counter: int = 0
    event_stack: List[int] = field(default_factory=list)
    custom_metadata_stack: List[Dict[str, Any]] = field(default_factory=list)

    def next_seq(self) -> int:
        """Get next sequence number"""
        self.seq_counter += 1
        return self.seq_counter

    def current_parent(self) -> Optional[int]:
        """Get current parent sequence number (top of stack)"""
        return self.event_stack[-1] if self.event_stack else None

    def push_event(self, seq: int) -> None:
        """Push event onto stack (for nested events)"""
        self.event_stack.append(seq)

    def pop_event(self) -> Optional[int]:
        """Pop event from stack"""
        return self.event_stack.pop() if self.event_stack else None

    def push_custom_metadata(self, metadata: Dict[str, Any]) -> None:
        """Push custom_metadata context for nested events."""
        current = self.current_custom_metadata()
        merged = {**current, **metadata}
        self.custom_metadata_stack.append(merged)

    def pop_custom_metadata(self) -> Optional[Dict[str, Any]]:
        """Pop custom_metadata context"""
        return self.custom_metadata_stack.pop() if self.custom_metadata_stack else None

    def current_custom_metadata(self) -> Dict[str, Any]:
        """Get current custom_metadata (merged global + stack)."""
        base = _global_custom_metadata.copy()
        if self.custom_metadata_stack:
            base.update(self.custom_metadata_stack[-1])
        return base


# Thread-local session context
_session_context: ContextVar[Optional[SessionContext]] = ContextVar(
    "evoke_session",
    default=None
)

# Global identity
_global_identity: Optional[Identity] = None

# Global custom metadata
_global_custom_metadata: dict = {}

# Global policy configuration
_global_policy: Optional[PolicyConfig] = None


def identity(
    user_id: Optional[str] = None,
    user_type: Optional[str] = None,
    organization_id: Optional[str] = None,
    org_id: Optional[str] = None,
    organization_type: Optional[str] = None,
    role: Optional[str] = None,
    access_level: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """
    Set identity metadata for YOUR application's users.

    IMPORTANT: This is NOT Evoke platform identity. This tracks YOUR
    end users - the people using YOUR AI-powered application.

    Args:
        user_id: Your user's identifier (e.g., "user_123")
        user_type: Type of user (admin, user, service, etc.)
        organization_id: Your customer's organization ID
        org_id: Alias for organization_id
        organization_type: Type of organization (enterprise, team, personal)
        role: User's role in your application
        access_level: Access level (public, internal, confidential, restricted)
        session_id: Your app's session ID (optional override)
    """
    global _global_identity

    resolved_org_id = organization_id or org_id

    _global_identity = Identity(
        user_id=user_id,
        user_type=user_type,
        organization_id=resolved_org_id,
        organization_type=organization_type,
        role=role,
        access_level=access_level,
        session_id=session_id,
    )

    logger.debug(f"Set identity: user_id={user_id}, org_id={resolved_org_id}, role={role}")


def custom_metadata(data: dict) -> None:
    """
    Set custom metadata for all events.

    Args:
        data: Dictionary of custom metadata key-value pairs

    Raises:
        TypeError: If data is not a dictionary
    """
    global _global_custom_metadata

    if not isinstance(data, dict):
        raise TypeError(f"custom_metadata expects a dict, got {type(data).__name__}")

    _global_custom_metadata.update(data)
    logger.debug(f"Set custom metadata: {_global_custom_metadata}")


def get_identity() -> Optional[Identity]:
    """Get the current global identity"""
    return _global_identity


def get_custom_metadata() -> dict:
    """Get the current global custom metadata"""
    return _global_custom_metadata.copy()


def get_policy_config() -> Optional[PolicyConfig]:
    """Get the current policy configuration"""
    return _global_policy


def set_policy_config(policy: PolicyConfig) -> None:
    """Set the policy configuration"""
    global _global_policy
    _global_policy = policy
    logger.debug(f"Set policy config: mode={policy.mode}, redact={policy.redact}")


def get_current_session() -> Optional[SessionContext]:
    """Get current session context if one exists"""
    return _session_context.get()


def get_or_create_session() -> SessionContext:
    """
    Get current session or auto-create one.
    This is called automatically when any event is captured.
    """
    ctx = _session_context.get()
    if ctx is None:
        session_id = str(uuid.uuid4())
        ctx = SessionContext(session_id=session_id)
        _session_context.set(ctx)
        logger.debug(f"Auto-created session: {session_id}")
    return ctx


def end_session() -> Optional[str]:
    """End current session and return the session_id."""
    ctx = _session_context.get()
    if ctx:
        session_id = ctx.session_id
        _session_context.set(None)
        logger.debug(f"Ended session: {session_id}")
        return session_id
    return None


def new_session() -> str:
    """
    Start a new session, ending any existing one.

    Returns:
        The new session_id
    """
    # Flush any pending events from the old session
    try:
        from evoke.core.transport import get_transport
        transport = get_transport()
        if transport:
            transport.flush()
    except ImportError:
        pass

    # End current session if exists
    end_session()

    # Create new session
    session_id = str(uuid.uuid4())
    ctx = SessionContext(session_id=session_id)
    _session_context.set(ctx)
    logger.debug(f"Started new session: {session_id}")

    return session_id


@contextmanager
def session(name: Optional[str] = None, **metadata):
    """
    Context manager for explicit session boundaries.

    Most users won't need this - sessions are created automatically.
    Use this if you want to group specific events into a named session.

    Args:
        name: Session/agent name (for logging)
        **metadata: Additional metadata for this session
    """
    session_id = str(uuid.uuid4())
    ctx = SessionContext(session_id=session_id)

    previous = _session_context.get()
    token = _session_context.set(ctx)

    logger.debug(f"Started explicit session: {session_id}")

    try:
        yield ctx
    finally:
        try:
            from evoke.core.transport import get_transport
            transport = get_transport()
            if transport:
                transport.flush()
        except ImportError:
            pass

        _session_context.reset(token)
        if previous:
            _session_context.set(previous)

        logger.debug(f"Ended explicit session: {session_id}")
