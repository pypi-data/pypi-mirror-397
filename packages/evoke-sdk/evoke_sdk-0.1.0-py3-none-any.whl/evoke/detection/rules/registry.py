"""
Evoke Detection - Rule registry for managing detection rules
"""
from typing import List, Dict, Optional, TYPE_CHECKING
import logging

from evoke.schema import Detection

if TYPE_CHECKING:
    from evoke.detection.rules.base import DetectionRule

logger = logging.getLogger(__name__)


class RuleRegistry:
    """Registry for managing detection rules."""

    def __init__(self):
        self._rules: Dict[str, "DetectionRule"] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy load built-in rules on first access."""
        if self._loaded:
            return
        self._loaded = True
        # Import rules lazily to avoid startup overhead
        from evoke.detection.rules.patterns import ALL_PATTERN_RULES
        from evoke.detection.rules.injection import ALL_INJECTION_RULES
        for rule in ALL_PATTERN_RULES:
            self._rules[rule.rule_id] = rule
        for rule in ALL_INJECTION_RULES:
            self._rules[rule.rule_id] = rule
        logger.debug(f"Loaded {len(self._rules)} built-in rules")

    def add_rule(self, rule: "DetectionRule") -> None:
        """Add a rule to the registry."""
        self._ensure_loaded()
        self._rules[rule.rule_id] = rule
        logger.debug(f"Added rule: {rule.rule_id}")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule from the registry."""
        self._ensure_loaded()
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def get_rule(self, rule_id: str) -> Optional["DetectionRule"]:
        """Get a rule by ID."""
        self._ensure_loaded()
        return self._rules.get(rule_id)

    def get_rules_by_category(self, category: str) -> List["DetectionRule"]:
        """Get all rules in a category."""
        self._ensure_loaded()
        return [r for r in self._rules.values() if r.category == category]

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        self._ensure_loaded()
        rule = self._rules.get(rule_id)
        if rule:
            rule.enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        self._ensure_loaded()
        rule = self._rules.get(rule_id)
        if rule:
            rule.enabled = False
            return True
        return False

    def run_all(self, content: str, context: Optional[dict] = None) -> List[Detection]:
        """Run all enabled rules on content."""
        self._ensure_loaded()
        detections = []
        for rule in self._rules.values():
            if rule.enabled:
                try:
                    rule_detections = rule.detect(content, context)
                    detections.extend(rule_detections)
                except Exception as e:
                    logger.warning(f"Rule {rule.rule_id} failed: {e}")
        return detections

    @property
    def rule_count(self) -> int:
        """Number of registered rules."""
        self._ensure_loaded()
        return len(self._rules)

    @property
    def enabled_rule_count(self) -> int:
        """Number of enabled rules."""
        self._ensure_loaded()
        return sum(1 for r in self._rules.values() if r.enabled)


# Global registry instance
_registry: Optional[RuleRegistry] = None


def get_registry() -> RuleRegistry:
    """Get the global rule registry."""
    global _registry
    if _registry is None:
        _registry = RuleRegistry()
    return _registry
