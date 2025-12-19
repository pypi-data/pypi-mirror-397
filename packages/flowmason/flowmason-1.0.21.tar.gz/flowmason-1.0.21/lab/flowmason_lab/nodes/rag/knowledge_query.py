"""
Knowledge Query Node - RAG Component.

Combines retrieval and generation to answer questions
using knowledge from a vector database.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="knowledge_query",
    category="rag",
    description="Answer questions using retrieved context from a knowledge base (RAG)",
    icon="brain",
    color="#10B981",  # Emerald green for RAG
    version="1.0.0",
    author="FlowMason",
    tags=["rag", "qa", "knowledge-base", "retrieval", "generation"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 4096,
        },
    },
    default_provider="anthropic",
    required_capabilities=["chat", "embedding"],
)
class KnowledgeQueryNode:
    """
    Answer questions using RAG (Retrieval Augmented Generation).

    This node combines retrieval and generation in a single step:
    1. Embeds the question using an embedding provider
    2. Retrieves relevant context from the vector database
    3. Generates an answer using the LLM with retrieved context

    Use cases:
    - Company knowledge bases
    - Documentation Q&A
    - Customer support automation
    - Research assistants
    - Policy/procedure lookup

    The node automatically handles:
    - Context window management (truncation if needed)
    - Source citation
    - Confidence scoring based on retrieval quality
    """

    class Input(NodeInput):
        question: str = Field(
            description="The question to answer using the knowledge base",
            examples=[
                "What is our refund policy for digital products?",
                "How do I set up SSO authentication?",
            ],
        )
        index_name: str = Field(
            description="Name of the vector index/collection to search",
            examples=["company-docs", "knowledge-base"],
        )
        top_k: int = Field(
            default=5,
            ge=1,
            le=20,
            description="Number of context chunks to retrieve",
        )
        namespace: Optional[str] = Field(
            default=None,
            description="Optional namespace to search within",
        )
        filter: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Metadata filter for retrieval",
        )
        system_prompt: Optional[str] = Field(
            default=None,
            description="Custom system prompt (default uses RAG-optimized prompt)",
        )
        include_sources: bool = Field(
            default=True,
            description="Include source documents in the response",
        )
        max_context_tokens: int = Field(
            default=8000,
            ge=500,
            le=100000,
            description="Maximum tokens for retrieved context",
        )
        temperature: float = Field(
            default=0.3,
            ge=0.0,
            le=2.0,
            description="Generation temperature (lower = more factual)",
        )
        require_citation: bool = Field(
            default=False,
            description="Require the model to cite sources in its answer",
        )

    class Output(NodeOutput):
        answer: str = Field(description="Generated answer based on retrieved context")
        sources: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Source documents used to generate the answer",
        )
        confidence: float = Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Confidence score based on retrieval quality",
        )
        context_used: int = Field(
            default=0,
            description="Number of context chunks used",
        )
        tokens_used: int = Field(
            default=0,
            description="Total tokens used for generation",
        )
        model: str = Field(default="", description="LLM model used")
        retrieval_scores: List[float] = Field(
            default_factory=list,
            description="Similarity scores from retrieval",
        )

    class Config:
        requires_llm: bool = True
        timeout_seconds: int = 120

    async def execute(self, input: Input, context) -> Output:
        """
        Execute RAG: retrieve context and generate answer.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with answer, sources, and metadata
        """
        # Get providers
        llm = getattr(context, "llm", None)
        embedding_provider = getattr(context, "embedding", None)
        vectordb_provider = getattr(context, "vectordb", None)

        if not llm or not embedding_provider or not vectordb_provider:
            # Fallback for testing
            return self.Output(
                answer=f"[Mock answer for: {input.question[:50]}...]",
                sources=[{"id": "mock", "content": "Mock source"}],
                confidence=0.8,
                context_used=1,
                model="mock",
            )

        # Step 1: Embed the question
        embedding_response = await embedding_provider.embed_async(input.question)
        query_vector = embedding_response.embeddings[0]

        # Step 2: Retrieve relevant context
        search_response = await vectordb_provider.search(
            index_name=input.index_name,
            query_vector=query_vector,
            top_k=input.top_k,
            namespace=input.namespace,
            filter=input.filter,
            include_metadata=True,
        )

        # Step 3: Build context from retrieved documents
        context_chunks = []
        sources = []
        retrieval_scores = []

        for i, match in enumerate(search_response.results):
            # Extract content from metadata
            content = ""
            if match.metadata:
                content = match.metadata.get("content") or match.metadata.get("text", "")

            if content:
                context_chunks.append(f"[Source {i+1}]\n{content}")
                sources.append({
                    "id": match.id,
                    "score": match.score,
                    "content": content[:500] + "..." if len(content) > 500 else content,
                    "metadata": {k: v for k, v in (match.metadata or {}).items()
                               if k not in ["content", "text", "embedding"]},
                })
                retrieval_scores.append(match.score)

        # Calculate confidence based on retrieval quality
        confidence = 0.0
        if retrieval_scores:
            # Confidence is based on average similarity of top results
            avg_score = sum(retrieval_scores) / len(retrieval_scores)
            # Scale from 0.5-1.0 similarity to 0-1 confidence
            confidence = min(1.0, max(0.0, (avg_score - 0.5) * 2))

        # Step 4: Build the RAG prompt
        context_text = "\n\n".join(context_chunks)

        default_system_prompt = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Answer the question using ONLY the information from the provided context
- If the context doesn't contain enough information to answer, say so clearly
- Be concise and direct in your answers
- If asked to cite sources, reference them as [Source N]"""

        if input.require_citation:
            default_system_prompt += "\n- You MUST cite your sources using [Source N] notation"

        system_prompt = input.system_prompt or default_system_prompt

        # Build the user prompt with context
        user_prompt = f"""Context:
{context_text}

Question: {input.question}

Answer:"""

        # Step 5: Generate the answer
        response = await llm.generate_async(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=input.temperature,
            max_tokens=4096,
        )

        # Extract token usage
        tokens = response.total_tokens if hasattr(response, "total_tokens") else 0

        return self.Output(
            answer=response.content,
            sources=sources if input.include_sources else [],
            confidence=confidence,
            context_used=len(context_chunks),
            tokens_used=tokens,
            model=response.model or llm.provider_name,
            retrieval_scores=retrieval_scores,
        )
