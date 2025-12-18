"""
Tests for compliance nodes.

Tests cover:
- RuleCheckerOperator
- PolicyLookupNode
- ComplianceEvaluatorNode
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

from flowmason_lab.nodes.compliance import (
    RuleCheckerOperator,
    PolicyLookupNode,
    ComplianceEvaluatorNode,
)


class TestRuleCheckerOperator:
    """Tests for RuleCheckerOperator."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(RuleCheckerOperator, "_flowmason_metadata")
        meta = RuleCheckerOperator._flowmason_metadata
        assert meta["name"] == "rule_checker"
        assert meta["category"] == "compliance"
        assert meta["component_kind"] == "operator"

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = RuleCheckerOperator.Input.model_json_schema()
        props = input_schema["properties"]
        assert "data" in props
        assert "rules" in props
        assert "fail_fast" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = RuleCheckerOperator.Output.model_json_schema()
        props = output_schema["properties"]
        assert "passed" in props
        assert "violations" in props
        assert "blocking_violations" in props

    def test_builtin_patterns(self):
        """Test builtin PII patterns."""
        op = RuleCheckerOperator()
        patterns = op.BUILTIN_PATTERNS
        assert "ssn" in patterns
        assert "credit_card" in patterns
        assert "email" in patterns

    @pytest.mark.asyncio
    async def test_regex_rule_ssn_detection(self):
        """Test SSN detection with regex rule."""
        op = RuleCheckerOperator()
        input_obj = RuleCheckerOperator.Input(
            data={"message": "My SSN is 123-45-6789"},
            rules=[{
                "id": "ssn-check",
                "name": "SSN Detection",
                "type": "regex",
                "field": "message",
                "pattern": r"\d{3}-\d{2}-\d{4}",
                "severity": "critical",
                "action": "block",
                "message": "SSN detected",
            }],
        )
        context = Mock()

        result = await op.execute(input_obj, context)

        assert result.passed is False
        assert len(result.violations) == 1
        assert result.violations[0]["rule_id"] == "ssn-check"
        assert result.blocking_violations == 1

    @pytest.mark.asyncio
    async def test_threshold_rule(self):
        """Test threshold rule."""
        op = RuleCheckerOperator()
        input_obj = RuleCheckerOperator.Input(
            data={"amount": 15000},
            rules=[{
                "id": "amount-limit",
                "name": "Transaction Limit",
                "type": "threshold",
                "field": "amount",
                "operator": ">",
                "value": 10000,
                "severity": "high",
                "action": "require_approval",
                "message": "Amount exceeds limit",
            }],
        )
        context = Mock()

        result = await op.execute(input_obj, context)

        assert result.passed is True  # require_approval doesn't block
        assert len(result.violations) == 1
        assert result.requires_approval is True

    @pytest.mark.asyncio
    async def test_contains_rule(self):
        """Test contains rule with keywords."""
        op = RuleCheckerOperator()
        input_obj = RuleCheckerOperator.Input(
            data={"comment": "This product is terrible and I hate it"},
            rules=[{
                "id": "profanity-check",
                "name": "Profanity Filter",
                "type": "contains",
                "field": "comment",
                "keywords": ["hate", "terrible"],
                "severity": "medium",
                "action": "warn",
                "message": "Negative language detected",
            }],
        )
        context = Mock()

        result = await op.execute(input_obj, context)

        assert len(result.violations) == 1
        assert result.warning_count == 1

    @pytest.mark.asyncio
    async def test_no_violations(self):
        """Test when no rules are violated."""
        op = RuleCheckerOperator()
        input_obj = RuleCheckerOperator.Input(
            data={"email": "test@example.com", "amount": 100},
            rules=[{
                "id": "amount-limit",
                "type": "threshold",
                "field": "amount",
                "operator": ">",
                "value": 10000,
                "action": "block",
            }],
        )
        context = Mock()

        result = await op.execute(input_obj, context)

        assert result.passed is True
        assert len(result.violations) == 0

    @pytest.mark.asyncio
    async def test_fail_fast(self):
        """Test fail_fast stops after first blocking violation."""
        op = RuleCheckerOperator()
        input_obj = RuleCheckerOperator.Input(
            data={"text": "SSN: 123-45-6789 and CC: 4111-1111-1111-1111"},
            rules=[
                {
                    "id": "ssn",
                    "type": "regex",
                    "pattern": r"\d{3}-\d{2}-\d{4}",
                    "action": "block",
                },
                {
                    "id": "cc",
                    "type": "regex",
                    "pattern": r"\d{4}-\d{4}-\d{4}-\d{4}",
                    "action": "block",
                },
            ],
            fail_fast=True,
        )
        context = Mock()

        result = await op.execute(input_obj, context)

        # Should only have one violation due to fail_fast
        assert len(result.violations) == 1


class TestPolicyLookupNode:
    """Tests for PolicyLookupNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(PolicyLookupNode, "_flowmason_metadata")
        meta = PolicyLookupNode._flowmason_metadata
        assert meta["name"] == "policy_lookup"
        assert meta["category"] == "compliance"

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = PolicyLookupNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "query" in props
        assert "index_name" in props
        assert "top_k" in props
        assert "score_threshold" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = PolicyLookupNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "policies" in props
        assert "has_relevant_policies" in props
        assert "policy_count" in props

    @pytest.mark.asyncio
    async def test_execute_without_providers(self):
        """Test execution without providers returns mock."""
        node = PolicyLookupNode()
        input_obj = PolicyLookupNode.Input(
            query="What is the refund policy?",
            index_name="policies",
        )
        context = Mock()
        context.embedding = None
        context.vectordb = None

        result = await node.execute(input_obj, context)

        assert result.has_relevant_policies is True
        assert result.policy_count == 1

    @pytest.mark.asyncio
    async def test_execute_with_mocked_providers(self):
        """Test execution with mocked providers."""
        node = PolicyLookupNode()
        input_obj = PolicyLookupNode.Input(
            query="remote work policy",
            index_name="hr-policies",
            top_k=3,
        )

        mock_embedding = MagicMock()
        mock_embedding.embed_async = AsyncMock(return_value=MagicMock(
            embeddings=[[0.1, 0.2, 0.3]]
        ))

        mock_result = MagicMock()
        mock_result.id = "policy-1"
        mock_result.score = 0.85
        mock_result.metadata = {
            "title": "Remote Work Policy",
            "category": "hr",
            "content": "Employees may work remotely up to 3 days per week...",
        }

        mock_vectordb = MagicMock()
        mock_vectordb.search = AsyncMock(return_value=MagicMock(results=[mock_result]))

        context = Mock()
        context.embedding = mock_embedding
        context.vectordb = mock_vectordb

        result = await node.execute(input_obj, context)

        assert result.has_relevant_policies is True
        assert result.policy_count == 1
        assert result.policies[0]["title"] == "Remote Work Policy"
        assert "hr" in result.categories_found

    @pytest.mark.asyncio
    async def test_score_threshold_filtering(self):
        """Test that low-score results are filtered."""
        node = PolicyLookupNode()
        input_obj = PolicyLookupNode.Input(
            query="test",
            index_name="policies",
            score_threshold=0.7,
        )

        mock_embedding = MagicMock()
        mock_embedding.embed_async = AsyncMock(return_value=MagicMock(
            embeddings=[[0.1, 0.2]]
        ))

        # One result above threshold, one below
        mock_result1 = MagicMock()
        mock_result1.id = "1"
        mock_result1.score = 0.8
        mock_result1.metadata = {"title": "High Score", "content": "a"}

        mock_result2 = MagicMock()
        mock_result2.id = "2"
        mock_result2.score = 0.5  # Below threshold
        mock_result2.metadata = {"title": "Low Score", "content": "b"}

        mock_vectordb = MagicMock()
        mock_vectordb.search = AsyncMock(return_value=MagicMock(
            results=[mock_result1, mock_result2]
        ))

        context = Mock()
        context.embedding = mock_embedding
        context.vectordb = mock_vectordb

        result = await node.execute(input_obj, context)

        # Only one result should pass the threshold
        assert result.policy_count == 1
        assert result.policies[0]["id"] == "1"


class TestComplianceEvaluatorNode:
    """Tests for ComplianceEvaluatorNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(ComplianceEvaluatorNode, "_flowmason_metadata")
        meta = ComplianceEvaluatorNode._flowmason_metadata
        assert meta["name"] == "compliance_evaluator"
        assert meta["category"] == "compliance"
        assert meta["requires_llm"] is True

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = ComplianceEvaluatorNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "context_data" in props
        assert "rule_violations" in props
        assert "relevant_policies" in props
        assert "evaluation_type" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = ComplianceEvaluatorNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "decision" in props
        assert "risk_level" in props
        assert "explanation" in props
        assert "recommended_actions" in props

    @pytest.mark.asyncio
    async def test_execute_without_llm(self):
        """Test execution without LLM returns basic decision."""
        node = ComplianceEvaluatorNode()
        input_obj = ComplianceEvaluatorNode.Input(
            context_data={"request": "test"},
            rule_violations=[{"rule_name": "test", "severity": "high"}],
        )
        context = Mock()
        context.llm = None

        result = await node.execute(input_obj, context)

        assert result.decision == "denied"  # Has violations
        assert result.risk_level == "high"

    @pytest.mark.asyncio
    async def test_execute_no_violations(self):
        """Test execution with no violations."""
        node = ComplianceEvaluatorNode()
        input_obj = ComplianceEvaluatorNode.Input(
            context_data={"request": "test"},
            rule_violations=[],  # No violations
        )
        context = Mock()
        context.llm = None

        result = await node.execute(input_obj, context)

        assert result.decision == "approved"
        assert result.risk_level == "low"

    @pytest.mark.asyncio
    async def test_execute_with_mocked_llm(self):
        """Test execution with mocked LLM."""
        node = ComplianceEvaluatorNode()
        input_obj = ComplianceEvaluatorNode.Input(
            context_data={
                "request_type": "refund",
                "amount": 150,
                "days_since_purchase": 25,
            },
            rule_violations=[],
            relevant_policies=[{
                "title": "Refund Policy",
                "content": "Refunds are allowed within 30 days",
            }],
        )

        mock_llm = MagicMock()
        mock_llm.generate_async = AsyncMock(return_value=MagicMock(
            content="""DECISION: approved
RISK_LEVEL: low
CONFIDENCE: 0.95
EXPLANATION: The refund request is within the 30-day policy window.
RECOMMENDED_ACTIONS:
- Process the refund
- Send confirmation email
EXCEPTION_DETAILS: None
ESCALATION_REQUIRED: false
AUDIT_SUMMARY: Refund approved per standard policy.""",
            total_tokens=200,
            model="claude-3-5-sonnet",
        ))
        mock_llm.provider_name = "anthropic"

        context = Mock()
        context.llm = mock_llm

        result = await node.execute(input_obj, context)

        assert result.decision == "approved"
        assert result.risk_level == "low"
        assert result.confidence == 0.95
        assert "30-day" in result.explanation
        assert len(result.recommended_actions) > 0

    def test_normalize_decision(self):
        """Test decision normalization."""
        node = ComplianceEvaluatorNode()

        assert node._normalize_decision("approved") == "approved"
        assert node._normalize_decision("APPROVED") == "approved"
        assert node._normalize_decision("approve this") == "approved"
        assert node._normalize_decision("denied") == "denied"
        assert node._normalize_decision("reject") == "denied"
        assert node._normalize_decision("exception recommended") == "exception_recommended"
        assert node._normalize_decision("unclear") == "requires_review"

    def test_normalize_risk(self):
        """Test risk level normalization."""
        node = ComplianceEvaluatorNode()

        assert node._normalize_risk("low") == "low"
        assert node._normalize_risk("HIGH") == "high"
        assert node._normalize_risk("critical risk") == "critical"
        assert node._normalize_risk("moderate") == "medium"
        assert node._normalize_risk("unknown") == "low"
