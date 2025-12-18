"""
Evoke Security - Content analysis function
"""
from typing import Optional, List
from datetime import datetime
from threading import Thread
import uuid
import logging

from evoke.schema import EventType, AnalysisResult, Detection, PolicyMatch
from evoke.functions.policy import get_highest_severity, determine_safe

logger = logging.getLogger(__name__)

# 24 hours in seconds - max staleness for policy sync
POLICY_MAX_AGE_SECONDS = 86400


def analyze(
    content: str,
    wait: bool = True,
) -> Optional[AnalysisResult]:
    """
    Analyze text content through the detection engine.

    Runs detection rules locally (fast) and optionally ML classification.

    Args:
        content: The text content to analyze (must be a string)
        wait: If True (default), block and return AnalysisResult.
              If False, send for analysis asynchronously and return None.

    Returns:
        AnalysisResult if wait=True, None if wait=False

    Raises:
        TypeError: If content is not a string

    Example:
        result = evoke.analyze("Check this user input for threats")
        if result.safe:
            proceed_with_action()
        else:
            print(f"Blocked! Severity: {result.severity}")
    """
    if not isinstance(content, str):
        raise TypeError(f"content must be a string, got {type(content).__name__}")

    from evoke.core.config import is_initialized
    from evoke.core.session import get_policy_config

    if not is_initialized():
        logger.warning("Evoke SDK not initialized - analysis may not be sent")

    policy = get_policy_config()

    if policy and policy.mode == "off":
        logger.debug("Policy mode is 'off', skipping analysis")
        if wait:
            return AnalysisResult(
                content=content,
                safe=True,
                severity="none",
                analyzed_at=datetime.utcnow(),
            )
        return None

    if wait:
        return _analyze_sync(content, policy)
    else:
        _analyze_async(content, policy)
        return None


def _run_detection(content: str) -> List[Detection]:
    """
    Run detection rules on content using the detection engine.
    """
    try:
        from evoke.detection import get_detection_engine
        engine = get_detection_engine()
        return engine.analyze(content)
    except Exception as e:
        logger.debug(f"Detection engine not available: {e}")
        return []


def _evaluate_policies(content: str) -> List[PolicyMatch]:
    """
    Evaluate content against synced policies.

    Automatically refreshes policies if older than 24 hours.
    """
    try:
        from evoke.core.client import get_policy_manager
        policy_manager = get_policy_manager()

        if not policy_manager:
            logger.debug("Policy manager not available")
            return []

        # Refresh if older than 24 hours
        policy_manager.sync_before_operation(max_age_seconds=POLICY_MAX_AGE_SECONDS)

        # Evaluate content against policies
        return policy_manager.evaluate(content)
    except Exception as e:
        logger.debug(f"Policy evaluation error: {e}")
        return []


def _analyze_sync(content: str, policy) -> AnalysisResult:
    """
    Synchronous analysis - runs local detection and policy evaluation.
    """
    from evoke.functions.capture import capture

    analysis_id = str(uuid.uuid4())

    # Run detection rules
    detections = _run_detection(content)

    # Evaluate against policies (auto-refreshes if >24hr stale)
    policy_matches = _evaluate_policies(content)

    # Determine severity from detections
    detection_severity = get_highest_severity(detections)

    # Get highest severity from policy matches
    policy_severity = "none"
    if policy_matches:
        severity_order = ["none", "info", "low", "medium", "high", "critical"]
        for match in policy_matches:
            match_sev = match.severity.lower() if match.severity else "none"
            if match_sev in severity_order:
                if severity_order.index(match_sev) > severity_order.index(policy_severity):
                    policy_severity = match_sev

    # Overall severity is the higher of detection vs policy
    severity_order = ["none", "info", "low", "medium", "high", "critical"]
    if severity_order.index(policy_severity) > severity_order.index(detection_severity):
        severity = policy_severity
    else:
        severity = detection_severity

    safe = determine_safe(severity)

    # Create result
    result = AnalysisResult(
        content=content,
        safe=safe,
        severity=severity,
        detections=detections,
        policy_matches=policy_matches,
        analyzed_at=datetime.utcnow(),
        analysis_id=analysis_id,
    )

    # Capture the analysis event
    capture(
        event_type=EventType.CONTENT_ANALYSIS,
        input=content,
        output=f"safe={safe}, severity={severity}, detections={len(detections)}, policy_matches={len(policy_matches)}",
        metadata={
            "analysis_id": analysis_id,
            "analysis_mode": "sync",
            "safe": safe,
            "severity": severity,
            "detection_count": len(detections),
            "policy_match_count": len(policy_matches),
            "policy_mode": policy.mode if policy else "monitor",
        },
    )

    return result


def _analyze_async(content: str, policy) -> None:
    """Asynchronous analysis - fire and forget"""

    def send_analysis():
        from evoke.functions.capture import capture

        detections = _run_detection(content)
        policy_matches = _evaluate_policies(content)

        # Determine severity from detections
        detection_severity = get_highest_severity(detections)

        # Get highest severity from policy matches
        policy_severity = "none"
        if policy_matches:
            severity_order = ["none", "info", "low", "medium", "high", "critical"]
            for match in policy_matches:
                match_sev = match.severity.lower() if match.severity else "none"
                if match_sev in severity_order:
                    if severity_order.index(match_sev) > severity_order.index(policy_severity):
                        policy_severity = match_sev

        # Overall severity
        severity_order = ["none", "info", "low", "medium", "high", "critical"]
        if severity_order.index(policy_severity) > severity_order.index(detection_severity):
            severity = policy_severity
        else:
            severity = detection_severity

        safe = determine_safe(severity)

        capture(
            event_type=EventType.CONTENT_ANALYSIS,
            input=content,
            output=f"safe={safe}, severity={severity}, detections={len(detections)}, policy_matches={len(policy_matches)}",
            metadata={
                "analysis_mode": "async",
                "safe": safe,
                "severity": severity,
                "detection_count": len(detections),
                "policy_match_count": len(policy_matches),
                "policy_mode": policy.mode if policy else "monitor",
            },
        )

    Thread(target=send_analysis, daemon=True).start()
