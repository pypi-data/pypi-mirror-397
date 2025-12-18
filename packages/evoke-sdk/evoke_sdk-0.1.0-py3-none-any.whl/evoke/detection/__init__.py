"""
Evoke Detection - Detection engine for content analysis
"""
from evoke.detection.engine import (
    DetectionEngine,
    get_detection_engine,
    reset_detection_engine,
)
from evoke.detection.rules import (
    DetectionRule,
    RegexRule,
    KeywordRule,
    RuleRegistry,
    get_registry,
)
from evoke.detection.ml import MLClassifier, MLEngine

__all__ = [
    # Engine
    "DetectionEngine",
    "get_detection_engine",
    "reset_detection_engine",
    # Rules
    "DetectionRule",
    "RegexRule",
    "KeywordRule",
    "RuleRegistry",
    "get_registry",
    # ML
    "MLClassifier",
    "MLEngine",
]
