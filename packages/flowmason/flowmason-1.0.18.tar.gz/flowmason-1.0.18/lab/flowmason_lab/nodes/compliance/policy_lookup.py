"""
Policy Lookup Node - Compliance Component.

Retrieves relevant policy documents from a knowledge base
using RAG for semantic policy matching.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="policy_lookup",
    category="compliance",
    description="Look up relevant policies using semantic search over policy documents",
    icon="book-open",
    color="#EF4444",  # Red for compliance
    version="1.0.0",
    author="FlowMason",
    tags=["compliance", "policy", "rag", "regulations", "procedures"],
    recommended_providers={
        "openai": {
            "model": "text-embedding-3-small",
        },
    },
    default_provider="openai",
    required_capabilities=["embedding"],
)
class PolicyLookupNode:
    """
    Look up relevant policies using semantic search.

    The Policy Lookup node searches a vector database of policy
    documents to find relevant policies for a given situation.

    This is the RAG layer of a hybrid compliance system:
    - Structured rules (rule_checker) handle deterministic patterns
    - Policy lookup handles semantic/contextual matching
    - Compliance evaluator combines both for final assessment

    Use cases:
    - Policy-based decision making
    - Procedure lookup
    - Regulatory compliance checks
    - Exception handling guidelines
    - Escalation procedures
    """

    class Input(NodeInput):
        query: str = Field(
            description="The situation or question to find policies for",
            examples=[
                "Customer is requesting a refund for a digital product after 60 days",
                "Employee wants to work remotely from another country",
            ],
        )
        index_name: str = Field(
            description="Name of the policy vector index",
            examples=["company-policies", "compliance-docs"],
        )
        top_k: int = Field(
            default=5,
            ge=1,
            le=20,
            description="Number of policies to retrieve",
        )
        namespace: Optional[str] = Field(
            default=None,
            description="Policy category/namespace to search",
            examples=["hr", "finance", "customer-service"],
        )
        filter: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Metadata filter for policies",
            examples=[
                {"department": "finance"},
                {"policy_type": "mandatory"},
            ],
        )
        include_full_text: bool = Field(
            default=True,
            description="Include full policy text in results",
        )
        score_threshold: float = Field(
            default=0.5,
            ge=0.0,
            le=1.0,
            description="Minimum relevance score (0-1)",
        )

    class Output(NodeOutput):
        policies: List[Dict[str, Any]] = Field(
            description="Relevant policy documents with scores",
        )
        policy_summaries: List[str] = Field(
            default_factory=list,
            description="Brief summaries of each policy",
        )
        has_relevant_policies: bool = Field(
            default=False,
            description="True if relevant policies were found",
        )
        policy_count: int = Field(
            default=0,
            description="Number of relevant policies found",
        )
        avg_relevance: float = Field(
            default=0.0,
            description="Average relevance score of results",
        )
        categories_found: List[str] = Field(
            default_factory=list,
            description="Policy categories/types found",
        )

    class Config:
        requires_llm: bool = False  # Uses embedding provider
        timeout_seconds: int = 30

    async def execute(self, input: Input, context) -> Output:
        """
        Execute policy lookup using embedding and vector database.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with relevant policies and metadata
        """
        # Get providers
        embedding_provider = getattr(context, "embedding", None)
        vectordb_provider = getattr(context, "vectordb", None)

        if not embedding_provider or not vectordb_provider:
            # Fallback for testing
            return self.Output(
                policies=[{
                    "id": "mock-policy",
                    "title": "Mock Policy",
                    "content": f"Mock policy for: {input.query[:50]}",
                    "score": 0.9,
                }],
                policy_summaries=["Mock policy summary"],
                has_relevant_policies=True,
                policy_count=1,
                avg_relevance=0.9,
            )

        # Embed the query
        embedding_response = await embedding_provider.embed_async(input.query)
        query_vector = embedding_response.embeddings[0]

        # Search for relevant policies
        search_response = await vectordb_provider.search(
            index_name=input.index_name,
            query_vector=query_vector,
            top_k=input.top_k,
            namespace=input.namespace,
            filter=input.filter,
            include_metadata=True,
        )

        # Process results
        policies = []
        summaries = []
        categories = set()
        scores = []

        for match in search_response.results:
            # Apply score threshold
            if match.score < input.score_threshold:
                continue

            policy = {
                "id": match.id,
                "score": match.score,
            }

            # Extract metadata
            if match.metadata:
                policy["title"] = match.metadata.get("title", "Untitled Policy")
                policy["category"] = match.metadata.get("category", "general")
                policy["effective_date"] = match.metadata.get("effective_date")
                policy["version"] = match.metadata.get("version")

                if match.metadata.get("category"):
                    categories.add(match.metadata["category"])

                # Include full text if requested
                if input.include_full_text:
                    content = (
                        match.metadata.get("content") or
                        match.metadata.get("text") or
                        ""
                    )
                    policy["content"] = content

                # Get or generate summary
                summary = match.metadata.get("summary")
                if not summary and policy.get("content"):
                    # Create a basic summary from first 200 chars
                    summary = policy["content"][:200].strip()
                    if len(policy.get("content", "")) > 200:
                        summary += "..."

                if summary:
                    summaries.append(f"{policy.get('title', 'Policy')}: {summary}")

            policies.append(policy)
            scores.append(match.score)

        # Calculate metrics
        has_relevant = len(policies) > 0
        avg_relevance = sum(scores) / len(scores) if scores else 0.0

        return self.Output(
            policies=policies,
            policy_summaries=summaries,
            has_relevant_policies=has_relevant,
            policy_count=len(policies),
            avg_relevance=avg_relevance,
            categories_found=list(categories),
        )
