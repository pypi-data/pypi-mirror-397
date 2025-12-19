"""
Retriever Node - RAG Component.

Retrieves relevant document chunks from a vector database
based on semantic similarity to a query.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="retriever",
    category="rag",
    description="Retrieve relevant document chunks from a vector database using semantic search",
    icon="search",
    color="#10B981",  # Emerald green for RAG
    version="1.0.0",
    author="FlowMason",
    tags=["rag", "retrieval", "vector-search", "semantic-search", "knowledge"],
    recommended_providers={
        "openai": {
            "model": "text-embedding-3-small",
            "dimensions": 1536,
        },
    },
    default_provider="openai",
    required_capabilities=["embedding"],
)
class RetrieverNode:
    """
    Retrieve relevant document chunks from a vector database.

    The Retriever is a core RAG component that:
    1. Embeds the query using an embedding provider
    2. Searches the vector database for similar chunks
    3. Returns ranked results with metadata and scores

    Use cases:
    - Document Q&A systems
    - Knowledge base search
    - Contextual information retrieval
    - Semantic search applications
    - Support ticket similarity matching

    Supported Vector Databases:
    - Pinecone (serverless and pod-based)
    - ChromaDB (local or persistent)
    - Weaviate (cloud or self-hosted)
    """

    class Input(NodeInput):
        query: str = Field(
            description="The query to search for in the vector database",
            examples=[
                "What is the refund policy?",
                "How do I configure authentication?",
            ],
        )
        index_name: str = Field(
            description="Name of the vector index/collection to search",
            examples=["company-docs", "knowledge-base"],
        )
        top_k: int = Field(
            default=5,
            ge=1,
            le=100,
            description="Number of results to return",
        )
        namespace: Optional[str] = Field(
            default=None,
            description="Optional namespace/partition to search within",
        )
        filter: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Metadata filter to apply (provider-specific format)",
            examples=[
                {"category": "policy"},
                {"department": {"$in": ["sales", "support"]}},
            ],
        )
        score_threshold: Optional[float] = Field(
            default=None,
            ge=0.0,
            le=1.0,
            description="Minimum similarity score threshold (0-1)",
        )
        include_metadata: bool = Field(
            default=True,
            description="Include document metadata in results",
        )
        include_content: bool = Field(
            default=True,
            description="Include document content/text in results",
        )

    class Output(NodeOutput):
        results: List[Dict[str, Any]] = Field(
            description="Retrieved documents with scores and metadata"
        )
        query_embedding: Optional[List[float]] = Field(
            default=None,
            description="The embedding vector used for the query (if requested)",
        )
        total_results: int = Field(
            default=0,
            description="Total number of results returned",
        )
        index_name: str = Field(
            default="",
            description="Index that was searched",
        )
        model: str = Field(
            default="",
            description="Embedding model used for the query",
        )

    class Config:
        requires_llm: bool = False  # Uses embedding provider, not LLM
        timeout_seconds: int = 30

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the retrieval using embedding and vector database providers.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with retrieved documents and metadata
        """
        # Get providers from context
        embedding_provider = getattr(context, "embedding", None)
        vectordb_provider = getattr(context, "vectordb", None)

        if not embedding_provider or not vectordb_provider:
            # Fallback for testing without providers
            return self.Output(
                results=[
                    {
                        "id": "mock-1",
                        "content": f"[Mock result for: {input.query[:50]}...]",
                        "score": 0.95,
                        "metadata": {"source": "mock"},
                    }
                ],
                total_results=1,
                index_name=input.index_name,
                model="mock",
            )

        # Generate embedding for the query
        embedding_response = await embedding_provider.embed_async(input.query)
        query_vector = embedding_response.embeddings[0]

        # Search the vector database
        search_response = await vectordb_provider.search(
            index_name=input.index_name,
            query_vector=query_vector,
            top_k=input.top_k,
            namespace=input.namespace,
            filter=input.filter,
            include_metadata=input.include_metadata,
            include_vectors=False,
        )

        # Format results
        results = []
        for match in search_response.results:
            # Apply score threshold if specified
            if input.score_threshold and match.score < input.score_threshold:
                continue

            result = {
                "id": match.id,
                "score": match.score,
            }

            if input.include_metadata and match.metadata:
                result["metadata"] = match.metadata

            if input.include_content:
                # Content may be in metadata or as separate field
                content = match.metadata.get("content") if match.metadata else None
                content = content or match.metadata.get("text") if match.metadata else None
                if content:
                    result["content"] = content

            results.append(result)

        return self.Output(
            results=results,
            query_embedding=query_vector if input.include_metadata else None,
            total_results=len(results),
            index_name=input.index_name,
            model=embedding_provider.name if hasattr(embedding_provider, "name") else "unknown",
        )
