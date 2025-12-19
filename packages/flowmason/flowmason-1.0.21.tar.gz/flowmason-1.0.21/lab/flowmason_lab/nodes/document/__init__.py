"""
FlowMason Document Nodes

Provides intelligent document processing nodes for OCR,
layout analysis, and structured data extraction.

Built-in Nodes:
- document_reader: Full document analysis with tables and key-values
- form_extractor: Extract specific fields from invoices, receipts, forms

Usage:
    # Full document analysis
    {
        "id": "analyze-contract",
        "component": "document_reader",
        "inputs": {
            "document": "{{input.file_path}}",
            "extract_tables": true,
            "extract_key_values": true
        }
    }

    # Invoice extraction
    {
        "id": "process-invoice",
        "component": "form_extractor",
        "inputs": {
            "document": "{{input.invoice_path}}",
            "document_type": "invoice",
            "fields": ["VendorName", "InvoiceTotal", "DueDate"]
        }
    }
"""

from .document_reader import DocumentReaderNode
from .form_extractor import FormExtractorNode

__all__ = [
    "DocumentReaderNode",
    "FormExtractorNode",
]
