"""
FlowMason Compliance Nodes

Provides a hybrid compliance system combining structured rules
with semantic policy lookup and AI-powered evaluation.

Architecture:
    ┌─────────────────────┐
    │   rule_checker      │  Deterministic rule evaluation
    │  (fast, patterns)   │  - Regex (SSN, credit cards)
    └──────────┬──────────┘  - Thresholds (amount limits)
               │             - Keywords (prohibited terms)
               │
    ┌──────────▼──────────┐
    │   policy_lookup     │  Semantic policy retrieval
    │   (RAG search)      │  - Find relevant policies
    └──────────┬──────────┘  - Context-aware matching
               │
    ┌──────────▼──────────┐
    │compliance_evaluator │  AI-powered decision making
    │  (LLM reasoning)    │  - Combine rules + policies
    └─────────────────────┘  - Handle edge cases
                             - Generate explanations

Built-in Nodes:
- rule_checker: Fast pattern-based rule evaluation (operator)
- policy_lookup: RAG over policy documents (node)
- compliance_evaluator: AI-powered final assessment (node)

Usage - Full Compliance Pipeline:
    # Stage 1: Check structured rules
    {
        "id": "check-rules",
        "component": "rule_checker",
        "inputs": {
            "data": "{{input.request}}",
            "rules": "{{env.COMPLIANCE_RULES}}"
        }
    }

    # Stage 2: Look up relevant policies
    {
        "id": "lookup-policies",
        "component": "policy_lookup",
        "inputs": {
            "query": "{{input.request.description}}",
            "index_name": "company-policies",
            "namespace": "{{input.request.department}}"
        }
    }

    # Stage 3: Final AI evaluation
    {
        "id": "evaluate-compliance",
        "component": "compliance_evaluator",
        "inputs": {
            "context_data": "{{input.request}}",
            "rule_violations": "{{upstream.check-rules.violations}}",
            "relevant_policies": "{{upstream.lookup-policies.policies}}",
            "evaluation_type": "standard"
        }
    }

Example Rules:
    [
        {
            "id": "pii-ssn",
            "name": "SSN Detection",
            "type": "regex",
            "pattern": "\\d{3}-\\d{2}-\\d{4}",
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
            "message": "Amount exceeds approval threshold"
        }
    ]
"""

from .rule_checker import RuleCheckerOperator
from .policy_lookup import PolicyLookupNode
from .compliance_evaluator import ComplianceEvaluatorNode

__all__ = [
    "RuleCheckerOperator",
    "PolicyLookupNode",
    "ComplianceEvaluatorNode",
]
