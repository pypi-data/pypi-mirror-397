"""
Evoke Sync - Policy condition evaluator
"""
from typing import List, Dict, Any, Optional
import re
import logging

from evoke.schema.policy import PolicyMatch

logger = logging.getLogger(__name__)


class PolicyEvaluator:
    """
    Evaluates content against policy conditions.

    Policies have conditions with 'all' (AND) and 'any' (OR) logic.
    Each condition specifies a field, operator, and value to check.
    """

    def evaluate(
        self,
        content: str,
        policies: List[dict],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[PolicyMatch]:
        """
        Evaluate content against all policies.

        Args:
            content: The content to evaluate (e.g., user input, LLM output)
            policies: List of policy dicts from the backend
            context: Optional context dict with additional fields to check

        Returns:
            List of PolicyMatch objects for policies that matched
        """
        matches = []
        context = context or {}

        # Build evaluation context - content is the primary field
        eval_context = {
            "content": content,
            "input": {"messages": {"content": content}},  # For field paths like "input.messages.content"
            **context,
        }

        for policy in policies:
            # Skip disabled policies
            if not policy.get("enabled", True):
                continue

            matched_conditions = self._evaluate_policy(policy, eval_context)
            if matched_conditions:
                match = PolicyMatch.from_policy(policy, matched_conditions)
                matches.append(match)
                logger.debug(f"Policy matched: {policy.get('name')} ({policy.get('policy_id')})")

        return matches

    def _evaluate_policy(
        self,
        policy: dict,
        context: Dict[str, Any],
    ) -> List[dict]:
        """
        Evaluate a single policy against the context.

        Returns list of matched conditions if policy matches, empty list otherwise.
        """
        conditions = policy.get("conditions", {})
        all_conditions = conditions.get("all") or []
        any_conditions = conditions.get("any") or []

        matched = []

        # Evaluate 'all' conditions (AND logic) - all must match
        if all_conditions:
            all_matched = []
            for condition in all_conditions:
                if self._evaluate_condition(condition, context):
                    all_matched.append(condition)
                else:
                    # If any 'all' condition fails, the whole policy fails
                    return []
            matched.extend(all_matched)

        # Evaluate 'any' conditions (OR logic) - at least one must match
        if any_conditions:
            any_matched = []
            for condition in any_conditions:
                if self._evaluate_condition(condition, context):
                    any_matched.append(condition)

            # If there are 'any' conditions but none matched, policy fails
            if any_conditions and not any_matched:
                return []
            matched.extend(any_matched)

        # If no conditions defined, policy doesn't match
        if not all_conditions and not any_conditions:
            return []

        return matched

    def _evaluate_condition(
        self,
        condition: dict,
        context: Dict[str, Any],
    ) -> bool:
        """
        Evaluate a single condition against the context.

        Condition format:
        {
            "field": "input.messages.content",
            "operator": "contains",
            "value": "Ignore all previous instructions",
            "array_quantifier": "any"  # optional, for array fields
        }
        """
        field_path = condition.get("field", "")
        operator = condition.get("operator", "contains")
        condition_value = condition.get("value", "")
        array_quantifier = condition.get("array_quantifier", "any")

        # Get the field value from context
        field_value = self._get_field_value(field_path, context)

        if field_value is None:
            return False

        # Handle array fields
        if isinstance(field_value, list):
            if array_quantifier == "all":
                return all(
                    self._check_operator(operator, item, condition_value)
                    for item in field_value
                )
            else:  # "any" is default
                return any(
                    self._check_operator(operator, item, condition_value)
                    for item in field_value
                )

        # Single value
        return self._check_operator(operator, field_value, condition_value)

    def _get_field_value(
        self,
        field_path: str,
        context: Dict[str, Any],
    ) -> Any:
        """
        Get a value from context using dot-notation path.

        Examples:
            "content" -> context["content"]
            "input.messages.content" -> context["input"]["messages"]["content"]
        """
        if not field_path:
            return None

        parts = field_path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value

    def _check_operator(
        self,
        operator: str,
        field_value: Any,
        condition_value: Any,
    ) -> bool:
        """
        Check if field_value matches condition_value using the operator.

        Supported operators:
        - contains: string contains substring (case-insensitive)
        - equals: exact match
        - not_equals: not equal
        - starts_with: string starts with prefix
        - ends_with: string ends with suffix
        - regex: regex pattern match
        - in: value in list
        - not_in: value not in list
        - gt: greater than (numeric)
        - gte: greater than or equal
        - lt: less than (numeric)
        - lte: less than or equal
        """
        # Convert to strings for string operations
        str_field = str(field_value) if field_value is not None else ""
        str_condition = str(condition_value) if condition_value is not None else ""

        operator = operator.lower()

        if operator == "contains":
            return str_condition.lower() in str_field.lower()

        elif operator == "equals":
            return str_field.lower() == str_condition.lower()

        elif operator == "not_equals":
            return str_field.lower() != str_condition.lower()

        elif operator == "starts_with":
            return str_field.lower().startswith(str_condition.lower())

        elif operator == "ends_with":
            return str_field.lower().endswith(str_condition.lower())

        elif operator == "regex":
            try:
                return bool(re.search(str_condition, str_field, re.IGNORECASE))
            except re.error:
                logger.warning(f"Invalid regex pattern: {str_condition}")
                return False

        elif operator == "in":
            if isinstance(condition_value, list):
                return field_value in condition_value
            return False

        elif operator == "not_in":
            if isinstance(condition_value, list):
                return field_value not in condition_value
            return True

        elif operator == "gt":
            try:
                return float(field_value) > float(condition_value)
            except (ValueError, TypeError):
                return False

        elif operator == "gte":
            try:
                return float(field_value) >= float(condition_value)
            except (ValueError, TypeError):
                return False

        elif operator == "lt":
            try:
                return float(field_value) < float(condition_value)
            except (ValueError, TypeError):
                return False

        elif operator == "lte":
            try:
                return float(field_value) <= float(condition_value)
            except (ValueError, TypeError):
                return False

        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
