"""
Code Generation Models.

Models for generating standalone code from pipelines.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TargetLanguage(str, Enum):
    """Supported target languages for code generation."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    NODEJS = "nodejs"
    GO = "go"
    APEX = "apex"  # Salesforce Apex


class TargetPlatform(str, Enum):
    """Supported deployment platforms."""

    STANDALONE = "standalone"  # Regular executable
    AWS_LAMBDA = "aws_lambda"
    CLOUDFLARE_WORKERS = "cloudflare_workers"
    AZURE_FUNCTIONS = "azure_functions"
    GCP_FUNCTIONS = "gcp_functions"
    FIREBASE_FUNCTIONS = "firebase_functions"
    DOCKER = "docker"
    SALESFORCE = "salesforce"  # Salesforce Platform


class OutputFormat(str, Enum):
    """Code output format."""

    SINGLE_FILE = "single_file"  # All code in one file
    PACKAGE = "package"  # Proper package structure
    ZIP = "zip"  # Downloadable archive


class CodeGenOptions(BaseModel):
    """Options for code generation."""

    # Target
    language: TargetLanguage = Field(default=TargetLanguage.PYTHON)
    platform: TargetPlatform = Field(default=TargetPlatform.STANDALONE)
    output_format: OutputFormat = Field(default=OutputFormat.PACKAGE)

    # Code style
    include_comments: bool = Field(default=True, description="Include explanatory comments")
    include_type_hints: bool = Field(default=True, description="Include type annotations")
    include_docstrings: bool = Field(default=True, description="Include docstrings")
    async_mode: bool = Field(default=True, description="Generate async code")

    # Runtime options
    inline_prompts: bool = Field(
        default=False,
        description="Inline prompt templates instead of loading from files"
    )
    include_retry_logic: bool = Field(default=True, description="Include retry logic")
    include_logging: bool = Field(default=True, description="Include logging")
    include_metrics: bool = Field(default=False, description="Include metrics collection")

    # Secrets handling
    secrets_from_env: bool = Field(
        default=True,
        description="Load secrets from environment variables"
    )
    secrets_prefix: str = Field(
        default="FLOWMASON_",
        description="Prefix for environment variable names"
    )

    # Dependencies
    minimal_dependencies: bool = Field(
        default=False,
        description="Use minimal dependencies (no flowmason runtime)"
    )
    pin_versions: bool = Field(default=True, description="Pin dependency versions")


class GeneratedFile(BaseModel):
    """A generated code file."""

    path: str = Field(description="Relative file path")
    content: str = Field(description="File content")
    is_binary: bool = Field(default=False)
    executable: bool = Field(default=False)
    description: str = Field(default="", description="What this file does")


class CodeGenResult(BaseModel):
    """Result of code generation."""

    id: str = Field(description="Generation ID")
    pipeline_id: str = Field(description="Source pipeline ID")
    pipeline_name: str = Field(description="Pipeline name")

    # Options used
    options: CodeGenOptions

    # Generated files
    files: List[GeneratedFile] = Field(default_factory=list)
    entry_point: str = Field(description="Main entry point file")

    # Metadata
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    generator_version: str = Field(default="1.0.0")

    # Stats
    total_lines: int = Field(default=0)
    total_files: int = Field(default=0)

    # Deployment info (for serverless)
    deployment_config: Optional[Dict[str, Any]] = Field(default=None)
    deploy_instructions: Optional[str] = Field(default=None)


class StageCodeTemplate(BaseModel):
    """Template for generating stage code."""

    component_type: str
    imports: List[str] = Field(default_factory=list)
    class_template: Optional[str] = None
    function_template: str
    async_function_template: Optional[str] = None


# API Request/Response Models


class GenerateCodeRequest(BaseModel):
    """Request to generate code from a pipeline."""

    pipeline_id: str
    options: CodeGenOptions = Field(default_factory=CodeGenOptions)
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional output directory (for CLI usage)"
    )


class GenerateCodeResponse(BaseModel):
    """Response with generated code."""

    result: CodeGenResult
    download_url: Optional[str] = Field(
        default=None,
        description="URL to download as ZIP"
    )


class PreviewCodeRequest(BaseModel):
    """Request to preview generated code without saving."""

    pipeline_id: str
    options: CodeGenOptions = Field(default_factory=CodeGenOptions)
    file_path: Optional[str] = Field(
        default=None,
        description="Specific file to preview"
    )


class PreviewCodeResponse(BaseModel):
    """Response with code preview."""

    files: List[GeneratedFile]
    entry_point: str
    estimated_lines: int


class ListTemplatesResponse(BaseModel):
    """Response listing available templates."""

    templates: Dict[str, StageCodeTemplate]
    languages: List[str]
    platforms: List[str]
