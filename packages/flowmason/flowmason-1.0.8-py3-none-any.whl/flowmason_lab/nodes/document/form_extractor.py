"""
Form Extractor Node - Document Processing Component.

Extracts specific fields from structured documents like
invoices, receipts, and forms.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="form_extractor",
    category="document",
    description="Extract specific fields from invoices, receipts, and forms",
    icon="clipboard-list",
    color="#6366F1",  # Indigo for documents
    version="1.0.0",
    author="FlowMason",
    tags=["ocr", "form", "invoice", "receipt", "extraction"],
    recommended_providers={
        "azure": {
            "model": "prebuilt-invoice",
        },
    },
    default_provider="azure",
    required_capabilities=["intelligent_extraction"],
)
class FormExtractorNode:
    """
    Extract specific fields from structured documents.

    The Form Extractor uses specialized pre-built models to
    extract known fields from common document types.

    Supported Document Types:
    - invoice: Vendor, amounts, line items, dates
    - receipt: Merchant, totals, items, payment method
    - id: Name, DOB, document number, expiration
    - business_card: Name, title, company, contact info
    - tax_w2: Employer, wages, withholdings
    - contract: Parties, dates, terms

    Use cases:
    - Accounts payable automation
    - Expense reporting
    - Identity verification
    - Contract management
    - Tax document processing
    """

    class Input(NodeInput):
        document: str = Field(
            description="Document source: file path, URL, or base64-encoded document",
            examples=[
                "/path/to/invoice.pdf",
                "https://example.com/receipt.jpg",
            ],
        )
        document_type: str = Field(
            description="Type of document to extract",
            examples=["invoice", "receipt", "id", "business_card"],
        )
        fields: Optional[List[str]] = Field(
            default=None,
            description="Specific fields to extract (None = all available)",
            examples=[
                ["vendor_name", "invoice_total", "due_date"],
                ["merchant_name", "total", "transaction_date"],
            ],
        )
        validate_fields: bool = Field(
            default=False,
            description="Validate extracted fields against expected patterns",
        )
        include_confidence: bool = Field(
            default=True,
            description="Include confidence scores for each field",
        )
        include_bounding_boxes: bool = Field(
            default=False,
            description="Include bounding box coordinates for fields",
        )

    class Output(NodeOutput):
        fields: Dict[str, Any] = Field(
            description="Extracted fields with values",
        )
        field_details: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Detailed field information (confidence, bbox)",
        )
        line_items: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Line items for invoices/receipts",
        )
        document_type: str = Field(
            default="",
            description="Document type that was processed",
        )
        confidence: float = Field(
            default=1.0,
            description="Overall extraction confidence",
        )
        validation_errors: List[str] = Field(
            default_factory=list,
            description="Validation errors if validate_fields is True",
        )
        model: str = Field(default="", description="Model used for extraction")

    class Config:
        requires_llm: bool = False
        timeout_seconds: int = 120

    # Field mappings for common document types
    DOCUMENT_TYPE_MODELS = {
        "invoice": "prebuilt-invoice",
        "receipt": "prebuilt-receipt",
        "id": "prebuilt-idDocument",
        "business_card": "prebuilt-businessCard",
        "tax_w2": "prebuilt-tax.us.w2",
        "health_insurance": "prebuilt-healthInsuranceCard.us",
        "contract": "prebuilt-contract",
    }

    # Expected fields per document type
    EXPECTED_FIELDS = {
        "invoice": [
            "VendorName", "VendorAddress", "CustomerName", "CustomerAddress",
            "InvoiceId", "InvoiceDate", "DueDate", "PurchaseOrder",
            "SubTotal", "TotalTax", "InvoiceTotal", "AmountDue",
            "BillingAddress", "ShippingAddress", "Items"
        ],
        "receipt": [
            "MerchantName", "MerchantAddress", "MerchantPhoneNumber",
            "TransactionDate", "TransactionTime", "Total", "Subtotal",
            "TotalTax", "Tip", "Items"
        ],
        "id": [
            "FirstName", "LastName", "DocumentNumber", "DateOfBirth",
            "DateOfExpiration", "Sex", "Address", "CountryRegion"
        ],
        "business_card": [
            "FirstName", "LastName", "CompanyName", "JobTitle",
            "Department", "Email", "Phone", "Mobile", "Fax",
            "Address", "Website"
        ],
    }

    async def execute(self, input: Input, context) -> Output:
        """
        Execute form extraction using the document provider.

        Args:
            input: The validated Input model
            context: Execution context with providers

        Returns:
            Output with extracted fields and metadata
        """
        # Get document provider from context
        document_provider = getattr(context, "document", None)

        if not document_provider:
            # Fallback for testing
            mock_fields = {"vendor_name": "Mock Vendor", "total": "$100.00"}
            return self.Output(
                fields=mock_fields,
                document_type=input.document_type,
                model="mock",
            )

        # Get model for document type
        model = self.DOCUMENT_TYPE_MODELS.get(
            input.document_type.lower(),
            "prebuilt-document"
        )

        # Use specialized method if available, otherwise use generic analyze
        if input.document_type.lower() == "invoice":
            result = await document_provider.analyze_invoice(input.document)
        elif input.document_type.lower() == "receipt":
            result = await document_provider.analyze_receipt(input.document)
        else:
            result = await document_provider.analyze(
                document=input.document,
                model=model,
                extract_key_values=True,
            )

        # Handle error case
        if not result.success:
            raise ValueError(result.error or "Form extraction failed")

        # Extract fields from result
        all_fields = result.get_key_value_dict()

        # Filter to requested fields if specified
        if input.fields:
            fields = {k: v for k, v in all_fields.items() if k in input.fields}
        else:
            fields = all_fields

        # Build field details with confidence
        field_details = []
        for kv in result.key_values:
            if input.fields and kv.key not in input.fields:
                continue

            detail = {
                "key": kv.key,
                "value": kv.value,
            }
            if input.include_confidence:
                detail["confidence"] = kv.confidence
            if input.include_bounding_boxes and kv.value_bounding_box:
                detail["bounding_box"] = kv.value_bounding_box.to_dict()

            field_details.append(detail)

        # Extract line items (for invoices/receipts)
        line_items = []
        if input.document_type.lower() in ["invoice", "receipt"]:
            # Line items are typically in tables
            for table in result.tables:
                if table.headers:
                    for row in table.rows:
                        if row != table.headers:
                            item = dict(zip(table.headers, row))
                            line_items.append(item)

        # Validate fields if requested
        validation_errors = []
        if input.validate_fields:
            validation_errors = self._validate_fields(
                fields,
                input.document_type.lower()
            )

        # Calculate overall confidence
        confidences = [kv.confidence for kv in result.key_values if kv.confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0

        return self.Output(
            fields=fields,
            field_details=field_details,
            line_items=line_items,
            document_type=input.document_type,
            confidence=avg_confidence,
            validation_errors=validation_errors,
            model=result.model,
        )

    def _validate_fields(
        self,
        fields: Dict[str, Any],
        document_type: str
    ) -> List[str]:
        """Validate extracted fields against expected patterns."""
        errors = []

        # Check for expected fields
        expected = self.EXPECTED_FIELDS.get(document_type, [])
        for field in expected:
            if field.lower() in [f.lower() for f in fields.keys()]:
                continue
            # Only warn about commonly expected fields
            if field in ["InvoiceTotal", "Total", "VendorName", "MerchantName"]:
                errors.append(f"Expected field '{field}' not found")

        # Validate date formats
        date_fields = ["InvoiceDate", "DueDate", "TransactionDate", "DateOfBirth"]
        for field in date_fields:
            if field in fields:
                value = fields[field]
                if value and not self._is_valid_date(value):
                    errors.append(f"Invalid date format in '{field}': {value}")

        return errors

    def _is_valid_date(self, value: str) -> bool:
        """Check if a string looks like a valid date."""
        import re
        # Common date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\w+ \d{1,2}, \d{4}',  # Month DD, YYYY
        ]
        return any(re.search(p, str(value)) for p in patterns)
