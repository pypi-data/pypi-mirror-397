"""
Evoke Detection - PII and credential detection patterns
"""
from evoke.detection.rules.base import RegexRule

# PII Detection Rules
PII_RULES = [
    RegexRule(
        rule_id="pii_ssn",
        name="Social Security Number",
        pattern=r"\b\d{3}-\d{2}-\d{4}\b",
        category="pii",
        severity="high",
        confidence=0.95,
    ),
    RegexRule(
        rule_id="pii_credit_card",
        name="Credit Card Number",
        pattern=r"\b(?:\d{4}[- ]?){3}\d{4}\b",
        category="pii",
        severity="high",
        confidence=0.9,
    ),
    RegexRule(
        rule_id="pii_email",
        name="Email Address",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        category="pii",
        severity="medium",
        confidence=0.95,
    ),
    RegexRule(
        rule_id="pii_phone",
        name="Phone Number",
        pattern=r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b",
        category="pii",
        severity="medium",
        confidence=0.8,
    ),
    RegexRule(
        rule_id="pii_ip_address",
        name="IP Address",
        pattern=r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        category="pii",
        severity="low",
        confidence=0.9,
    ),
]

# Credential Detection Rules
CREDENTIAL_RULES = [
    RegexRule(
        rule_id="credential_openai_key",
        name="OpenAI API Key",
        pattern=r"\bsk-[A-Za-z0-9]{48}\b",
        category="credentials",
        severity="critical",
        confidence=0.99,
    ),
    RegexRule(
        rule_id="credential_anthropic_key",
        name="Anthropic API Key",
        pattern=r"\bsk-ant-[A-Za-z0-9-]{90,}\b",
        category="credentials",
        severity="critical",
        confidence=0.99,
    ),
    RegexRule(
        rule_id="credential_aws_key",
        name="AWS Access Key",
        pattern=r"\bAKIA[A-Z0-9]{16}\b",
        category="credentials",
        severity="critical",
        confidence=0.99,
    ),
    RegexRule(
        rule_id="credential_stripe_key",
        name="Stripe API Key",
        pattern=r"\b(?:sk_live_|pk_live_|sk_test_|pk_test_)[A-Za-z0-9]{24,}\b",
        category="credentials",
        severity="critical",
        confidence=0.99,
    ),
    RegexRule(
        rule_id="credential_github_token",
        name="GitHub Token",
        pattern=r"\b(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{36,}\b",
        category="credentials",
        severity="critical",
        confidence=0.99,
    ),
    RegexRule(
        rule_id="credential_generic_api_key",
        name="Generic API Key Pattern",
        pattern=r"\b(?:api[_-]?key|apikey|api[_-]?secret)[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9_-]{20,})[\"']?\b",
        category="credentials",
        severity="high",
        confidence=0.7,
    ),
    RegexRule(
        rule_id="credential_password",
        name="Password Pattern",
        pattern=r"\b(?:password|passwd|pwd)[\"']?\s*[:=]\s*[\"']?([^\s\"']{8,})[\"']?\b",
        category="credentials",
        severity="high",
        confidence=0.6,
    ),
]

# All pattern rules
ALL_PATTERN_RULES = PII_RULES + CREDENTIAL_RULES
