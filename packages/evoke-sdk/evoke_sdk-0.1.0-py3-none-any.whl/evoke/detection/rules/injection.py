"""
Evoke Detection - Prompt injection detection rules
"""
from evoke.detection.rules.base import RegexRule, KeywordRule

# Prompt Injection Detection Rules
INJECTION_RULES = [
    RegexRule(
        rule_id="injection_ignore_previous",
        name="Ignore Previous Instructions",
        pattern=r"ignore\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|context|rules?|guidelines?)",
        category="prompt_injection",
        severity="high",
        confidence=0.85,
    ),
    RegexRule(
        rule_id="injection_new_instructions",
        name="New Instructions Override",
        pattern=r"(?:new|real|actual|true)\s+instructions?\s*(?:are|:)",
        category="prompt_injection",
        severity="high",
        confidence=0.8,
    ),
    RegexRule(
        rule_id="injection_system_override",
        name="System Role Override",
        pattern=r"(?:system|admin|root)\s*(?:prompt|message|role)\s*[:=]",
        category="prompt_injection",
        severity="high",
        confidence=0.85,
    ),
    RegexRule(
        rule_id="injection_role_play",
        name="Role Play Injection",
        pattern=r"(?:pretend|act|imagine|roleplay|role-play)\s+(?:you\s+are|to\s+be|as)\s+(?:a|an)?\s*(?:different|new|evil|malicious|unrestricted)",
        category="prompt_injection",
        severity="medium",
        confidence=0.75,
    ),
    RegexRule(
        rule_id="injection_developer_mode",
        name="Developer Mode Injection",
        pattern=r"(?:developer|dev|debug|test)\s*mode\s*(?:enabled?|activated?|on)",
        category="prompt_injection",
        severity="medium",
        confidence=0.8,
    ),
    RegexRule(
        rule_id="injection_jailbreak_dan",
        name="DAN Jailbreak",
        pattern=r"\bDAN\b.*(?:do\s+anything\s+now|jailbreak)",
        category="jailbreak",
        severity="high",
        confidence=0.9,
    ),
    RegexRule(
        rule_id="injection_bypass_filters",
        name="Filter Bypass Attempt",
        pattern=r"(?:bypass|circumvent|ignore|disable|turn\s+off)\s+(?:filters?|safety|guardrails?|restrictions?|limitations?)",
        category="prompt_injection",
        severity="high",
        confidence=0.85,
    ),
    RegexRule(
        rule_id="injection_encoding",
        name="Encoded Injection",
        pattern=r"(?:base64|hex|rot13|unicode)\s*(?:decode|encoded?)\s*[:=]",
        category="prompt_injection",
        severity="medium",
        confidence=0.7,
    ),
]

# Jailbreak Keywords
JAILBREAK_KEYWORDS = KeywordRule(
    rule_id="jailbreak_keywords",
    name="Jailbreak Keywords",
    keywords=[
        "jailbreak",
        "DAN",
        "do anything now",
        "ignore your training",
        "unrestricted mode",
        "no limitations",
        "hypothetically",
        "pretend there are no rules",
    ],
    category="jailbreak",
    severity="high",
    confidence=0.75,
)

# All injection rules
ALL_INJECTION_RULES = INJECTION_RULES + [JAILBREAK_KEYWORDS]
