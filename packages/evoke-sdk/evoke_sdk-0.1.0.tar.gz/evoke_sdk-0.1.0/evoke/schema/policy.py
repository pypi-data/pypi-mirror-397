"""
Evoke Schema - Policy evaluation models
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PolicyMatch:
    """Result of a policy match against content."""

    policy_id: str
    policy_name: str
    severity: str
    category: str
    remediation: str
    matched_conditions: List[dict] = field(default_factory=list)
    applies_to: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_id": self.policy_id,
            "policy_name": self.policy_name,
            "severity": self.severity,
            "category": self.category,
            "remediation": self.remediation,
            "matched_conditions": self.matched_conditions,
            "applies_to": self.applies_to,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_policy(cls, policy: dict, matched_conditions: List[dict]) -> "PolicyMatch":
        """Create a PolicyMatch from a policy dict and matched conditions."""
        return cls(
            policy_id=policy.get("policy_id") or policy.get("id", "unknown"),
            policy_name=policy.get("name", "Unknown Policy"),
            severity=policy.get("severity", "medium"),
            category=policy.get("category", "unknown"),
            remediation=policy.get("remediation", ""),
            matched_conditions=matched_conditions,
            applies_to=policy.get("applies_to", {}),
            description=policy.get("description"),
            tags=policy.get("tags", []),
        )
