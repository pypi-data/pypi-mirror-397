"""
Evoke Schema - Detection and analysis result structures
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from evoke.schema.policy import PolicyMatch


@dataclass
class Detection:
    """Result of running a detection rule"""
    rule_id: str
    rule_name: str
    category: str
    severity: str  # critical, high, medium, low, info
    confidence: float  # 0.0 - 1.0
    evidence: str  # The matched text/pattern
    position: Optional[tuple] = None  # (start, end) position in text
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """Result of content analysis through the detection engine"""
    content: str
    safe: bool = True
    severity: str = "none"  # none, info, low, medium, high, critical
    detections: List[Detection] = field(default_factory=list)
    policy_matches: List["PolicyMatch"] = field(default_factory=list)
    analyzed_at: Optional[datetime] = None
    analysis_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "safe": self.safe,
            "severity": self.severity,
            "detections": [d.to_dict() for d in self.detections],
            "policy_matches": [p.to_dict() for p in self.policy_matches],
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "analysis_id": self.analysis_id,
        }

    @property
    def has_detections(self) -> bool:
        """Check if any detections were found"""
        return len(self.detections) > 0

    @staticmethod
    def determine_safe(severity: str) -> bool:
        """Determine if content is safe based on severity level"""
        return severity in ("none", "info", "low")
