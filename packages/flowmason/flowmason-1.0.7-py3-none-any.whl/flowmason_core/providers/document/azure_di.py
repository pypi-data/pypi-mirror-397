"""
Azure Document Intelligence Provider

Best-in-class document processing using Azure AI Document Intelligence
(formerly Form Recognizer).
"""

import io
import os
from typing import Any, BinaryIO, Dict, List, Optional, Union

from .base import (
    BoundingBox,
    DocumentAnalysisResult,
    DocumentProvider,
    DocumentType,
    ExtractedEntity,
    ExtractedKeyValue,
    ExtractedTable,
    ExtractedText,
    PageContent,
    TableCell,
    register_document_provider,
)


@register_document_provider
class AzureDocumentIntelligenceProvider(DocumentProvider):
    """
    Document provider for Azure AI Document Intelligence.

    Azure Document Intelligence is Microsoft's best-in-class document
    processing service, offering:

    Pre-built Models:
    - prebuilt-read: OCR + basic layout
    - prebuilt-layout: Advanced layout with tables, forms
    - prebuilt-document: General document understanding
    - prebuilt-invoice: Invoice extraction
    - prebuilt-receipt: Receipt extraction
    - prebuilt-idDocument: ID card extraction
    - prebuilt-businessCard: Business card extraction
    - prebuilt-tax.us.w2: US W-2 tax forms
    - prebuilt-healthInsuranceCard.us: US health insurance cards

    Custom Models:
    - Train on your own documents for specialized extraction

    Features:
    - 300+ languages supported
    - Tables with row/column headers
    - Key-value pair extraction
    - Named entity recognition
    - Document classification
    - Handwriting recognition
    """

    # Pre-built models
    PREBUILT_MODELS = {
        "read": "prebuilt-read",
        "layout": "prebuilt-layout",
        "document": "prebuilt-document",
        "invoice": "prebuilt-invoice",
        "receipt": "prebuilt-receipt",
        "id": "prebuilt-idDocument",
        "business_card": "prebuilt-businessCard",
        "tax_w2": "prebuilt-tax.us.w2",
        "health_insurance": "prebuilt-healthInsuranceCard.us",
        "contract": "prebuilt-contract",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: int = 120,
        api_version: str = "2024-02-29-preview",
        **kwargs
    ):
        """
        Initialize Azure Document Intelligence provider.

        Args:
            api_key: Azure API key (or set AZURE_DOCUMENT_INTELLIGENCE_KEY)
            endpoint: Azure endpoint URL (or set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT)
            default_model: Default model (default: prebuilt-document)
            timeout: Request timeout
            api_version: API version
            **kwargs: Additional options
        """
        api_key = api_key or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        endpoint = endpoint or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")

        if not api_key:
            raise ValueError(
                "Azure API key required. Set AZURE_DOCUMENT_INTELLIGENCE_KEY env var or pass api_key."
            )
        if not endpoint:
            raise ValueError(
                "Azure endpoint required. Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT env var or pass endpoint."
            )

        super().__init__(
            api_key=api_key,
            endpoint=endpoint,
            default_model=default_model or "prebuilt-document",
            timeout=timeout,
            **kwargs
        )
        self.api_version = api_version
        self._client = None

    @property
    def client(self):
        """Lazy-load the Azure Document Intelligence client."""
        if self._client is None:
            try:
                from azure.ai.documentintelligence import DocumentIntelligenceClient
                from azure.core.credentials import AzureKeyCredential

                self._client = DocumentIntelligenceClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.api_key),
                )
            except ImportError:
                raise ImportError(
                    "azure-ai-documentintelligence package required. "
                    "Install with: pip install azure-ai-documentintelligence"
                )
        return self._client

    @property
    def name(self) -> str:
        return "azure_document_intelligence"

    @property
    def capabilities(self) -> List[str]:
        return [
            "ocr",
            "layout_analysis",
            "entity_extraction",
            "document_classification",
            "intelligent_extraction",
        ]

    @property
    def supported_formats(self) -> List[DocumentType]:
        return [
            DocumentType.PDF,
            DocumentType.IMAGE,
            DocumentType.WORD,
            DocumentType.EXCEL,
            DocumentType.POWERPOINT,
        ]

    async def analyze(
        self,
        document: Union[BinaryIO, bytes, str],
        document_type: Optional[DocumentType] = None,
        model: Optional[str] = None,
        extract_tables: bool = True,
        extract_key_values: bool = True,
        extract_entities: bool = False,
        pages: Optional[List[int]] = None,
        locale: Optional[str] = None,
        **kwargs
    ) -> DocumentAnalysisResult:
        """
        Analyze document using Azure Document Intelligence.

        Args:
            document: Document data (file-like, bytes, or file path)
            document_type: Document type (auto-detected)
            model: Model ID (prebuilt-* or custom model ID)
            extract_tables: Extract tables
            extract_key_values: Extract key-value pairs
            extract_entities: Extract named entities (requires prebuilt-document)
            pages: Page range (e.g., [1, 3] for pages 1 and 3)
            locale: Locale hint (e.g., "en-US")
            **kwargs: Additional options

        Returns:
            DocumentAnalysisResult with extracted content
        """
        import time
        model = model or self.default_model

        try:
            # Load document
            doc_data = self._load_document(document)
            path = document if isinstance(document, str) else None

            # Build request parameters
            features = []
            if extract_key_values:
                features.append("keyValuePairs")
            if extract_entities:
                features.append("entities")

            # Build pages string
            pages_str = None
            if pages:
                pages_str = ",".join(str(p) for p in pages)

            start = time.perf_counter()

            # Analyze document
            poller = self.client.begin_analyze_document(
                model_id=model,
                body=doc_data,
                content_type="application/octet-stream",
                pages=pages_str,
                locale=locale,
                features=features if features else None,
            )
            result = poller.result()

            duration_ms = int((time.perf_counter() - start) * 1000)

            # Extract full text
            full_text = result.content if hasattr(result, 'content') else ""

            # Extract pages
            extracted_pages = []
            if hasattr(result, 'pages') and result.pages:
                for page in result.pages:
                    page_content = PageContent(
                        page_number=page.page_number,
                        text=self._get_page_text(page, result),
                        width=page.width,
                        height=page.height,
                        angle=page.angle if hasattr(page, 'angle') else 0.0,
                    )
                    extracted_pages.append(page_content)

            # Extract tables
            tables = []
            if extract_tables and hasattr(result, 'tables') and result.tables:
                for table in result.tables:
                    tables.append(self._parse_table(table))

            # Extract key-value pairs
            key_values = []
            if extract_key_values and hasattr(result, 'key_value_pairs') and result.key_value_pairs:
                for kv in result.key_value_pairs:
                    key = kv.key.content if kv.key else ""
                    value = kv.value.content if kv.value else ""
                    confidence = kv.confidence if hasattr(kv, 'confidence') else 1.0

                    key_values.append(ExtractedKeyValue(
                        key=key,
                        value=value,
                        confidence=confidence,
                    ))

            # Extract entities
            entities = []
            if extract_entities and hasattr(result, 'entities') and result.entities:
                for entity in result.entities:
                    entities.append(ExtractedEntity(
                        text=entity.content,
                        entity_type=entity.category,
                        confidence=entity.confidence if hasattr(entity, 'confidence') else 1.0,
                    ))

            # Detect document type if available
            doc_type_detected = None
            if hasattr(result, 'documents') and result.documents:
                doc_type_detected = result.documents[0].doc_type if result.documents[0].doc_type else None

            # Get language
            language = None
            if hasattr(result, 'languages') and result.languages:
                language = result.languages[0].locale if result.languages else None

            return DocumentAnalysisResult(
                text=full_text,
                pages=extracted_pages,
                tables=tables,
                key_values=key_values,
                entities=entities,
                document_type=doc_type_detected,
                language=language,
                confidence=1.0,
                page_count=len(extracted_pages),
                model=model,
                duration_ms=duration_ms,
                success=True,
                raw_response=result.as_dict() if hasattr(result, 'as_dict') else {},
            )

        except Exception as e:
            return DocumentAnalysisResult(
                text="",
                pages=[],
                tables=[],
                key_values=[],
                entities=[],
                model=model,
                success=False,
                error=str(e),
            )

    async def extract_text(
        self,
        document: Union[BinaryIO, bytes, str],
        document_type: Optional[DocumentType] = None,
        pages: Optional[List[int]] = None,
        **kwargs
    ) -> str:
        """
        Extract plain text using prebuilt-read model.

        This is the fastest option for simple OCR.
        """
        result = await self.analyze(
            document=document,
            document_type=document_type,
            model="prebuilt-read",
            extract_tables=False,
            extract_key_values=False,
            extract_entities=False,
            pages=pages,
            **kwargs
        )

        if result.success:
            return result.text
        raise ValueError(result.error or "Text extraction failed")

    def _get_page_text(self, page, result) -> str:
        """Extract text for a specific page."""
        if not hasattr(result, 'content'):
            return ""

        # Get text from spans
        if hasattr(page, 'spans') and page.spans:
            texts = []
            for span in page.spans:
                start = span.offset
                end = span.offset + span.length
                texts.append(result.content[start:end])
            return "".join(texts)

        return ""

    def _parse_table(self, table) -> ExtractedTable:
        """Parse an Azure table into our format."""
        cells = []
        rows: List[List[str]] = []
        headers: List[str] = []

        # Parse cells
        if hasattr(table, 'cells') and table.cells:
            # Initialize rows matrix
            row_count = table.row_count if hasattr(table, 'row_count') else 0
            col_count = table.column_count if hasattr(table, 'column_count') else 0

            rows = [[""] * col_count for _ in range(row_count)]

            for cell in table.cells:
                content = cell.content if hasattr(cell, 'content') else ""
                row_idx = cell.row_index if hasattr(cell, 'row_index') else 0
                col_idx = cell.column_index if hasattr(cell, 'column_index') else 0
                is_header = cell.kind == "columnHeader" if hasattr(cell, 'kind') else False

                cells.append(TableCell(
                    content=content,
                    row_index=row_idx,
                    column_index=col_idx,
                    row_span=cell.row_span if hasattr(cell, 'row_span') else 1,
                    column_span=cell.column_span if hasattr(cell, 'column_span') else 1,
                    is_header=is_header,
                ))

                # Fill rows matrix
                if row_idx < len(rows) and col_idx < len(rows[row_idx]):
                    rows[row_idx][col_idx] = content

                # Collect headers
                if is_header:
                    while len(headers) <= col_idx:
                        headers.append("")
                    headers[col_idx] = content

        # Get bounding box
        bbox = None
        if hasattr(table, 'bounding_regions') and table.bounding_regions:
            region = table.bounding_regions[0]
            if hasattr(region, 'polygon') and region.polygon:
                # Convert polygon to bounding box
                xs = [region.polygon[i] for i in range(0, len(region.polygon), 2)]
                ys = [region.polygon[i] for i in range(1, len(region.polygon), 2)]
                bbox = BoundingBox(
                    x=min(xs),
                    y=min(ys),
                    width=max(xs) - min(xs),
                    height=max(ys) - min(ys),
                    page=region.page_number if hasattr(region, 'page_number') else 1,
                )

        return ExtractedTable(
            cells=cells,
            rows=rows,
            headers=headers if headers else None,
            row_count=table.row_count if hasattr(table, 'row_count') else len(rows),
            column_count=table.column_count if hasattr(table, 'column_count') else (len(rows[0]) if rows else 0),
            bounding_box=bbox,
        )

    async def classify_document(
        self,
        document: Union[BinaryIO, bytes, str],
        classifier_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Classify a document using a custom classifier.

        Args:
            document: Document data
            classifier_id: Custom classifier ID

        Returns:
            Classification result with document type and confidence
        """
        import time

        try:
            doc_data = self._load_document(document)

            start = time.perf_counter()
            poller = self.client.begin_classify_document(
                classifier_id=classifier_id,
                body=doc_data,
                content_type="application/octet-stream",
            )
            result = poller.result()
            duration_ms = int((time.perf_counter() - start) * 1000)

            classifications = []
            if hasattr(result, 'documents') and result.documents:
                for doc in result.documents:
                    classifications.append({
                        "doc_type": doc.doc_type,
                        "confidence": doc.confidence,
                        "page_range": [doc.bounding_regions[0].page_number] if doc.bounding_regions else [],
                    })

            return {
                "classifications": classifications,
                "duration_ms": duration_ms,
                "success": True,
            }

        except Exception as e:
            return {
                "classifications": [],
                "success": False,
                "error": str(e),
            }
