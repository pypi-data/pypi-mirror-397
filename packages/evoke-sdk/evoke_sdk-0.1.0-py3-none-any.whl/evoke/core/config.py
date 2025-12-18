"""
Evoke Core - Configuration singleton for SDK state
"""
from typing import Optional
from evoke.schema import PolicyConfig


class Config:
    """Global SDK configuration singleton"""

    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.api_key: Optional[str] = None
        self.endpoint: Optional[str] = None
        self.debug: bool = False
        self.policy: Optional[PolicyConfig] = None

        # Sync configuration
        self.sync_signatures: bool = True
        self.signature_poll_interval: int = 300
        self.sync_policies: bool = True
        self.policy_poll_interval: int = 300

        # Detection configuration
        self.enable_ml_detection: bool = True
        self.detection_model: Optional[str] = None

        self._initialized = True

    @classmethod
    def get(cls) -> "Config":
        """Get the config singleton"""
        return cls()

    @classmethod
    def reset(cls) -> None:
        """Reset config (for testing)"""
        cls._instance = None


# Global state
_initialized = False


def is_initialized() -> bool:
    """Check if SDK is initialized"""
    return _initialized


def set_initialized(value: bool) -> None:
    """Set initialization state"""
    global _initialized
    _initialized = value
