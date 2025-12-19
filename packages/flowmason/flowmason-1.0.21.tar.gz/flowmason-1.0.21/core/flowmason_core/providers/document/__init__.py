"""
FlowMason Document Providers

Provides document processing providers for OCR, layout analysis,
form extraction, and intelligent document understanding.

Built-in Providers:
- AzureDocumentIntelligenceProvider: Best-in-class document processing

Usage:
    from flowmason_core.providers.document import (
        AzureDocumentIntelligenceProvider,
        DocumentType,
    )

    # Full document analysis
    provider = AzureDocumentIntelligenceProvider()
    result = await provider.analyze(
        "document.pdf",
        extract_tables=True,
        extract_key_values=True
    )

    print(f"Text: {result.text}")
    print(f"Tables: {len(result.tables)}")
    print(f"Key-Values: {result.get_key_value_dict()}")

    # Invoice extraction
    result = await provider.analyze_invoice("invoice.pdf")
    print(f"Invoice fields: {result.get_key_value_dict()}")

    # Simple OCR
    text = await provider.extract_text("image.png")
"""

from .base import (
    BoundingBox,
    DocumentAnalysisResult,
    DocumentProvider,
    DocumentProviderConfig,
    DocumentType,
    ExtractedEntity,
    ExtractedKeyValue,
    ExtractedTable,
    ExtractedText,
    PageContent,
    TableCell,
    create_document_provider,
    get_document_provider,
    list_document_providers,
    register_document_provider,
)

# Import built-in providers to register them
from .azure_di import AzureDocumentIntelligenceProvider

__all__ = [
    # Base classes
    "DocumentProvider",
    "DocumentType",
    "DocumentAnalysisResult",
    "PageContent",
    "ExtractedText",
    "ExtractedTable",
    "TableCell",
    "ExtractedKeyValue",
    "ExtractedEntity",
    "BoundingBox",
    "DocumentProviderConfig",
    # Registry functions
    "register_document_provider",
    "get_document_provider",
    "list_document_providers",
    "create_document_provider",
    # Built-in providers
    "AzureDocumentIntelligenceProvider",
]
