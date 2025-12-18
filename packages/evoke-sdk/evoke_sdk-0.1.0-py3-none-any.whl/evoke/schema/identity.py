"""
Evoke Schema - Identity and policy configuration
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Identity:
    """
    Client application identity metadata for event attribution.

    IMPORTANT: This represents YOUR end users (your application's users),
    NOT Evoke platform users. Use this to track which of your users
    triggered AI events in your application.
    """
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    organization_id: Optional[str] = None
    organization_type: Optional[str] = None
    role: Optional[str] = None
    access_level: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class PolicyConfig:
    """Configuration for security policy behavior"""
    mode: str = "monitor"  # "monitor" | "enforce" | "off"
    redact: Any = False  # True/False or list of types to redact

    def should_redact(self, detection_type: str) -> bool:
        """Check if a detection type should be redacted"""
        if isinstance(self.redact, bool):
            return self.redact
        if isinstance(self.redact, list):
            return detection_type in self.redact
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"mode": self.mode, "redact": self.redact}
