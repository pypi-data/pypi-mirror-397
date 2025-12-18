"""
Compliance Evaluator Node - Compliance Component.

Combines structured rule results with policy lookup for
intelligent compliance assessment using LLM reasoning.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="compliance_evaluator",
    category="compliance",
    description="Evaluate compliance using AI reasoning over rules and policies",
    icon="scale",
    color="#EF4444",  # Red for compliance
    version="1.0.0",
    author="FlowMason",
    tags=["compliance", "ai", "evaluation", "reasoning", "decision"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.2,
            "max_tokens": 4096,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 4096,
        },
    },
    default_provider="anthropic",
    required_capabilities=["chat"],
)
class ComplianceEvaluatorNode:
    """
    Evaluate compliance using AI reasoning over rules and policies.

    The Compliance Evaluator is the intelligent layer of the hybrid
    compliance system. It takes:
    - Results from rule_checker (deterministic violations)
    - Policies from policy_lookup (semantic matches)
    - Original data/context

    And produces:
    - Final compliance decision
    - Risk assessment
    - Recommended actions
    - Detailed explanation

    This node handles:
    - Edge cases where rules don't fully apply
    - Context-sensitive interpretation
    - Policy conflict resolution
    - Exception recommendations
    - Escalation decisions

    Use cases:
    - Final compliance decision making
    - Exception request evaluation
    - Risk assessment with explanation
    - Audit trail generation
    """

    class Input(NodeInput):
        context_data: Dict[str, Any] = Field(
            description="Original data/request being evaluated",
            examples=[{
                "request_type": "refund",
                "amount": 150,
                "days_since_purchase": 45,
                "customer_tier": "gold",
            }],
        )
        rule_violations: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Violations from rule_checker",
        )
        relevant_policies: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Policies from policy_lookup",
        )
        evaluation_type: str = Field(
            default="standard",
            description="Type of evaluation: standard, strict, lenient",
        )
        require_explanation: bool = Field(
            default=True,
            description="Include detailed reasoning in response",
        )
        allow_exceptions: bool = Field(
            default=True,
            description="Whether exceptions can be recommended",
        )
        additional_context: Optional[str] = Field(
            default=None,
            description="Additional context for evaluation",
        )

    class Output(NodeOutput):
        decision: str = Field(
            description="Compliance decision: approved, denied, requires_review, exception_recommended"
        )
        risk_level: str = Field(
            default="low",
            description="Risk level: low, medium, high, critical"
        )
        confidence: float = Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Confidence in the decision (0-1)",
        )
        explanation: str = Field(
            default="",
            description="Detailed explanation of the decision",
        )
        recommended_actions: List[str] = Field(
            default_factory=list,
            description="Recommended next steps",
        )
        exception_details: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Exception recommendation details (if applicable)",
        )
        policies_applied: List[str] = Field(
            default_factory=list,
            description="Policies that influenced the decision",
        )
        violations_considered: List[str] = Field(
            default_factory=list,
            description="Violations that were evaluated",
        )
        escalation_required: bool = Field(
            default=False,
            description="Whether human review is needed",
        )
        audit_summary: str = Field(
            default="",
            description="Summary for audit trail",
        )

    class Config:
        requires_llm: bool = True
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """
        Execute compliance evaluation using LLM reasoning.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with compliance decision and details
        """
        llm = getattr(context, "llm", None)

        if not llm:
            # Fallback for testing
            has_violations = len(input.rule_violations) > 0
            return self.Output(
                decision="denied" if has_violations else "approved",
                risk_level="high" if has_violations else "low",
                confidence=0.8,
                explanation="Mock evaluation result",
                recommended_actions=["Review violations"] if has_violations else [],
            )

        # Build the evaluation prompt
        prompt = self._build_evaluation_prompt(input)
        system_prompt = self._get_system_prompt(input.evaluation_type)

        # Get LLM evaluation
        response = await llm.generate_async(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=4096,
        )

        # Parse the response
        result = self._parse_evaluation_response(
            response.content,
            input
        )

        return result

    def _get_system_prompt(self, evaluation_type: str) -> str:
        """Get system prompt based on evaluation type."""
        base_prompt = """You are a compliance evaluation expert. Your role is to:
1. Analyze the provided data, rule violations, and relevant policies
2. Make a compliance decision with clear reasoning
3. Assess risk level
4. Recommend appropriate actions

You must respond in a structured format with the following sections:

DECISION: [approved|denied|requires_review|exception_recommended]
RISK_LEVEL: [low|medium|high|critical]
CONFIDENCE: [0.0-1.0]
EXPLANATION: [detailed reasoning]
RECOMMENDED_ACTIONS: [bullet list of actions]
EXCEPTION_DETAILS: [if recommending exception, explain why and under what conditions]
ESCALATION_REQUIRED: [true|false]
AUDIT_SUMMARY: [one sentence summary for records]

Be thorough but concise. Focus on facts and policy alignment."""

        if evaluation_type == "strict":
            base_prompt += """

STRICT MODE: Apply rules and policies literally. Do not recommend exceptions
unless explicitly permitted by policy. Prioritize compliance over flexibility."""

        elif evaluation_type == "lenient":
            base_prompt += """

LENIENT MODE: Consider the spirit of policies, not just the letter.
Look for reasonable exceptions and mitigating factors. Balance compliance
with business needs and customer experience."""

        return base_prompt

    def _build_evaluation_prompt(self, input: Input) -> str:
        """Build the evaluation prompt with all context."""
        sections = []

        # Context data
        sections.append("## Request/Data Being Evaluated")
        sections.append("```json")
        import json
        sections.append(json.dumps(input.context_data, indent=2, default=str))
        sections.append("```")

        # Rule violations
        if input.rule_violations:
            sections.append("\n## Rule Violations Detected")
            for v in input.rule_violations:
                sections.append(f"- **{v.get('rule_name', 'Unknown Rule')}** ({v.get('severity', 'unknown')} severity)")
                sections.append(f"  - Action: {v.get('action', 'unknown')}")
                sections.append(f"  - Message: {v.get('message', 'No message')}")
                if v.get('matched_value'):
                    sections.append(f"  - Matched: {v.get('matched_value')}")
        else:
            sections.append("\n## Rule Violations")
            sections.append("No structured rule violations detected.")

        # Relevant policies
        if input.relevant_policies:
            sections.append("\n## Relevant Policies")
            for p in input.relevant_policies:
                sections.append(f"### {p.get('title', 'Untitled Policy')}")
                if p.get('category'):
                    sections.append(f"*Category: {p.get('category')}*")
                if p.get('content'):
                    content = p.get('content', '')
                    # Truncate very long policies
                    if len(content) > 2000:
                        content = content[:2000] + "..."
                    sections.append(content)
                sections.append("")
        else:
            sections.append("\n## Relevant Policies")
            sections.append("No specific policies found for this situation.")

        # Additional context
        if input.additional_context:
            sections.append("\n## Additional Context")
            sections.append(input.additional_context)

        # Instructions
        sections.append("\n## Your Task")
        sections.append("Evaluate this request for compliance. Consider:")
        sections.append("1. Any rule violations and their severity")
        sections.append("2. How policies apply to this specific situation")
        sections.append("3. Any mitigating or aggravating factors")
        sections.append("4. Whether an exception might be appropriate")

        if not input.allow_exceptions:
            sections.append("\nNote: Exceptions are NOT permitted for this evaluation.")

        return "\n".join(sections)

    def _parse_evaluation_response(
        self,
        response: str,
        input: Input
    ) -> Output:
        """Parse the LLM response into structured output."""
        # Default values
        decision = "requires_review"
        risk_level = "medium"
        confidence = 0.5
        explanation = ""
        recommended_actions = []
        exception_details = None
        escalation_required = False
        audit_summary = ""

        # Parse structured response
        lines = response.split("\n")
        current_section = None
        section_content = []

        for line in lines:
            line_upper = line.upper().strip()

            if line_upper.startswith("DECISION:"):
                decision = line.split(":", 1)[1].strip().lower()
                decision = self._normalize_decision(decision)
            elif line_upper.startswith("RISK_LEVEL:"):
                risk_level = line.split(":", 1)[1].strip().lower()
                risk_level = self._normalize_risk(risk_level)
            elif line_upper.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    confidence = min(1.0, max(0.0, confidence))
                except ValueError:
                    confidence = 0.5
            elif line_upper.startswith("EXPLANATION:"):
                current_section = "explanation"
                section_content = [line.split(":", 1)[1].strip()]
            elif line_upper.startswith("RECOMMENDED_ACTIONS:"):
                if current_section == "explanation":
                    explanation = "\n".join(section_content).strip()
                current_section = "actions"
                section_content = []
            elif line_upper.startswith("EXCEPTION_DETAILS:"):
                if current_section == "actions":
                    recommended_actions = [
                        a.strip().lstrip("-•*").strip()
                        for a in section_content
                        if a.strip() and a.strip() not in ["", "-", "•", "*"]
                    ]
                current_section = "exception"
                section_content = [line.split(":", 1)[1].strip()]
            elif line_upper.startswith("ESCALATION_REQUIRED:"):
                if current_section == "exception":
                    exception_text = "\n".join(section_content).strip()
                    if exception_text and exception_text.lower() not in ["none", "n/a", "not applicable"]:
                        exception_details = {"reasoning": exception_text}
                escalation_required = "true" in line.lower()
                current_section = None
            elif line_upper.startswith("AUDIT_SUMMARY:"):
                audit_summary = line.split(":", 1)[1].strip()
                current_section = None
            elif current_section and line.strip():
                section_content.append(line)

        # Handle any remaining section content
        if current_section == "explanation" and not explanation:
            explanation = "\n".join(section_content).strip()
        elif current_section == "actions" and not recommended_actions:
            recommended_actions = [
                a.strip().lstrip("-•*").strip()
                for a in section_content
                if a.strip() and a.strip() not in ["", "-", "•", "*"]
            ]

        # Build output
        policies_applied = [
            p.get("title", p.get("id", "Unknown"))
            for p in input.relevant_policies
        ]
        violations_considered = [
            v.get("rule_name", v.get("rule_id", "Unknown"))
            for v in input.rule_violations
        ]

        return self.Output(
            decision=decision,
            risk_level=risk_level,
            confidence=confidence,
            explanation=explanation or response[:500],  # Fallback to raw response
            recommended_actions=recommended_actions[:10],  # Limit actions
            exception_details=exception_details,
            policies_applied=policies_applied,
            violations_considered=violations_considered,
            escalation_required=escalation_required,
            audit_summary=audit_summary or f"Compliance evaluation: {decision}",
        )

    def _normalize_decision(self, decision: str) -> str:
        """Normalize decision to allowed values."""
        decision = decision.lower().strip()
        if "approved" in decision or "approve" in decision or "allow" in decision:
            return "approved"
        elif "denied" in decision or "deny" in decision or "reject" in decision or "block" in decision:
            return "denied"
        elif "exception" in decision:
            return "exception_recommended"
        else:
            return "requires_review"

    def _normalize_risk(self, risk: str) -> str:
        """Normalize risk level to allowed values."""
        risk = risk.lower().strip()
        if "critical" in risk:
            return "critical"
        elif "high" in risk:
            return "high"
        elif "medium" in risk or "moderate" in risk:
            return "medium"
        else:
            return "low"
