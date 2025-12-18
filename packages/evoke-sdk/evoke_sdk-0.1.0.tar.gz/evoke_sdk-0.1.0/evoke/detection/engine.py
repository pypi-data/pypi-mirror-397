"""
Evoke Detection - Main detection engine orchestrator
"""
from typing import List, Optional, Dict, Any
import logging

from evoke.schema import Detection
from evoke.detection.rules import get_registry, RuleRegistry
from evoke.detection.ml import MLEngine

logger = logging.getLogger(__name__)


class DetectionEngine:
    """
    Orchestrates rule-based and ML-based detection.

    Detection flow:
    1. RuleEngine runs first (fast regex patterns)
    2. If no critical detections, MLEngine runs (optional)
    3. Results merged and deduplicated
    4. Sorted by severity
    """

    def __init__(
        self,
        enable_ml: bool = True,
        model_path: Optional[str] = None,
    ):
        self.rule_registry = get_registry()
        self.ml_engine = MLEngine(enable=enable_ml, model_path=model_path)
        logger.debug(f"Detection engine initialized (rules={self.rule_registry.rule_count}, ml={enable_ml})")

    def analyze(
        self,
        content: str,
        context: Optional[Dict] = None,
        use_ml: bool = True,
    ) -> List[Detection]:
        """
        Run detection pipeline.

        Args:
            content: Text content to analyze
            context: Optional context for detection
            use_ml: Whether to run ML classification

        Returns:
            List of Detection objects sorted by severity
        """
        detections = []

        # Fast path: rule-based detection
        rule_detections = self.rule_registry.run_all(content, context)
        detections.extend(rule_detections)

        # ML path: if enabled and no critical rules triggered
        if use_ml and not self._has_critical_detection(rule_detections):
            ml_detections = self.ml_engine.classify(content, context)
            detections.extend(ml_detections)

        return self._deduplicate_and_sort(detections)

    def _has_critical_detection(self, detections: List[Detection]) -> bool:
        """Check if any detection is critical severity."""
        return any(d.severity == "critical" for d in detections)

    def _deduplicate_and_sort(self, detections: List[Detection]) -> List[Detection]:
        """Remove duplicates and sort by severity."""
        # Deduplicate by (rule_id, position)
        seen = set()
        unique = []
        for d in detections:
            key = (d.rule_id, d.position)
            if key not in seen:
                seen.add(key)
                unique.append(d)

        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        return sorted(unique, key=lambda d: severity_order.get(d.severity, 5))

    def add_rule(self, rule) -> None:
        """Add a custom detection rule."""
        self.rule_registry.add_rule(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a detection rule."""
        return self.rule_registry.remove_rule(rule_id)

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a detection rule."""
        return self.rule_registry.enable_rule(rule_id)

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a detection rule."""
        return self.rule_registry.disable_rule(rule_id)

    def sync_signatures(self) -> None:
        """Trigger signature sync from platform."""
        try:
            from evoke.sync import get_signature_manager
            manager = get_signature_manager()
            if manager:
                manager.sync_now()
        except ImportError:
            logger.debug("Signature sync not available")

    @property
    def rule_count(self) -> int:
        """Number of registered rules."""
        return self.rule_registry.rule_count

    @property
    def ml_available(self) -> bool:
        """Check if ML classification is available."""
        return self.ml_engine.is_available


# Global detection engine instance
_engine: Optional[DetectionEngine] = None


def get_detection_engine(
    enable_ml: bool = True,
    model_path: Optional[str] = None,
) -> DetectionEngine:
    """Get or create the global detection engine."""
    global _engine
    if _engine is None:
        _engine = DetectionEngine(enable_ml=enable_ml, model_path=model_path)
    return _engine


def reset_detection_engine() -> None:
    """Reset the global detection engine (for testing)."""
    global _engine
    _engine = None
