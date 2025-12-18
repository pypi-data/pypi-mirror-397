"""
Evoke Core - SDK initialization and configuration

The SDK is designed to be simple: one line to initialize, then everything
is captured automatically.
"""
from typing import Optional, Union, List
import logging
import socket
import platform

from evoke._version import SDK_VERSION
from evoke.core.config import Config, set_initialized, is_initialized

logger = logging.getLogger(__name__)

# Global policy manager (for internal use by analyze())
_policy_manager = None


def get_policy_manager():
    """Get the global policy manager (internal use by analyze())."""
    return _policy_manager


def init(
    api_key: str = "",
    endpoint: str = "https://api.evokesecurity.com/api/v1",
    debug: bool = False,
    debug_file: Optional[str] = None,
    realtime: bool = True,
    buffer_size: int = 100,
    flush_interval: float = 5.0,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    environment: Optional[str] = None,
    application: Optional[str] = None,
    agent_version: Optional[str] = None,
    # Security policy configuration
    policy: Optional[str] = None,
    redact: Union[bool, List[str]] = False,
    # Signature sync options
    sync_signatures: bool = True,
    signature_poll_interval: int = 300,
    # Policy sync options
    sync_policies: bool = True,
    policy_poll_interval: int = 300,
    # Detection options
    enable_ml_detection: bool = True,
    detection_model: Optional[str] = None,
) -> None:
    """
    Initialize Evoke SDK - ONE LINE is all you need!

    The SDK will automatically:
    - Instrument model calls (OpenAI, Anthropic, etc.)
    - Instrument tool executions
    - Instrument data source access
    - Create sessions automatically
    - Sequence events with parent-child relationships
    - Send events to the platform (or save locally in debug mode)

    Args:
        api_key: Your Evoke API key (format: evoke_pk_...). Not required in debug mode.
        endpoint: Backend endpoint URL (default: localhost for dev)
        debug: If True, save events to local file instead of sending to backend.
        debug_file: Path to save debug events (default: ./evoke_events.json)
        realtime: Send events immediately (default: True).
        buffer_size: Number of events to buffer before sending
        flush_interval: Seconds between automatic flushes
        user_id: Optional user identifier for all events
        tenant_id: Optional tenant/organization identifier for all events
        environment: Optional environment name (production, staging, dev)
        application: Optional application name
        agent_version: Optional version of the agent application
        policy: Security policy mode - "monitor" (default), "enforce", or "off"
        redact: Types of sensitive data to redact - True/False or list of types
        sync_signatures: Enable signature sync from platform (default: True)
        signature_poll_interval: Seconds between signature polls (default: 300)
        sync_policies: Enable SDK policy sync from platform (default: True)
        policy_poll_interval: Seconds between policy polls (default: 300)
        enable_ml_detection: Enable ML-based detection (default: True)
        detection_model: Path to custom ML model (optional)
    """
    if is_initialized():
        logger.warning("Evoke SDK already initialized")
        return

    # In debug mode, API key is not required
    if not debug:
        if not api_key:
            raise ValueError("API key is required (or use debug=True for local testing)")
        if not api_key.startswith("evoke_pk_"):
            logger.warning("API key should start with 'evoke_pk_' prefix")

    # Store config
    config = Config.get()
    config.api_key = api_key
    config.endpoint = endpoint.rstrip("/")
    config.debug = debug
    config.sync_signatures = sync_signatures
    config.signature_poll_interval = signature_poll_interval
    config.sync_policies = sync_policies
    config.policy_poll_interval = policy_poll_interval
    config.enable_ml_detection = enable_ml_detection
    config.detection_model = detection_model

    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger("evoke").setLevel(logging.DEBUG)

    logger.info("Evoke SDK initializing...")

    # Collect system info (cached for all events)
    from evoke.core.system_info import init_system_info
    system_info = init_system_info(fetch_public_ip=not debug)
    logger.debug(f"System info collected: hostname={system_info.hostname}, ip={system_info.ip_address}")

    # Set up transport
    from evoke.core.transport import EventTransport, FileTransport, set_transport

    if debug:
        file_path = debug_file or "./evoke_events.json"
        transport = FileTransport(file_path=file_path)
        logger.info(f"Debug mode: Events will be saved to {file_path}")
    else:
        transport = EventTransport(
            endpoint=config.endpoint,
            api_key=config.api_key,
            realtime=realtime,
            buffer_size=buffer_size,
            flush_interval=flush_interval,
        )
    set_transport(transport)

    # Set user identity if provided
    if user_id or tenant_id:
        from evoke.core.session import identity
        identity(user_id=user_id, organization_id=tenant_id)

    # Set policy configuration if provided
    if policy is not None or redact:
        from evoke.core.session import set_policy_config
        from evoke.schema import PolicyConfig
        policy_config = PolicyConfig(
            mode=policy or "monitor",
            redact=redact,
        )
        set_policy_config(policy_config)
        config.policy = policy_config

    # Initialize signature sync (if not debug mode)
    if sync_signatures and not debug:
        try:
            from evoke.sync import SignatureManager
            signature_manager = SignatureManager(
                endpoint=config.endpoint,
                api_key=config.api_key,
                poll_interval=signature_poll_interval,
            )
            signature_manager.sync_on_init()
            signature_manager.start_polling()
            logger.debug("Signature sync initialized")
        except Exception as e:
            logger.debug(f"Signature sync not available: {e}")

    # Initialize policy sync (if not debug mode)
    global _policy_manager
    if sync_policies and not debug:
        try:
            from evoke.sync import PolicyManager
            _policy_manager = PolicyManager(
                endpoint=config.endpoint,
                api_key=config.api_key,
                poll_interval=policy_poll_interval,
            )
            _policy_manager.sync_on_init()
            _policy_manager.start_polling()
            logger.debug("Policy sync initialized")
        except Exception as e:
            logger.debug(f"Policy sync not available: {e}")

    # Initialize detection engine
    try:
        from evoke.detection import get_detection_engine
        engine = get_detection_engine(
            enable_ml=enable_ml_detection,
            model_path=detection_model,
        )
        logger.debug("Detection engine initialized")
    except Exception as e:
        logger.debug(f"Detection engine initialization: {e}")

    # Auto-instrument all available model SDKs
    from evoke.wrappers import auto_instrument
    instrumentors = auto_instrument()

    set_initialized(True)

    if debug:
        logger.info(f"Evoke SDK initialized (debug mode -> {debug_file or './evoke_events.json'})")
    else:
        logger.info(f"Evoke SDK initialized (backend: {config.endpoint})")
    if instrumentors:
        logger.info(f"Instrumented: {', '.join(instrumentors)}")


def flush() -> None:
    """
    Force send all buffered events to the backend.
    The SDK automatically flushes events periodically and on exit.
    """
    from evoke.core.transport import get_transport

    transport = get_transport()
    if transport:
        transport.flush()
        logger.debug("Flushed all pending events")
    else:
        logger.warning("Evoke SDK not initialized - nothing to flush")


def get_system_info() -> dict:
    """
    Get system information for enriching events.

    Note: System info is now auto-attached to all events.
    This function is kept for backward compatibility and manual access.

    Returns:
        Dictionary with comprehensive system information
    """
    from evoke.core.system_info import get_cached_system_info, collect_system_info

    cached = get_cached_system_info()
    if cached:
        return cached.to_dict()

    # If not cached (SDK not initialized), collect fresh
    return collect_system_info(fetch_public_ip=False).to_dict()
