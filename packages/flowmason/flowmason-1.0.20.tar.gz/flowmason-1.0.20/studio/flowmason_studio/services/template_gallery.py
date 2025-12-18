"""
Built-in Template Gallery.

Provides starter pipeline templates for common use cases.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineTemplate:
    """A starter pipeline template."""

    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    difficulty: str  # "beginner", "intermediate", "advanced"
    estimated_time: str  # e.g., "5 minutes"
    use_case: str  # Brief description of when to use

    # Template content
    pipeline: Dict[str, Any]
    sample_input: Dict[str, Any]

    # Documentation
    documentation: str = ""
    prerequisites: List[str] = field(default_factory=list)


# Built-in templates
TEMPLATES: List[PipelineTemplate] = [
    # ============================================
    # Content Generation Templates
    # ============================================
    PipelineTemplate(
        id="blog-post-generator",
        name="Blog Post Generator",
        description="Generate well-structured blog posts on any topic",
        category="content",
        tags=["writing", "blog", "content-generation"],
        difficulty="beginner",
        estimated_time="5 minutes",
        use_case="Creating blog posts, articles, or long-form content",
        pipeline={
            "name": "Blog Post Generator",
            "description": "Generate a blog post with outline, draft, and review",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "outline",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Create a detailed outline for a blog post about {{topic}}. Include:\n- Title\n- Introduction hook\n- 3-5 main sections with subpoints\n- Conclusion\n\nTarget audience: {{audience}}",
                        "model": "claude-3-5-sonnet-latest"
                    }
                },
                {
                    "id": "draft",
                    "component_type": "generator",
                    "depends_on": ["outline"],
                    "config": {
                        "prompt": "Using this outline:\n\n{{stages.outline.output.content}}\n\nWrite a complete blog post. Make it engaging, informative, and well-structured. Target length: {{word_count}} words.",
                        "model": "claude-3-5-sonnet-latest"
                    }
                },
                {
                    "id": "review",
                    "component_type": "critic",
                    "depends_on": ["draft"],
                    "config": {
                        "focus": "clarity, engagement, SEO-friendliness",
                        "improve": True
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Blog post topic"},
                    "audience": {"type": "string", "description": "Target audience"},
                    "word_count": {"type": "integer", "default": 1000}
                },
                "required": ["topic"]
            }
        },
        sample_input={
            "topic": "Getting Started with AI Automation",
            "audience": "Small business owners",
            "word_count": 1000
        },
        documentation="""
## Blog Post Generator

This template creates blog posts through a three-stage process:

1. **Outline**: Creates a structured outline for the post
2. **Draft**: Writes the full blog post based on the outline
3. **Review**: Reviews and improves the draft for clarity

### Customization

- Adjust the prompt in each stage for different writing styles
- Change the model for speed/quality tradeoffs
- Modify word count in the input
""",
        prerequisites=["Anthropic API key"]
    ),

    PipelineTemplate(
        id="email-writer",
        name="Professional Email Writer",
        description="Compose professional emails for any situation",
        category="content",
        tags=["email", "business", "communication"],
        difficulty="beginner",
        estimated_time="2 minutes",
        use_case="Writing business emails, follow-ups, or formal communications",
        pipeline={
            "name": "Email Writer",
            "description": "Write professional emails with appropriate tone",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "write-email",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Write a professional email.\n\nPurpose: {{purpose}}\nRecipient: {{recipient}}\nTone: {{tone}}\nKey points to include:\n{{key_points}}\n\nWrite a complete email with subject line, greeting, body, and sign-off.",
                        "model": "claude-3-5-sonnet-latest"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "purpose": {"type": "string"},
                    "recipient": {"type": "string"},
                    "tone": {"type": "string", "enum": ["formal", "friendly", "urgent", "apologetic"]},
                    "key_points": {"type": "string"}
                },
                "required": ["purpose", "recipient"]
            }
        },
        sample_input={
            "purpose": "Follow up on a project proposal",
            "recipient": "potential client",
            "tone": "friendly",
            "key_points": "- Remind them of our meeting\n- Ask about timeline\n- Offer to answer questions"
        },
        prerequisites=["Anthropic API key"]
    ),

    # ============================================
    # Data Processing Templates
    # ============================================
    PipelineTemplate(
        id="data-extractor",
        name="Document Data Extractor",
        description="Extract structured data from unstructured documents",
        category="data",
        tags=["extraction", "data", "structured"],
        difficulty="intermediate",
        estimated_time="5 minutes",
        use_case="Extracting specific information from documents, emails, or reports",
        pipeline={
            "name": "Data Extractor",
            "description": "Extract structured data from text",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "extract",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Extract the following information from this document:\n\n{{document}}\n\nFields to extract:\n{{fields}}\n\nReturn as JSON with these exact field names. If a field is not found, use null.",
                        "model": "claude-3-5-sonnet-latest"
                    }
                },
                {
                    "id": "parse",
                    "component_type": "json_transform",
                    "depends_on": ["extract"],
                    "config": {
                        "expression": "$.content | parse_json"
                    }
                },
                {
                    "id": "validate",
                    "component_type": "schema_validate",
                    "depends_on": ["parse"],
                    "config": {
                        "schema": "{{validation_schema}}"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "document": {"type": "string"},
                    "fields": {"type": "string"},
                    "validation_schema": {"type": "object"}
                },
                "required": ["document", "fields"]
            }
        },
        sample_input={
            "document": "Invoice #12345\nDate: 2024-01-15\nCustomer: Acme Corp\nTotal: $1,234.56\nDue Date: 2024-02-15",
            "fields": "invoice_number, date, customer_name, total_amount, due_date",
            "validation_schema": {
                "type": "object",
                "properties": {
                    "invoice_number": {"type": "string"},
                    "total_amount": {"type": "number"}
                }
            }
        },
        prerequisites=["Anthropic API key"]
    ),

    PipelineTemplate(
        id="csv-transformer",
        name="CSV Data Transformer",
        description="Transform and enrich CSV data with AI",
        category="data",
        tags=["csv", "transformation", "enrichment"],
        difficulty="intermediate",
        estimated_time="10 minutes",
        use_case="Processing CSV files, adding computed fields, or enriching data",
        pipeline={
            "name": "CSV Transformer",
            "description": "Load, transform, and enrich CSV data",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "load",
                    "component_type": "variable_set",
                    "config": {
                        "values": {
                            "data": "{{csv_data}}"
                        }
                    }
                },
                {
                    "id": "transform",
                    "component_type": "foreach",
                    "depends_on": ["load"],
                    "config": {
                        "items": "{{stages.load.output.data}}",
                        "stage": "enrich-row"
                    }
                },
                {
                    "id": "enrich-row",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Given this data row:\n{{item}}\n\nPerform: {{transformation}}\n\nReturn only the result as JSON.",
                        "model": "claude-3-haiku-20240307"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "csv_data": {"type": "array"},
                    "transformation": {"type": "string"}
                },
                "required": ["csv_data", "transformation"]
            }
        },
        sample_input={
            "csv_data": [
                {"name": "Apple Inc", "ticker": "AAPL"},
                {"name": "Microsoft", "ticker": "MSFT"}
            ],
            "transformation": "Add a 'sector' field based on the company name"
        },
        prerequisites=["Anthropic API key"]
    ),

    # ============================================
    # Analysis Templates
    # ============================================
    PipelineTemplate(
        id="sentiment-analyzer",
        name="Sentiment Analyzer",
        description="Analyze sentiment of text with detailed breakdown",
        category="analysis",
        tags=["sentiment", "nlp", "analysis"],
        difficulty="beginner",
        estimated_time="3 minutes",
        use_case="Analyzing customer feedback, reviews, or social media posts",
        pipeline={
            "name": "Sentiment Analyzer",
            "description": "Analyze sentiment with detailed scores",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "analyze",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Analyze the sentiment of this text:\n\n{{text}}\n\nProvide:\n1. Overall sentiment (positive/negative/neutral)\n2. Sentiment score (-1 to 1)\n3. Key phrases indicating sentiment\n4. Confidence level\n\nReturn as JSON.",
                        "model": "claude-3-5-sonnet-latest"
                    }
                },
                {
                    "id": "parse",
                    "component_type": "json_transform",
                    "depends_on": ["analyze"],
                    "config": {
                        "expression": "$.content | parse_json"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        },
        sample_input={
            "text": "I absolutely love this product! It exceeded all my expectations and the customer service was fantastic. Would definitely recommend to everyone."
        },
        prerequisites=["Anthropic API key"]
    ),

    PipelineTemplate(
        id="text-summarizer",
        name="Smart Text Summarizer",
        description="Summarize long documents while preserving key information",
        category="analysis",
        tags=["summary", "document", "nlp"],
        difficulty="beginner",
        estimated_time="3 minutes",
        use_case="Summarizing articles, documents, or meeting notes",
        pipeline={
            "name": "Text Summarizer",
            "description": "Create concise summaries of long text",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "summarize",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Summarize the following text in {{length}} format:\n\n{{text}}\n\nProvide:\n- Key points\n- Main conclusions\n- Action items (if any)",
                        "model": "claude-3-5-sonnet-latest"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "length": {"type": "string", "enum": ["brief (1-2 sentences)", "short (1 paragraph)", "detailed (multiple paragraphs)"], "default": "short (1 paragraph)"}
                },
                "required": ["text"]
            }
        },
        sample_input={
            "text": "Long document text here...",
            "length": "short (1 paragraph)"
        },
        prerequisites=["Anthropic API key"]
    ),

    # ============================================
    # Automation Templates
    # ============================================
    PipelineTemplate(
        id="api-chain",
        name="API Data Chain",
        description="Chain multiple API calls with data transformation",
        category="automation",
        tags=["api", "http", "integration"],
        difficulty="intermediate",
        estimated_time="10 minutes",
        use_case="Integrating multiple APIs in a single workflow",
        pipeline={
            "name": "API Chain",
            "description": "Fetch and process data from multiple APIs",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "fetch-primary",
                    "component_type": "http_request",
                    "config": {
                        "url": "{{primary_api_url}}",
                        "method": "GET",
                        "headers": {"Authorization": "Bearer {{api_key}}"}
                    }
                },
                {
                    "id": "transform",
                    "component_type": "json_transform",
                    "depends_on": ["fetch-primary"],
                    "config": {
                        "expression": "{{transform_expression}}"
                    }
                },
                {
                    "id": "fetch-secondary",
                    "component_type": "http_request",
                    "depends_on": ["transform"],
                    "config": {
                        "url": "{{secondary_api_url}}",
                        "method": "POST",
                        "body": "{{stages.transform.output}}"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "primary_api_url": {"type": "string"},
                    "secondary_api_url": {"type": "string"},
                    "api_key": {"type": "string"},
                    "transform_expression": {"type": "string"}
                },
                "required": ["primary_api_url"]
            }
        },
        sample_input={
            "primary_api_url": "https://api.example.com/data",
            "transform_expression": "$.data | select(.active == true)"
        },
        prerequisites=[]
    ),

    PipelineTemplate(
        id="webhook-processor",
        name="Webhook Processor",
        description="Process incoming webhook data with AI",
        category="automation",
        tags=["webhook", "automation", "event-driven"],
        difficulty="intermediate",
        estimated_time="10 minutes",
        use_case="Processing webhooks from external services",
        pipeline={
            "name": "Webhook Processor",
            "description": "Process webhook payloads with AI analysis",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "validate",
                    "component_type": "schema_validate",
                    "config": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "event_type": {"type": "string"},
                                "payload": {"type": "object"}
                            },
                            "required": ["event_type"]
                        }
                    }
                },
                {
                    "id": "route",
                    "component_type": "router",
                    "depends_on": ["validate"],
                    "config": {
                        "routes": [
                            {"condition": "$.event_type == 'order'", "next_stage": "process-order"},
                            {"condition": "$.event_type == 'support'", "next_stage": "process-support"},
                            {"default": True, "next_stage": "log-unknown"}
                        ]
                    }
                },
                {
                    "id": "process-order",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Process this order event:\n{{payload}}\n\nExtract: order_id, customer, items, total"
                    }
                },
                {
                    "id": "process-support",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Analyze this support ticket:\n{{payload}}\n\nProvide: urgency, category, suggested_response"
                    }
                },
                {
                    "id": "log-unknown",
                    "component_type": "logger",
                    "config": {
                        "level": "warning",
                        "message": "Unknown event type: {{event_type}}"
                    }
                }
            ]
        },
        sample_input={
            "event_type": "order",
            "payload": {"order_id": "12345", "items": [{"name": "Widget", "qty": 2}]}
        },
        prerequisites=["Anthropic API key"]
    ),

    # ============================================
    # Code Templates
    # ============================================
    PipelineTemplate(
        id="code-reviewer",
        name="AI Code Reviewer",
        description="Review code for bugs, security issues, and best practices",
        category="development",
        tags=["code", "review", "security"],
        difficulty="intermediate",
        estimated_time="5 minutes",
        use_case="Automated code review for PRs or code audits",
        pipeline={
            "name": "Code Reviewer",
            "description": "Comprehensive AI code review",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "analyze",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Review this {{language}} code:\n\n```{{language}}\n{{code}}\n```\n\nProvide a detailed review covering:\n1. Bugs or logical errors\n2. Security vulnerabilities\n3. Performance issues\n4. Code style and best practices\n5. Suggestions for improvement\n\nFor each issue, indicate severity (critical/warning/info).",
                        "model": "claude-3-5-sonnet-latest"
                    }
                },
                {
                    "id": "summarize",
                    "component_type": "generator",
                    "depends_on": ["analyze"],
                    "config": {
                        "prompt": "Based on this code review:\n\n{{stages.analyze.output.content}}\n\nProvide:\n1. Overall code quality score (1-10)\n2. Critical issues count\n3. Top 3 priority fixes\n4. One-paragraph summary"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "default": "python"}
                },
                "required": ["code"]
            }
        },
        sample_input={
            "code": "def calculate_total(items):\n    total = 0\n    for item in items:\n        total = total + item['price'] * item['quantity']\n    return total",
            "language": "python"
        },
        prerequisites=["Anthropic API key"]
    ),

    PipelineTemplate(
        id="code-explainer",
        name="Code Explainer",
        description="Explain code in plain English for learning",
        category="development",
        tags=["code", "education", "documentation"],
        difficulty="beginner",
        estimated_time="3 minutes",
        use_case="Understanding unfamiliar code or creating documentation",
        pipeline={
            "name": "Code Explainer",
            "description": "Explain code step by step",
            "version": "1.0.0",
            "stages": [
                {
                    "id": "explain",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Explain this {{language}} code to someone with {{experience_level}} experience:\n\n```{{language}}\n{{code}}\n```\n\nProvide:\n1. Overall purpose\n2. Step-by-step explanation\n3. Key concepts used\n4. Example usage",
                        "model": "claude-3-5-sonnet-latest"
                    }
                }
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "default": "python"},
                    "experience_level": {"type": "string", "enum": ["beginner", "intermediate", "expert"], "default": "intermediate"}
                },
                "required": ["code"]
            }
        },
        sample_input={
            "code": "async def fetch_data(url):\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as response:\n            return await response.json()",
            "language": "python",
            "experience_level": "beginner"
        },
        prerequisites=["Anthropic API key"]
    ),
]


class TemplateGallery:
    """Service for accessing pipeline templates."""

    _templates: Dict[str, PipelineTemplate]

    def __init__(self) -> None:
        self._templates = {t.id: t for t in TEMPLATES}

    def list_templates(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[PipelineTemplate]:
        """List templates with optional filtering."""
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]

        if search:
            search_lower = search.lower()
            templates = [
                t for t in templates
                if search_lower in t.name.lower()
                or search_lower in t.description.lower()
                or any(search_lower in tag for tag in t.tags)
            ]

        return templates

    def get_template(self, template_id: str) -> Optional[PipelineTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_categories(self) -> List[str]:
        """List all template categories."""
        categories = set(t.category for t in self._templates.values())
        return sorted(categories)

    def list_tags(self) -> List[str]:
        """List all template tags."""
        tags = set()
        for t in self._templates.values():
            tags.update(t.tags)
        return sorted(tags)


# Global instance
_gallery: Optional[TemplateGallery] = None


def get_template_gallery() -> TemplateGallery:
    """Get the global template gallery instance."""
    global _gallery
    if _gallery is None:
        _gallery = TemplateGallery()
    return _gallery
