"""
FlowMason RAG Nodes

Provides Retrieval Augmented Generation (RAG) nodes for
building knowledge-based AI applications.

Built-in Nodes:
- retriever: Retrieve relevant chunks from vector database
- knowledge_query: Answer questions using RAG

Usage:
    # In a pipeline, use the retriever node to search documents
    {
        "id": "search-docs",
        "component": "retriever",
        "inputs": {
            "query": "{{input.question}}",
            "index_name": "company-docs",
            "top_k": 5
        }
    }

    # Or use knowledge_query for full RAG in one step
    {
        "id": "answer-question",
        "component": "knowledge_query",
        "inputs": {
            "question": "{{input.question}}",
            "index_name": "company-docs",
            "top_k": 5
        }
    }
"""

from .retriever import RetrieverNode
from .knowledge_query import KnowledgeQueryNode

__all__ = [
    "RetrieverNode",
    "KnowledgeQueryNode",
]
