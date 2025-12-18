"""
Document Reader Node - Document Processing Component.

Performs intelligent document analysis including OCR, layout analysis,
table extraction, and key-value pair extraction.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="document_reader",
    category="document",
    description="Extract text, tables, and structured data from documents using intelligent OCR",
    icon="file-text",
    color="#6366F1",  # Indigo for documents
    version="1.0.0",
    author="FlowMason",
    tags=["ocr", "document", "extraction", "pdf", "layout"],
    recommended_providers={
        "azure": {
            "model": "prebuilt-document",
        },
    },
    default_provider="azure",
    required_capabilities=["ocr", "layout_analysis"],
)
class DocumentReaderNode:
    """
    Perform intelligent document analysis with OCR and layout understanding.

    The Document Reader extracts structured information from documents:
    - Full text extraction (OCR)
    - Table detection and extraction
    - Key-value pair extraction (form fields)
    - Layout analysis (paragraphs, headers, sections)
    - Named entity recognition

    Use cases:
    - Invoice processing
    - Contract analysis
    - Form digitization
    - Receipt scanning
    - Document classification
    - Data entry automation

    Supported Providers:
    - Azure Document Intelligence (best-in-class)
    """

    class Input(NodeInput):
        document: str = Field(
            description="Document source: file path, URL, or base64-encoded document",
            examples=[
                "/path/to/invoice.pdf",
                "https://example.com/contract.pdf",
            ],
        )
        model: Optional[str] = Field(
            default=None,
            description="Document model to use (provider-specific)",
            examples=[
                "prebuilt-document",
                "prebuilt-layout",
                "prebuilt-read",
            ],
        )
        extract_tables: bool = Field(
            default=True,
            description="Extract tables from the document",
        )
        extract_key_values: bool = Field(
            default=True,
            description="Extract key-value pairs (form fields)",
        )
        extract_entities: bool = Field(
            default=False,
            description="Extract named entities (requires supported model)",
        )
        pages: Optional[List[int]] = Field(
            default=None,
            description="Specific pages to analyze (1-indexed). None = all pages.",
            examples=[[1], [1, 2, 3], [1, 5, 10]],
        )
        locale: Optional[str] = Field(
            default=None,
            description="Locale hint for better OCR accuracy",
            examples=["en-US", "de-DE", "ja-JP"],
        )
        output_format: str = Field(
            default="structured",
            description="Output format: 'structured', 'text_only', 'markdown'",
        )

    class Output(NodeOutput):
        text: str = Field(description="Full extracted text content")
        tables: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Extracted tables with rows and columns",
        )
        key_values: Dict[str, str] = Field(
            default_factory=dict,
            description="Extracted key-value pairs",
        )
        entities: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Extracted named entities",
        )
        pages: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Per-page content and metadata",
        )
        page_count: int = Field(default=0, description="Total number of pages")
        document_type: Optional[str] = Field(
            default=None,
            description="Detected document type (if classified)",
        )
        language: Optional[str] = Field(
            default=None,
            description="Detected document language",
        )
        confidence: float = Field(
            default=1.0,
            description="Overall extraction confidence",
        )
        model: str = Field(default="", description="Model used for analysis")
        duration_ms: int = Field(
            default=0,
            description="Processing time in milliseconds",
        )

    class Config:
        requires_llm: bool = False  # Uses document provider, not LLM
        timeout_seconds: int = 180  # Document processing can be slow

    async def execute(self, input: Input, context) -> Output:
        """
        Execute document analysis using the document provider.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with extracted content and metadata
        """
        # Get document provider from context
        document_provider = getattr(context, "document", None)

        if not document_provider:
            # Fallback for testing
            return self.Output(
                text=f"[Mock document text from: {input.document}]",
                page_count=1,
                model="mock",
            )

        # Perform document analysis
        result = await document_provider.analyze(
            document=input.document,
            model=input.model,
            extract_tables=input.extract_tables,
            extract_key_values=input.extract_key_values,
            extract_entities=input.extract_entities,
            pages=input.pages,
            locale=input.locale,
        )

        # Handle error case
        if not result.success:
            raise ValueError(result.error or "Document analysis failed")

        # Format tables
        tables = []
        for table in result.tables:
            table_data = {
                "rows": table.rows,
                "row_count": table.row_count,
                "column_count": table.column_count,
            }
            if table.headers:
                table_data["headers"] = table.headers
            if table.caption:
                table_data["caption"] = table.caption
            tables.append(table_data)

        # Format key-values as dict
        key_values = result.get_key_value_dict()

        # Format entities
        entities = []
        for entity in result.entities:
            entities.append({
                "text": entity.text,
                "type": entity.entity_type,
                "confidence": entity.confidence,
            })

        # Format pages
        pages = []
        for page in result.pages:
            page_data = {
                "page_number": page.page_number,
                "text": page.text,
            }
            if page.width and page.height:
                page_data["dimensions"] = {
                    "width": page.width,
                    "height": page.height,
                }
            if page.angle:
                page_data["rotation"] = page.angle
            pages.append(page_data)

        # Generate output based on format
        if input.output_format == "text_only":
            output_text = result.text
        elif input.output_format == "markdown":
            # Convert to markdown with tables
            parts = [result.text]
            for i, table in enumerate(result.tables):
                parts.append(f"\n\n### Table {i+1}\n")
                parts.append(table.to_markdown())
            output_text = "\n".join(parts)
        else:
            output_text = result.text

        return self.Output(
            text=output_text,
            tables=tables,
            key_values=key_values,
            entities=entities,
            pages=pages,
            page_count=result.page_count,
            document_type=result.document_type,
            language=result.language,
            confidence=result.confidence,
            model=result.model,
            duration_ms=result.duration_ms,
        )
