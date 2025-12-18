"""
Evoke Security - Policy enforcement logic
"""
from typing import List
from evoke.schema import Detection


def get_highest_severity(detections: List[Detection]) -> str:
    """Get the highest severity from a list of detections"""
    if not detections:
        return "none"

    severity_order = ["critical", "high", "medium", "low", "info"]
    for sev in severity_order:
        if any(d.severity == sev for d in detections):
            return sev
    return "none"


def determine_safe(severity: str) -> bool:
    """
    Determine if content is safe based on severity level.

    Safe: none, info, low
    Unsafe: medium, high, critical
    """
    return severity in ("none", "info", "low")
