"""
Tests for document nodes.

Tests cover:
- DocumentReaderNode
- FormExtractorNode
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

from flowmason_lab.nodes.document import DocumentReaderNode, FormExtractorNode


class TestDocumentReaderNode:
    """Tests for DocumentReaderNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(DocumentReaderNode, "_flowmason_metadata")
        meta = DocumentReaderNode._flowmason_metadata
        assert meta["name"] == "document_reader"
        assert meta["category"] == "document"
        assert "ocr" in meta["tags"]

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = DocumentReaderNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "document" in props
        assert "model" in props
        assert "extract_tables" in props
        assert "extract_key_values" in props
        assert "pages" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = DocumentReaderNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "text" in props
        assert "tables" in props
        assert "key_values" in props
        assert "page_count" in props

    def test_input_validation(self):
        """Test input validation."""
        input_obj = DocumentReaderNode.Input(
            document="/path/to/doc.pdf",
            extract_tables=True,
            extract_key_values=True,
        )
        assert input_obj.document == "/path/to/doc.pdf"
        assert input_obj.extract_tables is True

    @pytest.mark.asyncio
    async def test_execute_without_provider(self):
        """Test execution without provider returns mock."""
        node = DocumentReaderNode()
        input_obj = DocumentReaderNode.Input(document="test.pdf")
        context = Mock()
        context.document = None

        result = await node.execute(input_obj, context)

        assert "Mock document text" in result.text
        assert result.model == "mock"

    @pytest.mark.asyncio
    async def test_execute_with_mocked_provider(self):
        """Test execution with mocked provider."""
        node = DocumentReaderNode()
        input_obj = DocumentReaderNode.Input(
            document="contract.pdf",
            extract_tables=True,
            extract_key_values=True,
        )

        # Create mock table
        mock_table = MagicMock()
        mock_table.rows = [["Item", "Price"], ["Widget", "$10"]]
        mock_table.row_count = 2
        mock_table.column_count = 2
        mock_table.headers = ["Item", "Price"]
        mock_table.caption = None
        mock_table.to_markdown.return_value = "| Item | Price |"

        # Create mock key-value
        mock_kv = MagicMock()
        mock_kv.key = "Date"
        mock_kv.value = "2024-01-01"
        mock_kv.confidence = 0.95

        # Create mock result
        mock_result = MagicMock()
        mock_result.text = "Contract Agreement\n\nThis contract is between..."
        mock_result.tables = [mock_table]
        mock_result.key_values = [mock_kv]
        mock_result.entities = []
        mock_result.pages = []
        mock_result.page_count = 3
        mock_result.document_type = "contract"
        mock_result.language = "en"
        mock_result.confidence = 0.98
        mock_result.model = "prebuilt-document"
        mock_result.duration_ms = 2500
        mock_result.success = True
        mock_result.get_key_value_dict.return_value = {"Date": "2024-01-01"}

        mock_doc = MagicMock()
        mock_doc.analyze = AsyncMock(return_value=mock_result)

        context = Mock()
        context.document = mock_doc

        result = await node.execute(input_obj, context)

        assert "Contract Agreement" in result.text
        assert len(result.tables) == 1
        assert result.key_values["Date"] == "2024-01-01"
        assert result.page_count == 3


class TestFormExtractorNode:
    """Tests for FormExtractorNode."""

    def test_node_metadata(self):
        """Test node has correct metadata."""
        assert hasattr(FormExtractorNode, "_flowmason_metadata")
        meta = FormExtractorNode._flowmason_metadata
        assert meta["name"] == "form_extractor"
        assert meta["category"] == "document"
        assert "invoice" in meta["tags"]

    def test_input_schema(self):
        """Test input schema fields."""
        input_schema = FormExtractorNode.Input.model_json_schema()
        props = input_schema["properties"]
        assert "document" in props
        assert "document_type" in props
        assert "fields" in props
        assert "validate_fields" in props

    def test_output_schema(self):
        """Test output schema fields."""
        output_schema = FormExtractorNode.Output.model_json_schema()
        props = output_schema["properties"]
        assert "fields" in props
        assert "field_details" in props
        assert "line_items" in props
        assert "confidence" in props

    def test_document_type_models(self):
        """Test document type to model mapping."""
        node = FormExtractorNode()
        models = node.DOCUMENT_TYPE_MODELS
        assert models["invoice"] == "prebuilt-invoice"
        assert models["receipt"] == "prebuilt-receipt"
        assert models["id"] == "prebuilt-idDocument"

    def test_input_validation(self):
        """Test input validation."""
        input_obj = FormExtractorNode.Input(
            document="invoice.pdf",
            document_type="invoice",
            fields=["VendorName", "InvoiceTotal"],
        )
        assert input_obj.document_type == "invoice"
        assert "VendorName" in input_obj.fields

    @pytest.mark.asyncio
    async def test_execute_without_provider(self):
        """Test execution without provider returns mock."""
        node = FormExtractorNode()
        input_obj = FormExtractorNode.Input(
            document="test.pdf",
            document_type="invoice",
        )
        context = Mock()
        context.document = None

        result = await node.execute(input_obj, context)

        assert "vendor_name" in result.fields
        assert result.model == "mock"

    @pytest.mark.asyncio
    async def test_execute_invoice(self):
        """Test invoice extraction."""
        node = FormExtractorNode()
        input_obj = FormExtractorNode.Input(
            document="invoice.pdf",
            document_type="invoice",
        )

        # Create mock key-values
        mock_kv1 = MagicMock()
        mock_kv1.key = "VendorName"
        mock_kv1.value = "Acme Corp"
        mock_kv1.confidence = 0.98

        mock_kv2 = MagicMock()
        mock_kv2.key = "InvoiceTotal"
        mock_kv2.value = "$1,500.00"
        mock_kv2.confidence = 0.95

        mock_result = MagicMock()
        mock_result.text = "Invoice"
        mock_result.tables = []
        mock_result.key_values = [mock_kv1, mock_kv2]
        mock_result.entities = []
        mock_result.success = True
        mock_result.model = "prebuilt-invoice"
        mock_result.get_key_value_dict.return_value = {
            "VendorName": "Acme Corp",
            "InvoiceTotal": "$1,500.00",
        }

        mock_doc = MagicMock()
        mock_doc.analyze_invoice = AsyncMock(return_value=mock_result)

        context = Mock()
        context.document = mock_doc

        result = await node.execute(input_obj, context)

        assert result.fields["VendorName"] == "Acme Corp"
        assert result.fields["InvoiceTotal"] == "$1,500.00"
        assert result.document_type == "invoice"

    @pytest.mark.asyncio
    async def test_execute_with_field_filter(self):
        """Test extraction with specific field filter."""
        node = FormExtractorNode()
        input_obj = FormExtractorNode.Input(
            document="invoice.pdf",
            document_type="invoice",
            fields=["VendorName"],  # Only request this field
        )

        mock_kv1 = MagicMock()
        mock_kv1.key = "VendorName"
        mock_kv1.value = "Acme Corp"
        mock_kv1.confidence = 0.98

        mock_kv2 = MagicMock()
        mock_kv2.key = "InvoiceTotal"
        mock_kv2.value = "$1,500.00"
        mock_kv2.confidence = 0.95

        mock_result = MagicMock()
        mock_result.key_values = [mock_kv1, mock_kv2]
        mock_result.tables = []
        mock_result.success = True
        mock_result.model = "prebuilt-invoice"
        mock_result.get_key_value_dict.return_value = {
            "VendorName": "Acme Corp",
            "InvoiceTotal": "$1,500.00",
        }

        mock_doc = MagicMock()
        mock_doc.analyze_invoice = AsyncMock(return_value=mock_result)

        context = Mock()
        context.document = mock_doc

        result = await node.execute(input_obj, context)

        # Should only have VendorName
        assert "VendorName" in result.fields
        assert "InvoiceTotal" not in result.fields

    def test_date_validation(self):
        """Test date validation helper."""
        node = FormExtractorNode()

        # Valid dates
        assert node._is_valid_date("2024-01-01") is True
        assert node._is_valid_date("01/15/2024") is True
        assert node._is_valid_date("January 1, 2024") is True

        # Invalid
        assert node._is_valid_date("not a date") is False
        assert node._is_valid_date("") is False
