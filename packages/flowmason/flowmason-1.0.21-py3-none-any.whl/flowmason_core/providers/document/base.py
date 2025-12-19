"""
Document Provider Base Classes

Provides the base infrastructure for document processing providers,
handling OCR, layout analysis, form extraction, and intelligent
document understanding.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, BinaryIO, Dict, List, Optional, Union


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    IMAGE = "image"  # PNG, JPG, TIFF, BMP
    WORD = "word"  # DOCX
    EXCEL = "excel"  # XLSX
    POWERPOINT = "powerpoint"  # PPTX


@dataclass
class BoundingBox:
    """Bounding box for a detected element."""
    x: float  # Left coordinate (0-1 normalized or pixels)
    y: float  # Top coordinate
    width: float
    height: float
    page: int = 1
    unit: str = "normalized"  # normalized (0-1) or pixels

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "page": self.page,
            "unit": self.unit,
        }


@dataclass
class ExtractedText:
    """A block of extracted text."""
    content: str
    confidence: float = 1.0
    bounding_box: Optional[BoundingBox] = None
    text_type: str = "paragraph"  # paragraph, heading, title, caption

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "text_type": self.text_type,
        }


@dataclass
class TableCell:
    """A cell in an extracted table."""
    content: str
    row_index: int
    column_index: int
    row_span: int = 1
    column_span: int = 1
    is_header: bool = False
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "row_index": self.row_index,
            "column_index": self.column_index,
            "row_span": self.row_span,
            "column_span": self.column_span,
            "is_header": self.is_header,
            "confidence": self.confidence,
        }


@dataclass
class ExtractedTable:
    """An extracted table from a document."""
    cells: List[TableCell]
    rows: List[List[str]]  # Simple row/column representation
    headers: Optional[List[str]] = None
    row_count: int = 0
    column_count: int = 0
    confidence: float = 1.0
    bounding_box: Optional[BoundingBox] = None
    caption: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cells": [c.to_dict() for c in self.cells],
            "rows": self.rows,
            "headers": self.headers,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "caption": self.caption,
        }

    def to_markdown(self) -> str:
        """Convert table to markdown format."""
        if not self.rows:
            return ""

        lines = []
        if self.headers:
            lines.append("| " + " | ".join(self.headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")

        for row in self.rows:
            if self.headers and row == self.headers:
                continue
            lines.append("| " + " | ".join(str(c) for c in row) + " |")

        return "\n".join(lines)


@dataclass
class ExtractedKeyValue:
    """A key-value pair extracted from a form."""
    key: str
    value: str
    confidence: float = 1.0
    key_bounding_box: Optional[BoundingBox] = None
    value_bounding_box: Optional[BoundingBox] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "confidence": self.confidence,
            "key_bounding_box": self.key_bounding_box.to_dict() if self.key_bounding_box else None,
            "value_bounding_box": self.value_bounding_box.to_dict() if self.value_bounding_box else None,
        }


@dataclass
class ExtractedEntity:
    """A named entity extracted from a document."""
    text: str
    entity_type: str  # PERSON, ORG, DATE, MONEY, ADDRESS, etc.
    confidence: float = 1.0
    bounding_box: Optional[BoundingBox] = None
    normalized_value: Optional[str] = None  # e.g., normalized date format

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "entity_type": self.entity_type,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "normalized_value": self.normalized_value,
        }


@dataclass
class PageContent:
    """Content from a single page."""
    page_number: int
    text: str
    text_blocks: List[ExtractedText] = field(default_factory=list)
    tables: List[ExtractedTable] = field(default_factory=list)
    key_values: List[ExtractedKeyValue] = field(default_factory=list)
    width: Optional[float] = None
    height: Optional[float] = None
    angle: float = 0.0  # Page rotation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "text_blocks": [t.to_dict() for t in self.text_blocks],
            "tables": [t.to_dict() for t in self.tables],
            "key_values": [kv.to_dict() for kv in self.key_values],
            "width": self.width,
            "height": self.height,
            "angle": self.angle,
        }


@dataclass
class DocumentAnalysisResult:
    """Complete result of document analysis."""
    text: str  # Full extracted text
    pages: List[PageContent]
    tables: List[ExtractedTable]
    key_values: List[ExtractedKeyValue]
    entities: List[ExtractedEntity]
    document_type: Optional[str] = None  # Detected document type (invoice, receipt, etc.)
    language: Optional[str] = None
    confidence: float = 1.0
    page_count: int = 0
    model: str = ""
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "pages": [p.to_dict() for p in self.pages],
            "tables": [t.to_dict() for t in self.tables],
            "key_values": [kv.to_dict() for kv in self.key_values],
            "entities": [e.to_dict() for e in self.entities],
            "document_type": self.document_type,
            "language": self.language,
            "confidence": self.confidence,
            "page_count": self.page_count,
            "model": self.model,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }

    def get_key_value_dict(self) -> Dict[str, str]:
        """Get key-values as a simple dictionary."""
        return {kv.key: kv.value for kv in self.key_values}


@dataclass
class DocumentProviderConfig:
    """Configuration for a document provider instance."""
    provider_type: str
    api_key_env: Optional[str] = None
    endpoint: Optional[str] = None
    default_model: Optional[str] = None
    timeout: int = 120
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_type": self.provider_type,
            "api_key_env": self.api_key_env,
            "endpoint": self.endpoint,
            "default_model": self.default_model,
            "timeout": self.timeout,
            "extra_config": self.extra_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentProviderConfig":
        return cls(**data)


class DocumentProvider(ABC):
    """
    Abstract base class for document processing providers.

    Providers must implement:
    - name: Provider identifier
    - analyze(): Full document analysis
    - extract_text(): Simple text extraction
    - capabilities: List of supported capabilities
    - supported_formats: List of supported document types

    Example implementation:

        class MyDocumentProvider(DocumentProvider):
            @property
            def name(self) -> str:
                return "my_document"

            @property
            def capabilities(self) -> List[str]:
                return ["ocr", "layout_analysis", "entity_extraction"]

            @property
            def supported_formats(self) -> List[DocumentType]:
                return [DocumentType.PDF, DocumentType.IMAGE]

            async def analyze(self, document, ...) -> DocumentAnalysisResult:
                # Implement analysis
                pass

            async def extract_text(self, document, ...) -> str:
                # Implement text extraction
                pass
    """

    # Supported pre-built models (override in subclasses)
    PREBUILT_MODELS: Dict[str, str] = {}

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: int = 120,
        **kwargs
    ):
        """
        Initialize the document provider.

        Args:
            api_key: API key for the provider
            endpoint: API endpoint URL
            default_model: Default model to use
            timeout: Request timeout in seconds
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.default_model = default_model
        self.timeout = timeout
        self.extra_config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        List of capabilities this provider supports.

        Values: "ocr", "layout_analysis", "entity_extraction",
                "document_classification", "intelligent_extraction"
        """
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> List[DocumentType]:
        """List of supported document formats."""
        pass

    @abstractmethod
    async def analyze(
        self,
        document: Union[BinaryIO, bytes, str],
        document_type: Optional[DocumentType] = None,
        model: Optional[str] = None,
        extract_tables: bool = True,
        extract_key_values: bool = True,
        extract_entities: bool = False,
        pages: Optional[List[int]] = None,
        **kwargs
    ) -> DocumentAnalysisResult:
        """
        Perform full document analysis.

        Args:
            document: Document data (file-like, bytes, or file path)
            document_type: Document type (auto-detected if not specified)
            model: Model to use (pre-built or custom)
            extract_tables: Extract tables from document
            extract_key_values: Extract form fields/key-value pairs
            extract_entities: Extract named entities
            pages: Specific pages to analyze (1-indexed)
            **kwargs: Provider-specific options

        Returns:
            DocumentAnalysisResult with extracted content
        """
        pass

    @abstractmethod
    async def extract_text(
        self,
        document: Union[BinaryIO, bytes, str],
        document_type: Optional[DocumentType] = None,
        pages: Optional[List[int]] = None,
        **kwargs
    ) -> str:
        """
        Extract plain text from document (OCR only).

        Args:
            document: Document data
            document_type: Document type
            pages: Specific pages to extract
            **kwargs: Provider-specific options

        Returns:
            Extracted text as string
        """
        pass

    async def analyze_invoice(
        self,
        document: Union[BinaryIO, bytes, str],
        **kwargs
    ) -> DocumentAnalysisResult:
        """
        Analyze an invoice document.

        Uses specialized invoice model if available.
        """
        model = self.PREBUILT_MODELS.get("invoice", self.default_model)
        return await self.analyze(document, model=model, **kwargs)

    async def analyze_receipt(
        self,
        document: Union[BinaryIO, bytes, str],
        **kwargs
    ) -> DocumentAnalysisResult:
        """
        Analyze a receipt document.

        Uses specialized receipt model if available.
        """
        model = self.PREBUILT_MODELS.get("receipt", self.default_model)
        return await self.analyze(document, model=model, **kwargs)

    async def analyze_form(
        self,
        document: Union[BinaryIO, bytes, str],
        **kwargs
    ) -> DocumentAnalysisResult:
        """
        Analyze a form document.

        Uses layout model to extract form fields.
        """
        model = self.PREBUILT_MODELS.get("layout", self.default_model)
        return await self.analyze(
            document,
            model=model,
            extract_key_values=True,
            **kwargs
        )

    def _load_document(self, document: Union[BinaryIO, bytes, str]) -> bytes:
        """Load document from various input types."""
        if isinstance(document, bytes):
            return document
        elif isinstance(document, str):
            with open(document, "rb") as f:
                return f.read()
        else:
            return document.read()

    def _detect_document_type(
        self,
        document: bytes,
        path: Optional[str] = None
    ) -> DocumentType:
        """Detect document type from content or path."""
        # Check by magic bytes
        if document[:4] == b'%PDF':
            return DocumentType.PDF
        elif document[:4] == b'PK\x03\x04':
            # Could be DOCX, XLSX, PPTX
            if path:
                ext = path.rsplit(".", 1)[-1].lower()
                if ext in ["docx", "doc"]:
                    return DocumentType.WORD
                elif ext in ["xlsx", "xls"]:
                    return DocumentType.EXCEL
                elif ext in ["pptx", "ppt"]:
                    return DocumentType.POWERPOINT
            return DocumentType.WORD  # Default to Word
        elif document[:8] == b'\x89PNG\r\n\x1a\n':
            return DocumentType.IMAGE
        elif document[:2] == b'\xff\xd8':
            return DocumentType.IMAGE  # JPEG
        elif document[:4] == b'II*\x00' or document[:4] == b'MM\x00*':
            return DocumentType.IMAGE  # TIFF
        else:
            return DocumentType.PDF  # Default

    def _time_call(self, func, *args, **kwargs) -> tuple:
        """Time a function call."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    async def _time_call_async(self, coro) -> tuple:
        """Time an async coroutine."""
        start = time.perf_counter()
        result = await coro
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    def get_config(self) -> DocumentProviderConfig:
        """Get the configuration for this provider instance."""
        return DocumentProviderConfig(
            provider_type=self.name,
            api_key_env=f"{self.name.upper()}_API_KEY",
            endpoint=self.endpoint,
            default_model=self.default_model,
            timeout=self.timeout,
            extra_config=self.extra_config,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.default_model})"


# Document Provider Registry
_DOCUMENT_REGISTRY: Dict[str, type] = {}


def register_document_provider(provider_class: type) -> type:
    """
    Register a document provider class.

    Can be used as a decorator:

        @register_document_provider
        class MyDocumentProvider(DocumentProvider):
            ...
    """
    if not issubclass(provider_class, DocumentProvider):
        raise ValueError(f"{provider_class.__name__} must extend DocumentProvider")

    try:
        temp = object.__new__(provider_class)
        temp.api_key = "temp"
        temp.endpoint = None
        temp.default_model = None
        temp.timeout = 120
        temp.extra_config = {}
        name = temp.name
    except Exception:
        name = provider_class.__name__.lower().replace("provider", "").replace("document", "")

    _DOCUMENT_REGISTRY[name] = provider_class
    return provider_class


def get_document_provider(name: str) -> Optional[type]:
    """Get a document provider class by name."""
    return _DOCUMENT_REGISTRY.get(name)


def list_document_providers() -> List[str]:
    """List all registered document provider names."""
    return list(_DOCUMENT_REGISTRY.keys())


def create_document_provider(config: DocumentProviderConfig) -> DocumentProvider:
    """Create a document provider instance from configuration."""
    import os

    provider_class = get_document_provider(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unknown document provider type: {config.provider_type}")

    api_key = os.environ.get(config.api_key_env) if config.api_key_env else None

    provider: DocumentProvider = provider_class(
        api_key=api_key,
        endpoint=config.endpoint,
        default_model=config.default_model,
        timeout=config.timeout,
        **config.extra_config
    )
    return provider
