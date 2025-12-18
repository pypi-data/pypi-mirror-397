"""
Tests for RAG nodes.

Tests cover:
- RetrieverNode
- KnowledgeQueryNode
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

from flowmason_lab.nodes.rag import RetrieverNode, KnowledgeQueryNode


class TestRetrieverNode:
    """Tests for RetrieverNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(RetrieverNode, "_flowmason_metadata")
        meta = RetrieverNode._flowmason_metadata
        assert meta["name"] == "retriever"
        assert meta["category"] == "rag"
        assert "vector-search" in meta["tags"]

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = RetrieverNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "query" in props
        assert "index_name" in props
        assert "top_k" in props
        assert "namespace" in props
        assert "filter" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = RetrieverNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "results" in props
        assert "total_results" in props
        assert "index_name" in props

    def test_input_validation(self):
        """Test input validation."""
        # Valid input
        input_obj = RetrieverNode.Input(
            query="test query",
            index_name="test-index",
            top_k=5,
        )
        assert input_obj.query == "test query"
        assert input_obj.top_k == 5

        # Invalid top_k (too high)
        with pytest.raises(Exception):
            RetrieverNode.Input(
                query="test",
                index_name="test-index",
                top_k=200,  # Max is 100
            )

    @pytest.mark.asyncio
    async def test_execute_without_providers(self):
        """Test execution without providers returns mock."""
        node = RetrieverNode()
        input_obj = RetrieverNode.Input(
            query="test query",
            index_name="test-index",
        )
        context = Mock()
        context.embedding = None
        context.vectordb = None

        result = await node.execute(input_obj, context)

        assert result.total_results == 1
        assert result.model == "mock"
        assert len(result.results) == 1

    @pytest.mark.asyncio
    async def test_execute_with_mocked_providers(self):
        """Test execution with mocked providers."""
        node = RetrieverNode()
        input_obj = RetrieverNode.Input(
            query="What is the refund policy?",
            index_name="docs",
            top_k=3,
        )

        # Mock embedding provider
        mock_embedding = MagicMock()
        mock_embedding.embed_async = AsyncMock(return_value=MagicMock(
            embeddings=[[0.1, 0.2, 0.3]]
        ))
        mock_embedding.name = "openai"

        # Mock vectordb provider
        mock_result1 = MagicMock()
        mock_result1.id = "doc-1"
        mock_result1.score = 0.95
        mock_result1.metadata = {"content": "Refund policy content"}

        mock_result2 = MagicMock()
        mock_result2.id = "doc-2"
        mock_result2.score = 0.85
        mock_result2.metadata = {"content": "More info"}

        mock_search_response = MagicMock()
        mock_search_response.results = [mock_result1, mock_result2]

        mock_vectordb = MagicMock()
        mock_vectordb.search = AsyncMock(return_value=mock_search_response)

        context = Mock()
        context.embedding = mock_embedding
        context.vectordb = mock_vectordb

        result = await node.execute(input_obj, context)

        assert result.total_results == 2
        assert result.results[0]["id"] == "doc-1"
        assert result.results[0]["score"] == 0.95


class TestKnowledgeQueryNode:
    """Tests for KnowledgeQueryNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(KnowledgeQueryNode, "_flowmason_metadata")
        meta = KnowledgeQueryNode._flowmason_metadata
        assert meta["name"] == "knowledge_query"
        assert meta["category"] == "rag"
        assert "qa" in meta["tags"]

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = KnowledgeQueryNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "question" in props
        assert "index_name" in props
        assert "top_k" in props
        assert "system_prompt" in props
        assert "include_sources" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = KnowledgeQueryNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "answer" in props
        assert "sources" in props
        assert "confidence" in props
        assert "context_used" in props

    def test_input_validation(self):
        """Test input validation."""
        input_obj = KnowledgeQueryNode.Input(
            question="What is our refund policy?",
            index_name="company-docs",
            top_k=5,
            temperature=0.3,
        )
        assert input_obj.question == "What is our refund policy?"
        assert input_obj.temperature == 0.3

    @pytest.mark.asyncio
    async def test_execute_without_providers(self):
        """Test execution without providers returns mock."""
        node = KnowledgeQueryNode()
        input_obj = KnowledgeQueryNode.Input(
            question="What is the policy?",
            index_name="docs",
        )
        context = Mock()
        context.llm = None
        context.embedding = None
        context.vectordb = None

        result = await node.execute(input_obj, context)

        assert "Mock answer" in result.answer
        assert result.confidence == 0.8

    @pytest.mark.asyncio
    async def test_execute_with_mocked_providers(self):
        """Test full RAG execution with mocks."""
        node = KnowledgeQueryNode()
        input_obj = KnowledgeQueryNode.Input(
            question="What is the refund policy?",
            index_name="docs",
            top_k=3,
        )

        # Mock embedding provider
        mock_embedding = MagicMock()
        mock_embedding.embed_async = AsyncMock(return_value=MagicMock(
            embeddings=[[0.1, 0.2, 0.3]]
        ))

        # Mock vectordb provider
        mock_result = MagicMock()
        mock_result.id = "doc-1"
        mock_result.score = 0.9
        mock_result.metadata = {"content": "Our refund policy allows returns within 30 days."}

        mock_search_response = MagicMock()
        mock_search_response.results = [mock_result]

        mock_vectordb = MagicMock()
        mock_vectordb.search = AsyncMock(return_value=mock_search_response)

        # Mock LLM provider
        mock_llm = MagicMock()
        mock_llm.generate_async = AsyncMock(return_value=MagicMock(
            content="Based on the policy, you can return items within 30 days.",
            total_tokens=150,
            model="claude-3-5-sonnet",
        ))
        mock_llm.provider_name = "anthropic"

        context = Mock()
        context.llm = mock_llm
        context.embedding = mock_embedding
        context.vectordb = mock_vectordb

        result = await node.execute(input_obj, context)

        assert "30 days" in result.answer
        assert result.context_used == 1
        assert len(result.sources) == 1
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_confidence_calculation(self):
        """Test confidence is calculated from retrieval scores."""
        node = KnowledgeQueryNode()
        input_obj = KnowledgeQueryNode.Input(
            question="test",
            index_name="docs",
        )

        # Mock with high similarity scores
        mock_embedding = MagicMock()
        mock_embedding.embed_async = AsyncMock(return_value=MagicMock(
            embeddings=[[0.1, 0.2]]
        ))

        mock_result = MagicMock()
        mock_result.id = "1"
        mock_result.score = 0.95  # High score
        mock_result.metadata = {"content": "test content"}

        mock_vectordb = MagicMock()
        mock_vectordb.search = AsyncMock(return_value=MagicMock(results=[mock_result]))

        mock_llm = MagicMock()
        mock_llm.generate_async = AsyncMock(return_value=MagicMock(
            content="Answer",
            total_tokens=10,
            model="test",
        ))
        mock_llm.provider_name = "test"

        context = Mock()
        context.llm = mock_llm
        context.embedding = mock_embedding
        context.vectordb = mock_vectordb

        result = await node.execute(input_obj, context)

        # 0.95 score should give high confidence (scaled from 0.5-1.0 to 0-1)
        assert result.confidence > 0.8
