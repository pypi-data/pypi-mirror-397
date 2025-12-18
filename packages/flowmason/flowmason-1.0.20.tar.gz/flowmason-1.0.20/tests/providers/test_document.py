"""
Tests for document providers.

Tests cover:
- DocumentProvider base class
- DocumentAnalysisResult and related dataclasses
- Azure Document Intelligence provider
- Registry functions
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from flowmason_core.providers.document import (
    DocumentProvider,
    DocumentType,
    DocumentAnalysisResult,
    PageContent,
    ExtractedText,
    ExtractedTable,
    TableCell,
    ExtractedKeyValue,
    ExtractedEntity,
    BoundingBox,
    DocumentProviderConfig,
    AzureDocumentIntelligenceProvider,
    register_document_provider,
    get_document_provider,
    list_document_providers,
)


class TestDocumentType:
    """Tests for DocumentType enum."""

    def test_document_types(self):
        """Test document type values."""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.IMAGE.value == "image"
        assert DocumentType.WORD.value == "word"
        assert DocumentType.EXCEL.value == "excel"


class TestBoundingBox:
    """Tests for BoundingBox dataclass."""

    def test_basic_bbox(self):
        """Test basic bounding box."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.5, height=0.3)
        assert bbox.x == 0.1
        assert bbox.width == 0.5
        assert bbox.page == 1

    def test_bbox_with_page(self):
        """Test bounding box on specific page."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.5, height=0.3, page=3)
        assert bbox.page == 3

    def test_to_dict(self):
        """Test serialization."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.5, height=0.3)
        d = bbox.to_dict()
        assert d["x"] == 0.1
        assert d["width"] == 0.5


class TestExtractedTable:
    """Tests for ExtractedTable dataclass."""

    def test_basic_table(self):
        """Test basic table."""
        cells = [
            TableCell(content="A1", row_index=0, column_index=0, is_header=True),
            TableCell(content="B1", row_index=0, column_index=1, is_header=True),
            TableCell(content="A2", row_index=1, column_index=0),
            TableCell(content="B2", row_index=1, column_index=1),
        ]
        table = ExtractedTable(
            cells=cells,
            rows=[["A1", "B1"], ["A2", "B2"]],
            headers=["A1", "B1"],
            row_count=2,
            column_count=2,
        )
        assert table.row_count == 2
        assert table.column_count == 2
        assert len(table.cells) == 4

    def test_to_markdown(self):
        """Test markdown conversion."""
        table = ExtractedTable(
            cells=[],
            rows=[["Name", "Age"], ["John", "30"]],
            headers=["Name", "Age"],
            row_count=2,
            column_count=2,
        )
        md = table.to_markdown()
        assert "| Name | Age |" in md
        assert "| --- | --- |" in md
        assert "| John | 30 |" in md


class TestExtractedKeyValue:
    """Tests for ExtractedKeyValue dataclass."""

    def test_basic_key_value(self):
        """Test basic key-value pair."""
        kv = ExtractedKeyValue(
            key="Invoice Number",
            value="INV-001",
            confidence=0.95,
        )
        assert kv.key == "Invoice Number"
        assert kv.value == "INV-001"
        assert kv.confidence == 0.95

    def test_to_dict(self):
        """Test serialization."""
        kv = ExtractedKeyValue(key="Total", value="$100")
        d = kv.to_dict()
        assert d["key"] == "Total"
        assert d["value"] == "$100"


class TestDocumentAnalysisResult:
    """Tests for DocumentAnalysisResult dataclass."""

    def test_basic_result(self):
        """Test basic analysis result."""
        result = DocumentAnalysisResult(
            text="Sample document text",
            pages=[],
            tables=[],
            key_values=[],
            entities=[],
            page_count=1,
        )
        assert result.text == "Sample document text"
        assert result.success is True
        assert result.page_count == 1

    def test_result_with_key_values(self):
        """Test result with key-values."""
        result = DocumentAnalysisResult(
            text="Invoice",
            pages=[],
            tables=[],
            key_values=[
                ExtractedKeyValue(key="Total", value="$100"),
                ExtractedKeyValue(key="Date", value="2024-01-01"),
            ],
            entities=[],
        )
        kv_dict = result.get_key_value_dict()
        assert kv_dict["Total"] == "$100"
        assert kv_dict["Date"] == "2024-01-01"

    def test_error_result(self):
        """Test error result."""
        result = DocumentAnalysisResult(
            text="",
            pages=[],
            tables=[],
            key_values=[],
            entities=[],
            success=False,
            error="Document too large",
        )
        assert result.success is False
        assert result.error == "Document too large"

    def test_to_dict(self):
        """Test serialization."""
        result = DocumentAnalysisResult(
            text="Test",
            pages=[],
            tables=[],
            key_values=[],
            entities=[],
            model="prebuilt-document",
            duration_ms=1500,
        )
        d = result.to_dict()
        assert d["text"] == "Test"
        assert d["model"] == "prebuilt-document"
        assert d["duration_ms"] == 1500


class TestDocumentRegistry:
    """Tests for document provider registry."""

    def test_list_providers(self):
        """Test listing providers."""
        providers = list_document_providers()
        assert "azure_document_intelligence" in providers

    def test_get_provider(self):
        """Test getting provider class."""
        provider_class = get_document_provider("azure_document_intelligence")
        assert provider_class is not None
        assert issubclass(provider_class, DocumentProvider)


class TestAzureDocumentIntelligenceProvider:
    """Tests for Azure Document Intelligence provider."""

    def test_init_requires_api_key(self):
        """Test init requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                AzureDocumentIntelligenceProvider()

    def test_init_requires_endpoint(self):
        """Test init requires endpoint."""
        with patch.dict("os.environ", {"AZURE_DOCUMENT_INTELLIGENCE_KEY": "key"}, clear=True):
            with pytest.raises(ValueError, match="endpoint required"):
                AzureDocumentIntelligenceProvider()

    def test_init_with_credentials(self):
        """Test init with credentials."""
        provider = AzureDocumentIntelligenceProvider(
            api_key="test-key",
            endpoint="https://test.cognitiveservices.azure.com",
        )
        assert provider.api_key == "test-key"
        assert provider.endpoint == "https://test.cognitiveservices.azure.com"
        assert provider.name == "azure_document_intelligence"

    def test_capabilities(self):
        """Test capabilities."""
        provider = AzureDocumentIntelligenceProvider(
            api_key="test-key",
            endpoint="https://test.cognitiveservices.azure.com",
        )
        caps = provider.capabilities
        assert "ocr" in caps
        assert "layout_analysis" in caps
        assert "entity_extraction" in caps
        assert "intelligent_extraction" in caps

    def test_supported_formats(self):
        """Test supported document formats."""
        provider = AzureDocumentIntelligenceProvider(
            api_key="test-key",
            endpoint="https://test.cognitiveservices.azure.com",
        )
        formats = provider.supported_formats
        assert DocumentType.PDF in formats
        assert DocumentType.IMAGE in formats
        assert DocumentType.WORD in formats

    def test_prebuilt_models(self):
        """Test prebuilt models mapping."""
        provider = AzureDocumentIntelligenceProvider(
            api_key="test-key",
            endpoint="https://test.cognitiveservices.azure.com",
        )
        models = provider.PREBUILT_MODELS
        assert models["invoice"] == "prebuilt-invoice"
        assert models["receipt"] == "prebuilt-receipt"
        assert models["layout"] == "prebuilt-layout"

    @pytest.mark.asyncio
    async def test_analyze_mock(self):
        """Test analysis with mocked client."""
        provider = AzureDocumentIntelligenceProvider(
            api_key="test-key",
            endpoint="https://test.cognitiveservices.azure.com",
        )

        # Mock the client and result
        mock_result = MagicMock()
        mock_result.content = "Extracted text from document"
        mock_result.pages = []
        mock_result.tables = []
        mock_result.key_value_pairs = []
        mock_result.entities = []
        mock_result.documents = []
        mock_result.languages = []
        mock_result.as_dict.return_value = {}

        mock_poller = MagicMock()
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_analyze_document.return_value = mock_poller
        provider._client = mock_client

        # Mock file loading
        with patch.object(provider, '_load_document', return_value=b"pdf_bytes"):
            result = await provider.analyze("test.pdf")

        assert result.success is True
        assert result.text == "Extracted text from document"

    @pytest.mark.asyncio
    async def test_extract_text_mock(self):
        """Test text extraction with mocked client."""
        provider = AzureDocumentIntelligenceProvider(
            api_key="test-key",
            endpoint="https://test.cognitiveservices.azure.com",
        )

        # Mock analyze to return text
        async def mock_analyze(*args, **kwargs):
            return DocumentAnalysisResult(
                text="Simple extracted text",
                pages=[],
                tables=[],
                key_values=[],
                entities=[],
                success=True,
            )

        provider.analyze = mock_analyze

        text = await provider.extract_text("test.png")
        assert text == "Simple extracted text"
