# FlowMason Component Development Guide

A comprehensive guide for building custom nodes and operators in FlowMason using VSCode.

---

## Table of Contents

1. [Overview](#overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Understanding Components](#understanding-components)
4. [Quick Start: Clone & Edit](#quick-start-clone--edit)
5. [Building a Node from Scratch](#building-a-node-from-scratch)
6. [Building an Operator from Scratch](#building-an-operator-from-scratch)
7. [Input/Output Models](#inputoutput-models)
8. [The Execute Method](#the-execute-method)
9. [Working with Context](#working-with-context)
10. [Testing Your Component](#testing-your-component)
11. [Packaging & Deployment](#packaging--deployment)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)
14. [Reference: Complete Examples](#reference-complete-examples)

---

## Overview

FlowMason components are self-contained, reusable building blocks for AI pipelines. There are two types:

| Type | Purpose | LLM Required | Examples |
|------|---------|--------------|----------|
| **Node** | AI-powered processing | Yes | Generator, Critic, Selector, Improver |
| **Operator** | Data transformation & utilities | No | HTTP Request, JSON Transform, Filter, Logger |

### Key Principles

1. **Zero Hardcoded Components** - All components are loaded dynamically from packages
2. **Pydantic Validation** - Type-safe inputs and outputs with automatic validation
3. **Async Execution** - All components run asynchronously for performance
4. **Universal Executor** - Same execution path for all component types

---

## Development Environment Setup

### Prerequisites

- Python 3.11+
- VSCode with Python extension
- Git

### Project Structure

```
flowmason/
├── core/flowmason_core/       # Core framework (don't modify)
│   ├── core/
│   │   ├── types.py           # Base classes (NodeInput, OperatorInput, etc.)
│   │   └── decorators.py      # @node and @operator decorators
│   ├── registry/              # Component registry
│   └── execution/             # Execution engine
├── lab/flowmason_lab/         # Component library (add your components here)
│   ├── nodes/
│   │   └── core/              # Core nodes
│   │       ├── generator.py
│   │       ├── critic.py
│   │       └── ...
│   └── operators/
│       └── core/              # Core operators
│           ├── http_request.py
│           ├── json_transform.py
│           └── ...
├── dist/packages/             # Built .fmpkg files
├── scripts/
│   └── package_builder.py     # Build tool
└── tests/                     # Test files
```

### VSCode Setup

1. **Open the project:**
   ```bash
   cd /path/to/flowmason
   code .
   ```

2. **Create/activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ./core
   pip install -e ./lab
   pip install -e ./studio
   pip install pytest pytest-asyncio httpx
   ```

4. **Configure VSCode settings** (`.vscode/settings.json`):
   ```json
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
     "python.analysis.extraPaths": [
       "${workspaceFolder}/core",
       "${workspaceFolder}/lab",
       "${workspaceFolder}/studio"
     ],
     "python.envFile": "${workspaceFolder}/.env",
     "python.testing.pytestEnabled": true,
     "python.testing.pytestArgs": ["tests"]
   }
   ```

5. **Set PYTHONPATH** (`.env` file):
   ```
   PYTHONPATH=core:lab:studio
   ```

6. **VSCode launch configuration** (`.vscode/launch.json`):
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Test Component",
         "type": "debugpy",
         "request": "launch",
         "module": "pytest",
         "args": ["tests/test_my_component.py", "-v", "-s"],
         "env": {
           "PYTHONPATH": "${workspaceFolder}/core:${workspaceFolder}/lab:${workspaceFolder}/studio"
         }
       },
       {
         "name": "Python: Run Studio Backend",
         "type": "debugpy",
         "request": "launch",
         "module": "uvicorn",
         "args": ["flowmason_studio.api.app:app", "--host", "127.0.0.1", "--port", "8999", "--reload"],
         "env": {
           "PYTHONPATH": "${workspaceFolder}/core:${workspaceFolder}/lab:${workspaceFolder}/studio"
         }
       }
     ]
   }
   ```

---

## Understanding Components

### Anatomy of a Component

Every component has these parts:

```python
from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node

@node(                          # 1. DECORATOR with metadata
    name="my_component",
    category="custom",
    description="What it does",
    ...
)
class MyComponent:
    class Input(NodeInput):     # 2. INPUT MODEL (Pydantic)
        field: str = Field(...)

    class Output(NodeOutput):   # 3. OUTPUT MODEL (Pydantic)
        result: str = Field(...)

    class Config:               # 4. CONFIG (optional)
        timeout_seconds = 60

    async def execute(          # 5. EXECUTE METHOD (async)
        self,
        input: Input,
        context
    ) -> Output:
        # Your logic here
        return self.Output(result="...")
```

### Node vs Operator

| Aspect | Node | Operator |
|--------|------|----------|
| Decorator | `@node()` | `@operator()` |
| Base Classes | `NodeInput`, `NodeOutput` | `OperatorInput`, `OperatorOutput` |
| LLM Access | Yes (`context.llm`) | No |
| Deterministic | No (AI varies) | Yes (same input = same output) |
| Use Case | Text generation, analysis, decisions | Data transform, API calls, validation |
| Icon Color (convention) | Purple/Pink tones | Blue/Green tones |

---

## Quick Start: Clone & Edit

The fastest way to create a component is to clone an existing one.

### Option 1: Clone a Node

1. **Copy an existing node:**
   ```bash
   cp lab/flowmason_lab/nodes/core/generator.py \
      lab/flowmason_lab/nodes/core/my_custom_node.py
   ```

2. **Edit the file in VSCode:**

   ```python
   # lab/flowmason_lab/nodes/core/my_custom_node.py

   from typing import Optional, List
   from flowmason_core.core.types import NodeInput, NodeOutput, Field
   from flowmason_core.core.decorators import node

   @node(
       name="my_custom_node",          # CHANGE: unique name (snake_case)
       category="custom",               # CHANGE: your category
       description="My custom AI node", # CHANGE: describe what it does
       icon="brain",                    # CHANGE: Lucide icon name
       color="#10B981",                 # CHANGE: hex color for UI
       version="1.0.0",
       author="Your Name",
       tags=["custom", "ai"],
       recommended_providers={
           "anthropic": {
               "model": "claude-3-5-sonnet-20241022",
               "temperature": 0.7,
               "max_tokens": 4096,
           },
       },
       default_provider="anthropic",
   )
   class MyCustomNode:
       """Your custom AI-powered node."""

       class Input(NodeInput):
           """Define your inputs here."""
           prompt: str = Field(
               description="The main prompt for the AI",
               examples=["Analyze this text..."]
           )
           context_data: Optional[str] = Field(
               default=None,
               description="Additional context"
           )
           max_tokens: int = Field(
               default=2048,
               ge=1,
               le=128000,
               description="Maximum response length"
           )

       class Output(NodeOutput):
           """Define your outputs here."""
           content: str = Field(description="Generated content")
           tokens_used: int = Field(default=0)
           confidence: float = Field(default=1.0, ge=0.0, le=1.0)

       class Config:
           deterministic = False
           timeout_seconds = 120

       async def execute(self, input: Input, context) -> Output:
           """Your execution logic."""
           llm = getattr(context, "llm", None)

           if not llm:
               # Fallback when no LLM configured
               return self.Output(
                   content=f"[Mock response for: {input.prompt[:50]}...]",
                   tokens_used=0,
                   confidence=0.0
               )

           # Build the full prompt
           full_prompt = input.prompt
           if input.context_data:
               full_prompt = f"Context:\n{input.context_data}\n\n{input.prompt}"

           # Call the LLM
           response = await llm.generate_async(
               prompt=full_prompt,
               max_tokens=input.max_tokens,
           )

           return self.Output(
               content=response.content,
               tokens_used=response.total_tokens,
               confidence=1.0
           )
   ```

### Option 2: Clone an Operator

1. **Copy an existing operator:**
   ```bash
   cp lab/flowmason_lab/operators/core/json_transform.py \
      lab/flowmason_lab/operators/core/my_custom_operator.py
   ```

2. **Edit the file:**

   ```python
   # lab/flowmason_lab/operators/core/my_custom_operator.py

   from typing import Any, Dict, Optional
   from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
   from flowmason_core.core.decorators import operator

   @operator(
       name="my_custom_operator",        # CHANGE: unique name
       category="custom",
       description="My custom data transformer",
       icon="settings",                  # Lucide icon
       color="#3B82F6",                  # Blue for operators
       version="1.0.0",
       author="Your Name",
       tags=["custom", "transform"],
   )
   class MyCustomOperator:
       """Your custom data transformation operator."""

       class Input(OperatorInput):
           data: Any = Field(description="Input data to transform")
           uppercase: bool = Field(default=False, description="Convert to uppercase")
           prefix: Optional[str] = Field(default=None, description="Add prefix")

       class Output(OperatorOutput):
           result: Any = Field(description="Transformed data")
           original_type: str = Field(description="Type of original data")

       class Config:
           deterministic = True
           timeout_seconds = 30

       async def execute(self, input: Input, context) -> Output:
           """Transform the data."""
           result = input.data

           # Apply transformations
           if isinstance(result, str):
               if input.uppercase:
                   result = result.upper()
               if input.prefix:
                   result = f"{input.prefix}{result}"

           return self.Output(
               result=result,
               original_type=type(input.data).__name__
           )
   ```

---

## Building a Node from Scratch

### Step 1: Create the File

Create a new file in the appropriate location:

```bash
# For a core node
touch lab/flowmason_lab/nodes/core/sentiment_analyzer.py

# For a custom category
mkdir -p lab/flowmason_lab/nodes/custom
touch lab/flowmason_lab/nodes/custom/sentiment_analyzer.py
```

### Step 2: Write the Component

```python
"""
Sentiment Analyzer Node

Analyzes text sentiment using an LLM and returns structured results.
"""

from typing import Optional, List, Literal
from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="sentiment_analyzer",
    category="analysis",
    description="Analyze sentiment of text content using AI",
    icon="heart",
    color="#EC4899",  # Pink
    version="1.0.0",
    author="Your Name",
    tags=["sentiment", "analysis", "nlp", "ai"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.3,  # Lower for consistent analysis
            "max_tokens": 1024,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.3,
        },
    },
    default_provider="anthropic",
)
class SentimentAnalyzerNode:
    """
    Analyzes the sentiment of input text.

    Returns a sentiment classification (positive/negative/neutral/mixed)
    along with a confidence score and detailed breakdown.
    """

    class Input(NodeInput):
        """Input configuration for sentiment analysis."""

        text: str = Field(
            description="The text to analyze for sentiment",
            min_length=1,
            max_length=50000,
            examples=[
                "I absolutely love this product! It exceeded all my expectations.",
                "The service was terrible and I'm very disappointed.",
            ]
        )

        include_emotions: bool = Field(
            default=True,
            description="Whether to include detailed emotion breakdown"
        )

        language: str = Field(
            default="auto",
            description="Language of the text (auto-detect if 'auto')",
            examples=["auto", "en", "es", "fr"]
        )

        context: Optional[str] = Field(
            default=None,
            description="Optional context about the text source (e.g., 'product review', 'tweet')"
        )

    class Output(NodeOutput):
        """Output from sentiment analysis."""

        sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(
            description="Overall sentiment classification"
        )

        confidence: float = Field(
            ge=0.0,
            le=1.0,
            description="Confidence score (0-1)"
        )

        score: float = Field(
            ge=-1.0,
            le=1.0,
            description="Sentiment score (-1 very negative to +1 very positive)"
        )

        emotions: Optional[dict] = Field(
            default=None,
            description="Detailed emotion breakdown if requested"
        )

        summary: str = Field(
            description="Brief explanation of the sentiment analysis"
        )

        tokens_used: int = Field(default=0)

    class Config:
        deterministic = False
        timeout_seconds = 60
        supports_streaming = False

    async def execute(self, input: Input, context) -> Output:
        """Execute sentiment analysis."""
        llm = getattr(context, "llm", None)

        if not llm:
            # Return mock data when no LLM is configured
            return self.Output(
                sentiment="neutral",
                confidence=0.0,
                score=0.0,
                emotions={"joy": 0.5, "sadness": 0.5} if input.include_emotions else None,
                summary="[Mock analysis - no LLM configured]",
                tokens_used=0
            )

        # Build the analysis prompt
        emotion_instruction = ""
        if input.include_emotions:
            emotion_instruction = """
Also provide an "emotions" object with scores (0-1) for these emotions:
- joy, sadness, anger, fear, surprise, disgust, trust, anticipation
"""

        context_note = ""
        if input.context:
            context_note = f"\nContext: This text is from a {input.context}."

        prompt = f"""Analyze the sentiment of the following text and respond in JSON format.
{context_note}

Text to analyze:
\"\"\"
{input.text}
\"\"\"

Respond with a JSON object containing:
- "sentiment": one of "positive", "negative", "neutral", or "mixed"
- "confidence": a number from 0 to 1 indicating how confident you are
- "score": a number from -1 (very negative) to +1 (very positive)
- "summary": a brief 1-2 sentence explanation
{emotion_instruction}

Respond ONLY with valid JSON, no other text."""

        system_prompt = """You are a sentiment analysis expert. Analyze text objectively and provide accurate sentiment classifications. Always respond with valid JSON only."""

        response = await llm.generate_async(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1024,
        )

        # Parse the JSON response
        import json
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback
                result = {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "score": 0.0,
                    "summary": response.content[:200]
                }

        return self.Output(
            sentiment=result.get("sentiment", "neutral"),
            confidence=result.get("confidence", 0.5),
            score=result.get("score", 0.0),
            emotions=result.get("emotions") if input.include_emotions else None,
            summary=result.get("summary", "Analysis complete"),
            tokens_used=response.total_tokens
        )
```

### Step 3: Test It

See [Testing Your Component](#testing-your-component) section below.

---

## Building an Operator from Scratch

### Step 1: Create the File

```bash
touch lab/flowmason_lab/operators/core/csv_parser.py
```

### Step 2: Write the Component

```python
"""
CSV Parser Operator

Parses CSV data into structured records.
"""

from typing import Any, Dict, List, Optional, Literal
import csv
import io
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="csv_parser",
    category="data",
    description="Parse CSV data into structured records",
    icon="table",
    color="#059669",  # Green
    version="1.0.0",
    author="Your Name",
    tags=["csv", "parser", "data", "transform"],
)
class CsvParserOperator:
    """
    Parses CSV text data into a list of dictionaries.

    Supports various CSV dialects, custom delimiters, and header handling.
    """

    class Input(OperatorInput):
        """Input configuration for CSV parsing."""

        data: str = Field(
            description="CSV data as a string",
            min_length=1,
            examples=[
                "name,age,city\nAlice,30,NYC\nBob,25,LA",
                "id;product;price\n1;Widget;9.99\n2;Gadget;19.99"
            ]
        )

        delimiter: str = Field(
            default=",",
            description="Field delimiter character",
            max_length=1,
            examples=[",", ";", "\t", "|"]
        )

        has_header: bool = Field(
            default=True,
            description="Whether the first row contains column headers"
        )

        skip_rows: int = Field(
            default=0,
            ge=0,
            description="Number of rows to skip at the beginning"
        )

        max_rows: Optional[int] = Field(
            default=None,
            ge=1,
            description="Maximum number of data rows to parse (None for all)"
        )

        column_names: Optional[List[str]] = Field(
            default=None,
            description="Custom column names (overrides header row)"
        )

        strip_whitespace: bool = Field(
            default=True,
            description="Strip whitespace from values"
        )

    class Output(OperatorOutput):
        """Output from CSV parsing."""

        records: List[Dict[str, Any]] = Field(
            description="Parsed records as list of dictionaries"
        )

        columns: List[str] = Field(
            description="Column names in order"
        )

        row_count: int = Field(
            description="Number of data rows parsed"
        )

        success: bool = Field(
            default=True,
            description="Whether parsing was successful"
        )

        errors: List[str] = Field(
            default_factory=list,
            description="Any parsing errors encountered"
        )

    class Config:
        deterministic = True
        timeout_seconds = 30

    async def execute(self, input: Input, context) -> Output:
        """Parse the CSV data."""
        errors = []
        records = []
        columns = []

        try:
            # Create a file-like object from the string
            csv_file = io.StringIO(input.data)

            # Skip rows if requested
            for _ in range(input.skip_rows):
                next(csv_file, None)

            # Create CSV reader
            reader = csv.reader(csv_file, delimiter=input.delimiter)

            # Handle headers
            if input.column_names:
                columns = input.column_names
                if input.has_header:
                    next(reader, None)  # Skip the header row
            elif input.has_header:
                header_row = next(reader, None)
                if header_row:
                    columns = [
                        col.strip() if input.strip_whitespace else col
                        for col in header_row
                    ]
                else:
                    errors.append("No header row found")
                    return self.Output(
                        records=[],
                        columns=[],
                        row_count=0,
                        success=False,
                        errors=errors
                    )
            else:
                # No headers - will use indices
                columns = []

            # Parse data rows
            row_num = 0
            for row in reader:
                if input.max_rows and row_num >= input.max_rows:
                    break

                # Strip whitespace if requested
                if input.strip_whitespace:
                    row = [val.strip() for val in row]

                # Create record
                if columns:
                    if len(row) != len(columns):
                        errors.append(
                            f"Row {row_num + 1}: expected {len(columns)} columns, got {len(row)}"
                        )
                        # Pad or truncate
                        while len(row) < len(columns):
                            row.append("")
                        row = row[:len(columns)]

                    record = dict(zip(columns, row))
                else:
                    # No headers - use column indices
                    if row_num == 0:
                        columns = [f"col_{i}" for i in range(len(row))]
                    record = dict(zip(columns, row))

                records.append(record)
                row_num += 1

            return self.Output(
                records=records,
                columns=columns,
                row_count=len(records),
                success=len(errors) == 0,
                errors=errors
            )

        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return self.Output(
                records=records,
                columns=columns,
                row_count=len(records),
                success=False,
                errors=errors
            )
```

---

## Input/Output Models

### Field Definition Reference

```python
from flowmason_core.core.types import Field
from typing import Optional, List, Dict, Any, Literal

class Input(NodeInput):
    # Required field
    required_field: str = Field(
        description="This field is required"
    )

    # Optional field with default
    optional_field: Optional[str] = Field(
        default=None,
        description="This field is optional"
    )

    # Field with default value
    with_default: int = Field(
        default=100,
        description="Has a default value"
    )

    # Numeric constraints
    bounded_int: int = Field(
        default=50,
        ge=0,          # >= 0
        le=100,        # <= 100
        description="Must be between 0 and 100"
    )

    bounded_float: float = Field(
        default=0.7,
        gt=0.0,        # > 0
        lt=1.0,        # < 1
        description="Must be between 0 and 1 (exclusive)"
    )

    # String constraints
    short_string: str = Field(
        default="",
        min_length=1,
        max_length=100,
        description="Length-constrained string"
    )

    # Regex pattern
    email: str = Field(
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',
        description="Must be valid email format"
    )

    # Enum/Literal for fixed choices
    mode: Literal["fast", "balanced", "thorough"] = Field(
        default="balanced",
        description="Processing mode"
    )

    # List with constraints
    tags: List[str] = Field(
        default_factory=list,
        max_length=10,  # Max 10 items
        description="Up to 10 tags"
    )

    # Dict/Any for flexible data
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata"
    )

    # With examples (shown in UI)
    prompt: str = Field(
        description="Your prompt",
        examples=[
            "Summarize this article...",
            "Translate to Spanish...",
        ]
    )
```

### Validation Behavior

| Input Type | Extra Fields | Behavior |
|------------|--------------|----------|
| `NodeInput` | Forbidden | Raises error if unknown fields passed |
| `OperatorInput` | Forbidden | Raises error if unknown fields passed |
| `NodeOutput` | Allowed | Extra fields preserved in output |
| `OperatorOutput` | Allowed | Extra fields preserved in output |

### Custom Validators

```python
from pydantic import field_validator, model_validator

class Input(NodeInput):
    start_date: str
    end_date: str

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure dates are in YYYY-MM-DD format."""
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v

    @model_validator(mode='after')
    def validate_date_range(self):
        """Ensure start_date is before end_date."""
        if self.start_date > self.end_date:
            raise ValueError('start_date must be before end_date')
        return self
```

---

## The Execute Method

### Signature

```python
async def execute(self, input: Input, context) -> Output:
    """
    Execute the component logic.

    Args:
        input: Validated Input instance with all fields populated
        context: ExecutionContext with runtime information

    Returns:
        Output instance with results

    Raises:
        Any exception will be caught and recorded as component failure
    """
    pass
```

### Key Rules

1. **Must be `async`** - All components are asynchronous
2. **Must accept `(self, input, context)`** - Exact signature required
3. **Must return `Output` instance** - Use `self.Output(...)`
4. **Don't catch all exceptions** - Let errors bubble up for proper handling

### Example Patterns

**Simple transformation:**
```python
async def execute(self, input: Input, context) -> Output:
    result = input.data.upper()
    return self.Output(result=result)
```

**With LLM call (nodes only):**
```python
async def execute(self, input: Input, context) -> Output:
    llm = getattr(context, "llm", None)
    if not llm:
        return self.Output(content="[No LLM]", tokens_used=0)

    response = await llm.generate_async(
        prompt=input.prompt,
        system_prompt=input.system_prompt,
        temperature=input.temperature,
        max_tokens=input.max_tokens,
    )

    return self.Output(
        content=response.content,
        tokens_used=response.total_tokens,
    )
```

**With HTTP call (operators):**
```python
async def execute(self, input: Input, context) -> Output:
    import httpx

    async with httpx.AsyncClient(timeout=input.timeout) as client:
        response = await client.request(
            method=input.method,
            url=input.url,
            headers=input.headers,
            json=input.body,
        )

        return self.Output(
            status_code=response.status_code,
            body=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            success=response.is_success,
        )
```

**With error handling:**
```python
async def execute(self, input: Input, context) -> Output:
    try:
        result = some_operation(input.data)
        return self.Output(result=result, success=True, error=None)
    except ValueError as e:
        return self.Output(result=None, success=False, error=str(e))
    # Let other exceptions bubble up
```

---

## Working with Context

The `context` object provides runtime information and services.

### Available Attributes

```python
async def execute(self, input: Input, context) -> Output:
    # Execution identifiers
    run_id = context.run_id              # Unique run ID
    pipeline_id = context.pipeline_id    # Pipeline name
    trace_id = context.trace_id          # For observability

    # Original pipeline input
    pipeline_input = context.pipeline_input  # Dict of pipeline inputs

    # LLM access (nodes only)
    llm = getattr(context, "llm", None)
    if llm:
        response = await llm.generate_async(prompt="...")

    # Logging
    logger = getattr(context, "logger", None)
    if logger:
        logger.info("Processing started")
```

### LLM Helper Methods

When `context.llm` is available (nodes only):

```python
# Simple generation
response = await llm.generate_async(
    prompt="Your prompt here",
    system_prompt="Optional system prompt",
    temperature=0.7,
    max_tokens=4096,
)

# Response object
response.content       # str: Generated text
response.total_tokens  # int: Total tokens used
response.model         # str: Model used
response.metadata      # dict: Additional info (stop_reason, etc.)
```

---

## Testing Your Component

### Create a Test File

```bash
touch tests/test_my_component.py
```

### Write Tests

```python
# tests/test_my_component.py

import pytest
from flowmason_lab.nodes.core.sentiment_analyzer import SentimentAnalyzerNode
# or
from flowmason_lab.operators.core.csv_parser import CsvParserOperator


class MockContext:
    """Mock context for testing without real LLM."""
    def __init__(self):
        self.run_id = "test_run"
        self.pipeline_id = "test_pipeline"
        self.trace_id = "test_trace"
        self.pipeline_input = {}
        self.llm = None  # No LLM for unit tests


class MockLLM:
    """Mock LLM for testing with controlled responses."""

    def __init__(self, response_content: str):
        self.response_content = response_content

    async def generate_async(self, prompt, **kwargs):
        class MockResponse:
            def __init__(self, content):
                self.content = content
                self.total_tokens = 100
                self.model = "mock-model"
                self.metadata = {}

        return MockResponse(self.response_content)


class MockContextWithLLM(MockContext):
    """Mock context with LLM for integration-style tests."""

    def __init__(self, llm_response: str):
        super().__init__()
        self.llm = MockLLM(llm_response)


# ============ TESTS ============

class TestSentimentAnalyzerNode:
    """Tests for SentimentAnalyzerNode."""

    @pytest.mark.asyncio
    async def test_input_validation(self):
        """Test that input validation works."""
        # Valid input
        input_obj = SentimentAnalyzerNode.Input(
            text="I love this!",
            include_emotions=True
        )
        assert input_obj.text == "I love this!"
        assert input_obj.include_emotions is True

        # Invalid input - empty text
        with pytest.raises(Exception):  # Pydantic ValidationError
            SentimentAnalyzerNode.Input(text="")

    @pytest.mark.asyncio
    async def test_execute_without_llm(self):
        """Test execution without LLM returns mock data."""
        node = SentimentAnalyzerNode()
        input_obj = SentimentAnalyzerNode.Input(
            text="Test text",
            include_emotions=True
        )
        context = MockContext()

        result = await node.execute(input_obj, context)

        assert result.sentiment == "neutral"
        assert result.confidence == 0.0
        assert result.tokens_used == 0

    @pytest.mark.asyncio
    async def test_execute_with_mock_llm(self):
        """Test execution with mocked LLM response."""
        node = SentimentAnalyzerNode()
        input_obj = SentimentAnalyzerNode.Input(
            text="I absolutely love this product!",
            include_emotions=False
        )

        # Mock LLM returns JSON
        mock_response = '{"sentiment": "positive", "confidence": 0.95, "score": 0.8, "summary": "Very positive sentiment"}'
        context = MockContextWithLLM(mock_response)

        result = await node.execute(input_obj, context)

        assert result.sentiment == "positive"
        assert result.confidence == 0.95
        assert result.score == 0.8
        assert "positive" in result.summary.lower()


class TestCsvParserOperator:
    """Tests for CsvParserOperator."""

    @pytest.mark.asyncio
    async def test_basic_parsing(self):
        """Test basic CSV parsing."""
        op = CsvParserOperator()
        input_obj = CsvParserOperator.Input(
            data="name,age,city\nAlice,30,NYC\nBob,25,LA",
            delimiter=",",
            has_header=True
        )
        context = MockContext()

        result = await op.execute(input_obj, context)

        assert result.success is True
        assert result.row_count == 2
        assert result.columns == ["name", "age", "city"]
        assert result.records[0] == {"name": "Alice", "age": "30", "city": "NYC"}
        assert result.records[1] == {"name": "Bob", "age": "25", "city": "LA"}

    @pytest.mark.asyncio
    async def test_custom_delimiter(self):
        """Test parsing with semicolon delimiter."""
        op = CsvParserOperator()
        input_obj = CsvParserOperator.Input(
            data="id;product;price\n1;Widget;9.99",
            delimiter=";",
            has_header=True
        )
        context = MockContext()

        result = await op.execute(input_obj, context)

        assert result.success is True
        assert result.records[0]["product"] == "Widget"

    @pytest.mark.asyncio
    async def test_no_header(self):
        """Test parsing without header row."""
        op = CsvParserOperator()
        input_obj = CsvParserOperator.Input(
            data="Alice,30,NYC\nBob,25,LA",
            has_header=False
        )
        context = MockContext()

        result = await op.execute(input_obj, context)

        assert result.columns == ["col_0", "col_1", "col_2"]
        assert result.records[0]["col_0"] == "Alice"

    @pytest.mark.asyncio
    async def test_max_rows(self):
        """Test max_rows limit."""
        op = CsvParserOperator()
        input_obj = CsvParserOperator.Input(
            data="a\n1\n2\n3\n4\n5",
            has_header=True,
            max_rows=2
        )
        context = MockContext()

        result = await op.execute(input_obj, context)

        assert result.row_count == 2
```

### Run Tests

```bash
# Run all tests
PYTHONPATH=core:lab:studio python -m pytest tests/ -v

# Run specific test file
PYTHONPATH=core:lab:studio python -m pytest tests/test_my_component.py -v

# Run specific test
PYTHONPATH=core:lab:studio python -m pytest tests/test_my_component.py::TestCsvParserOperator::test_basic_parsing -v

# With coverage
PYTHONPATH=core:lab:studio python -m pytest tests/ --cov=lab --cov-report=term-missing
```

---

## Packaging & Deployment

### Build Your Package

```bash
# Navigate to project root
cd /path/to/flowmason

# Build a single component
PYTHONPATH=core:lab:studio python scripts/package_builder.py \
    lab/flowmason_lab/nodes/core/sentiment_analyzer.py \
    --output dist/packages \
    --version 1.0.0

# Build all components
PYTHONPATH=core:lab:studio python scripts/package_builder.py all \
    --output dist/packages
```

### Package Output

```
dist/packages/
└── sentiment_analyzer-1.0.0.fmpkg  # ZIP archive containing:
    ├── flowmason-package.json       # Manifest
    └── index.py                     # Component source
```

### Manifest Structure

The build automatically generates `flowmason-package.json`:

```json
{
  "name": "sentiment_analyzer",
  "version": "1.0.0",
  "description": "Analyze sentiment of text content using AI",
  "type": "node",
  "author": {"name": "Your Name"},
  "license": "MIT",
  "category": "analysis",
  "tags": ["sentiment", "analysis", "nlp", "ai"],
  "entry_point": "index.py",
  "requires_llm": true,
  "dependencies": [],
  "recommended_providers": {
    "anthropic": {
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.3,
      "max_tokens": 1024
    }
  },
  "default_provider": "anthropic",
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "minLength": 1, "maxLength": 50000},
      "include_emotions": {"type": "boolean", "default": true},
      "language": {"type": "string", "default": "auto"},
      "context": {"type": "string", "nullable": true}
    },
    "required": ["text"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "sentiment": {"enum": ["positive", "negative", "neutral", "mixed"]},
      "confidence": {"type": "number", "minimum": 0, "maximum": 1},
      "score": {"type": "number", "minimum": -1, "maximum": 1},
      "emotions": {"type": "object", "nullable": true},
      "summary": {"type": "string"},
      "tokens_used": {"type": "integer"}
    }
  },
  "is_core": false,
  "created_at": "2025-12-10T10:00:00Z"
}
```

### Deploy to FlowMason

1. **Copy to packages directory:**
   ```bash
   cp dist/packages/sentiment_analyzer-1.0.0.fmpkg ~/.flowmason/packages/
   ```

2. **Restart Studio** (or refresh registry in API)

3. **Component appears in Studio's Component Palette**

---

## Best Practices

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Component name | snake_case | `sentiment_analyzer` |
| Class name | PascalCase | `SentimentAnalyzerNode` |
| Field names | snake_case | `max_tokens` |
| File name | snake_case.py | `sentiment_analyzer.py` |

### Code Organization

```python
"""
Module docstring explaining the component.
"""

# 1. Standard library imports
from typing import Optional, List, Dict, Any, Literal
import json

# 2. Third-party imports (if any)
import httpx

# 3. FlowMason imports
from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node

# 4. Constants (if any)
DEFAULT_MAX_TOKENS = 4096

# 5. Component class
@node(...)
class MyNode:
    """Class docstring."""

    class Input(NodeInput):
        """Input docstring."""
        pass

    class Output(NodeOutput):
        """Output docstring."""
        pass

    class Config:
        pass

    async def execute(self, input: Input, context) -> Output:
        """Execute docstring."""
        pass
```

### Error Handling

```python
async def execute(self, input: Input, context) -> Output:
    # DO: Return error info in Output when recoverable
    if not input.data:
        return self.Output(result=None, success=False, error="No data provided")

    # DO: Let exceptions bubble up for fatal errors
    # (they'll be caught by the executor and recorded)

    # DON'T: Catch all exceptions silently
    # try:
    #     ...
    # except:
    #     pass  # BAD!
```

### Performance Tips

1. **Avoid blocking calls** - Use `async` versions of libraries (httpx, aiofiles)
2. **Set appropriate timeouts** - Don't let operations hang forever
3. **Stream large data** - Don't load huge files into memory at once
4. **Cache when possible** - Reuse connections, cache computed values

### Documentation

1. **Module docstring** - Explain what the component does
2. **Class docstring** - More detail about behavior
3. **Field descriptions** - Clear descriptions for all Input/Output fields
4. **Examples** - Provide examples for string fields

---

## Troubleshooting

### Common Errors

**"Input class must inherit from NodeInput/OperatorInput"**
```python
# Wrong
class Input:
    pass

# Correct
class Input(NodeInput):
    pass
```

**"execute method must be async"**
```python
# Wrong
def execute(self, input, context):
    pass

# Correct
async def execute(self, input, context):
    pass
```

**"Field required" validation error**
```python
# Make optional with default
field: Optional[str] = Field(default=None, ...)
# Or provide a required value
field: str = Field(description="Required field")
```

**"Extra fields not allowed"**
- Input classes reject unknown fields
- Check your input_mapping in pipeline config

**Component not appearing in Studio**
1. Check package was built successfully
2. Verify .fmpkg file is in `~/.flowmason/packages/`
3. Restart Studio backend
4. Check for import errors in component code

### Debug Tips

1. **Print statements** (temporary):
   ```python
   async def execute(self, input, context):
       print(f"DEBUG: input = {input}")
       # ...
   ```

2. **Use the Logger operator** in pipelines for runtime debugging

3. **Check Studio's debug panel** for stage inputs/outputs

4. **Run tests with verbose output**:
   ```bash
   pytest tests/test_my_component.py -v -s
   ```

---

## Reference: Complete Examples

### Existing Components to Study

| Component | Type | Location | Good Example Of |
|-----------|------|----------|-----------------|
| `generator` | Node | `lab/flowmason_lab/nodes/core/generator.py` | Basic LLM node, all decorator options |
| `critic` | Node | `lab/flowmason_lab/nodes/core/critic.py` | Structured JSON output from LLM |
| `selector` | Node | `lab/flowmason_lab/nodes/core/selector.py` | Multiple input items, ranking |
| `http_request` | Operator | `lab/flowmason_lab/operators/core/http_request.py` | External API calls, async HTTP |
| `json_transform` | Operator | `lab/flowmason_lab/operators/core/json_transform.py` | Data transformation, field mapping |
| `schema_validate` | Operator | `lab/flowmason_lab/operators/core/schema_validate.py` | JSON Schema validation |
| `filter` | Operator | `lab/flowmason_lab/operators/core/filter.py` | Conditional logic, expressions |
| `loop` | Operator | `lab/flowmason_lab/operators/core/loop.py` | Batch processing |

### Minimal Node Template

```python
from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node

@node(
    name="minimal_node",
    category="custom",
    description="Minimal node template",
    icon="box",
    color="#6B7280",
    version="1.0.0",
    author="Your Name",
    tags=["template"],
    recommended_providers={"anthropic": {"model": "claude-3-5-sonnet-20241022"}},
    default_provider="anthropic",
)
class MinimalNode:
    class Input(NodeInput):
        prompt: str = Field(description="Input prompt")

    class Output(NodeOutput):
        content: str = Field(description="Generated content")

    async def execute(self, input: Input, context) -> Output:
        llm = getattr(context, "llm", None)
        if not llm:
            return self.Output(content=f"[No LLM] {input.prompt}")

        response = await llm.generate_async(prompt=input.prompt)
        return self.Output(content=response.content)
```

### Minimal Operator Template

```python
from typing import Any
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator

@operator(
    name="minimal_operator",
    category="custom",
    description="Minimal operator template",
    icon="settings",
    color="#3B82F6",
    version="1.0.0",
    author="Your Name",
    tags=["template"],
)
class MinimalOperator:
    class Input(OperatorInput):
        data: Any = Field(description="Input data")

    class Output(OperatorOutput):
        result: Any = Field(description="Processed result")

    async def execute(self, input: Input, context) -> Output:
        return self.Output(result=input.data)
```

---

## Decorator Reference

### @node Decorator Options

```python
@node(
    # Required
    name="component_name",           # Unique identifier (snake_case)
    category="category_name",        # For grouping in UI
    description="What it does",      # One-line description

    # Recommended
    version="1.0.0",                 # Semantic version
    author="Your Name",              # Author name
    tags=["tag1", "tag2"],           # Search/filter tags
    icon="sparkles",                 # Lucide icon name
    color="#8B5CF6",                 # Hex color for UI

    # LLM Configuration (nodes only)
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
            "max_tokens": 4096,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.7,
        },
    },
    default_provider="anthropic",    # Default provider to use

    # Optional
    required_capabilities=[],        # Required model capabilities
    min_context_window=10000,        # Minimum context size needed
    require_vision=False,            # Requires vision model
    require_function_calling=False,  # Requires function calling
)
```

### @operator Decorator Options

```python
@operator(
    # Required
    name="component_name",
    category="category_name",
    description="What it does",

    # Recommended
    version="1.0.0",
    author="Your Name",
    tags=["tag1", "tag2"],
    icon="settings",
    color="#3B82F6",
)
```

### Config Class Options

```python
class Config:
    deterministic = True       # Same input always produces same output
    timeout_seconds = 60       # Max execution time
    supports_streaming = False # Can stream responses
    max_retries = 3           # Retry count on failure
```

---

## Available LLM Providers

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-3-5-sonnet-20241022 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Google | `GOOGLE_API_KEY` | gemini-1.5-pro |
| Groq | `GROQ_API_KEY` | llama-3.3-70b-versatile |

---

## Additional Resources

- [API Reference](./api-reference.md) - REST API documentation
- [Studio User Guide](./studio-user-guide.md) - Using the visual Studio
- [Package Format](./package-format.md) - Package specification details
- [Architecture Rules](./architecture-rules.md) - Design principles

---

*Last updated: December 2025*
