"""
Evoke Detection - Base rule interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import re

from evoke.schema import Detection


class DetectionRule(ABC):
    """Base class for detection rules."""

    rule_id: str
    rule_name: str
    category: str
    severity: str  # critical, high, medium, low, info
    enabled: bool = True

    @abstractmethod
    def detect(self, content: str, context: Optional[dict] = None) -> List[Detection]:
        """Run detection on content."""
        pass


class RegexRule(DetectionRule):
    """Rule based on regex pattern matching."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        pattern: str,
        category: str,
        severity: str,
        confidence: float = 0.9,
        flags: int = re.IGNORECASE,
    ):
        self.rule_id = rule_id
        self.rule_name = name
        self.pattern = re.compile(pattern, flags)
        self.category = category
        self.severity = severity
        self.confidence = confidence
        self.enabled = True

    def detect(self, content: str, context: Optional[dict] = None) -> List[Detection]:
        detections = []
        for match in self.pattern.finditer(content):
            detections.append(Detection(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                category=self.category,
                severity=self.severity,
                confidence=self.confidence,
                evidence=match.group(0)[:100],  # Truncate evidence
                position=(match.start(), match.end()),
            ))
        return detections


class KeywordRule(DetectionRule):
    """Rule based on keyword matching."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        keywords: List[str],
        category: str,
        severity: str,
        confidence: float = 0.8,
        case_sensitive: bool = False,
    ):
        self.rule_id = rule_id
        self.rule_name = name
        self.keywords = keywords if case_sensitive else [k.lower() for k in keywords]
        self.category = category
        self.severity = severity
        self.confidence = confidence
        self.case_sensitive = case_sensitive
        self.enabled = True

    def detect(self, content: str, context: Optional[dict] = None) -> List[Detection]:
        detections = []
        search_content = content if self.case_sensitive else content.lower()

        for keyword in self.keywords:
            start = 0
            while True:
                pos = search_content.find(keyword, start)
                if pos == -1:
                    break
                detections.append(Detection(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    category=self.category,
                    severity=self.severity,
                    confidence=self.confidence,
                    evidence=content[pos:pos + len(keyword)],
                    position=(pos, pos + len(keyword)),
                ))
                start = pos + 1

        return detections
