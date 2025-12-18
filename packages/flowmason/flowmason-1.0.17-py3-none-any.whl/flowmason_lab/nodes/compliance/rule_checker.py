"""
Rule Checker Node - Compliance Component.

Evaluates data against structured compliance rules using
deterministic pattern matching and threshold checks.
"""

import re
from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput


@operator(
    name="rule_checker",
    category="compliance",
    description="Evaluate data against structured compliance rules (regex, thresholds, patterns)",
    icon="shield-check",
    color="#EF4444",  # Red for compliance
    version="1.0.0",
    author="FlowMason",
    tags=["compliance", "rules", "validation", "pii", "security"],
)
class RuleCheckerOperator:
    """
    Check data against structured compliance rules.

    The Rule Checker provides fast, deterministic rule evaluation
    using pattern matching, thresholds, and expressions.

    Rule Types:
    - regex: Pattern matching (SSN, credit cards, emails)
    - threshold: Numeric comparisons (amount > limit)
    - contains: Substring/keyword detection
    - expression: Custom boolean expressions

    Use cases:
    - PII detection (SSN, credit cards, emails)
    - Financial limit enforcement
    - Content policy validation
    - Data quality checks
    - Security scanning
    - Input sanitization

    This is the deterministic layer of a hybrid compliance system.
    For semantic/contextual checks, use policy_lookup + compliance_evaluator.
    """

    class Input(OperatorInput):
        data: Dict[str, Any] = Field(
            description="Data to check against rules",
            examples=[
                {"customer_email": "test@example.com", "amount": 5000},
                {"message": "My SSN is 123-45-6789"},
            ],
        )
        rules: List[Dict[str, Any]] = Field(
            description="Rules to evaluate. Each rule has: id, name, type, condition, severity, action, message",
            examples=[[
                {
                    "id": "ssn-detection",
                    "name": "SSN Detection",
                    "type": "regex",
                    "field": "message",
                    "pattern": r"\d{3}-\d{2}-\d{4}",
                    "severity": "critical",
                    "action": "block",
                    "message": "Social Security Number detected"
                },
                {
                    "id": "amount-limit",
                    "name": "Transaction Limit",
                    "type": "threshold",
                    "field": "amount",
                    "operator": ">",
                    "value": 10000,
                    "severity": "high",
                    "action": "require_approval",
                    "message": "Transaction exceeds $10,000 limit"
                }
            ]],
        )
        fail_fast: bool = Field(
            default=False,
            description="Stop checking after first violation",
        )
        include_passed: bool = Field(
            default=False,
            description="Include passed rules in results",
        )

    class Output(OperatorOutput):
        passed: bool = Field(description="True if no blocking violations found")
        violations: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="List of rule violations",
        )
        passed_rules: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="List of rules that passed (if include_passed)",
        )
        blocking_violations: int = Field(
            default=0,
            description="Count of 'block' action violations",
        )
        warning_count: int = Field(
            default=0,
            description="Count of non-blocking violations",
        )
        rules_checked: int = Field(
            default=0,
            description="Total number of rules evaluated",
        )
        requires_approval: bool = Field(
            default=False,
            description="True if any rule requires approval",
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 10

    # Pre-built patterns for common PII detection
    BUILTIN_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone_us": r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
        "api_key": r"\b[a-zA-Z0-9_-]{32,}\b",
    }

    async def execute(self, input: Input, context) -> Output:
        """
        Execute rule checking against provided data.

        Args:
            input: The validated Input model
            context: Execution context

        Returns:
            Output with violation details and summary
        """
        violations = []
        passed_rules = []
        blocking_count = 0
        warning_count = 0
        requires_approval = False

        for rule in input.rules:
            rule_result = self._evaluate_rule(rule, input.data)

            if rule_result["violated"]:
                violation = {
                    "rule_id": rule.get("id", "unknown"),
                    "rule_name": rule.get("name", "Unnamed Rule"),
                    "severity": rule.get("severity", "medium"),
                    "action": rule.get("action", "warn"),
                    "message": rule.get("message", "Rule violated"),
                    "field": rule.get("field"),
                    "matched_value": rule_result.get("matched_value"),
                }
                violations.append(violation)

                # Count by action type
                action = rule.get("action", "warn")
                if action == "block":
                    blocking_count += 1
                elif action == "require_approval":
                    requires_approval = True
                    warning_count += 1
                else:
                    warning_count += 1

                # Fail fast if requested
                if input.fail_fast and action == "block":
                    break
            else:
                if input.include_passed:
                    passed_rules.append({
                        "rule_id": rule.get("id", "unknown"),
                        "rule_name": rule.get("name", "Unnamed Rule"),
                    })

        return self.Output(
            passed=blocking_count == 0,
            violations=violations,
            passed_rules=passed_rules,
            blocking_violations=blocking_count,
            warning_count=warning_count,
            rules_checked=len(input.rules),
            requires_approval=requires_approval,
        )

    def _evaluate_rule(
        self,
        rule: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a single rule against data."""
        rule_type = rule.get("type", "contains")
        field = rule.get("field")

        # Get field value from data
        value = self._get_field_value(data, field) if field else None

        # Evaluate based on rule type
        if rule_type == "regex":
            return self._check_regex(rule, value, data)
        elif rule_type == "threshold":
            return self._check_threshold(rule, value)
        elif rule_type == "contains":
            return self._check_contains(rule, value, data)
        elif rule_type == "expression":
            return self._check_expression(rule, data)
        elif rule_type == "builtin":
            return self._check_builtin(rule, value, data)
        else:
            return {"violated": False}

    def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get a field value, supporting dot notation."""
        if not field:
            return None

        parts = field.split(".")
        value = data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit():
                idx = int(part)
                value = value[idx] if idx < len(value) else None
            else:
                return None

        return value

    def _check_regex(
        self,
        rule: Dict[str, Any],
        value: Any,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check value against regex pattern."""
        pattern = rule.get("pattern", "")

        # If no specific field, search all string values
        if value is None:
            text = self._flatten_to_text(data)
        else:
            text = str(value)

        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "violated": True,
                    "matched_value": match.group(),
                }
        except re.error:
            pass

        return {"violated": False}

    def _check_threshold(
        self,
        rule: Dict[str, Any],
        value: Any
    ) -> Dict[str, Any]:
        """Check value against numeric threshold."""
        if value is None:
            return {"violated": False}

        try:
            num_value = float(value)
            threshold = float(rule.get("value", 0))
            operator = rule.get("operator", ">")

            operators = {
                ">": lambda a, b: a > b,
                ">=": lambda a, b: a >= b,
                "<": lambda a, b: a < b,
                "<=": lambda a, b: a <= b,
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
            }

            op_func = operators.get(operator)
            if op_func and op_func(num_value, threshold):
                return {
                    "violated": True,
                    "matched_value": num_value,
                }
        except (ValueError, TypeError):
            pass

        return {"violated": False}

    def _check_contains(
        self,
        rule: Dict[str, Any],
        value: Any,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if value contains specified keywords."""
        keywords = rule.get("keywords", [])
        case_sensitive = rule.get("case_sensitive", False)

        if value is None:
            text = self._flatten_to_text(data)
        else:
            text = str(value)

        if not case_sensitive:
            text = text.lower()
            keywords = [k.lower() for k in keywords]

        for keyword in keywords:
            if keyword in text:
                return {
                    "violated": True,
                    "matched_value": keyword,
                }

        return {"violated": False}

    def _check_expression(
        self,
        rule: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a boolean expression against data."""
        expression = rule.get("expression", "")

        # Simple expression evaluation (safe subset)
        # Format: "field operator value" e.g., "amount > 1000"
        try:
            parts = expression.split()
            if len(parts) >= 3:
                field = parts[0]
                operator = parts[1]
                compare_value = " ".join(parts[2:])

                field_value = self._get_field_value(data, field)
                if field_value is not None:
                    # Try numeric comparison
                    try:
                        num_field = float(field_value)
                        num_compare = float(compare_value)

                        result = self._check_threshold(
                            {"operator": operator, "value": num_compare},
                            num_field
                        )
                        return result
                    except ValueError:
                        # String comparison
                        if operator == "==":
                            if str(field_value) == compare_value:
                                return {"violated": True, "matched_value": field_value}
                        elif operator == "!=":
                            if str(field_value) != compare_value:
                                return {"violated": True, "matched_value": field_value}
        except Exception:
            pass

        return {"violated": False}

    def _check_builtin(
        self,
        rule: Dict[str, Any],
        value: Any,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check using built-in pattern by name."""
        pattern_name = rule.get("pattern_name", "")
        pattern = self.BUILTIN_PATTERNS.get(pattern_name)

        if pattern:
            return self._check_regex({"pattern": pattern}, value, data)

        return {"violated": False}

    def _flatten_to_text(self, data: Dict[str, Any]) -> str:
        """Flatten all string values in data to searchable text."""
        texts = []

        def extract(obj):
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    extract(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item)

        extract(data)
        return " ".join(texts)
