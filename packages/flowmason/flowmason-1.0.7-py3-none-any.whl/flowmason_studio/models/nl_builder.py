"""
Natural Language Pipeline Builder Models.

Models for AI-powered pipeline generation from natural language descriptions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenerationStatus(str, Enum):
    """Status of pipeline generation."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationMode(str, Enum):
    """Mode for pipeline generation."""

    QUICK = "quick"           # Fast generation with basic structure
    DETAILED = "detailed"     # Full generation with configs
    INTERACTIVE = "interactive"  # Step-by-step with user feedback


class ComponentSuggestion(BaseModel):
    """A suggested component for the pipeline."""

    component_type: str = Field(description="Component type identifier")
    name: str = Field(description="Human-readable name")
    purpose: str = Field(description="What this component does in the pipeline")
    rationale: str = Field(description="Why this component was chosen")
    confidence: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description="Confidence score for this suggestion"
    )
    alternatives: List[str] = Field(
        default_factory=list,
        description="Alternative components that could work"
    )


class StageDefinition(BaseModel):
    """A generated stage definition."""

    id: str
    name: str
    component_type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    description: Optional[str] = None

    # Generation metadata
    generated_from: Optional[str] = Field(
        default=None,
        description="Part of the description this stage addresses"
    )


class GeneratedPipeline(BaseModel):
    """A complete generated pipeline."""

    name: str
    description: str
    version: str = "1.0.0"
    stages: List[StageDefinition]
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

    # Metadata
    generation_id: str
    generated_at: str
    original_request: str
    model_used: Optional[str] = None


class GenerationAnalysis(BaseModel):
    """Analysis of the natural language request."""

    intent: str = Field(description="Primary intent identified")
    entities: List[str] = Field(
        default_factory=list,
        description="Key entities extracted"
    )
    actions: List[str] = Field(
        default_factory=list,
        description="Actions to perform"
    )
    data_sources: List[str] = Field(
        default_factory=list,
        description="Data sources mentioned"
    )
    outputs: List[str] = Field(
        default_factory=list,
        description="Expected outputs"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Constraints or requirements"
    )
    ambiguities: List[str] = Field(
        default_factory=list,
        description="Unclear aspects that may need clarification"
    )


class GenerationResult(BaseModel):
    """Result of a pipeline generation request."""

    id: str
    status: GenerationStatus
    analysis: Optional[GenerationAnalysis] = None
    suggestions: List[ComponentSuggestion] = Field(default_factory=list)
    pipeline: Optional[GeneratedPipeline] = None
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None

    # Timing
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None


class RefinementRequest(BaseModel):
    """Request to refine a generated pipeline."""

    generation_id: str = Field(description="ID of the generation to refine")
    feedback: str = Field(description="User feedback for refinement")
    modifications: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Specific modifications to apply"
    )


class RefinementResult(BaseModel):
    """Result of a refinement request."""

    original_id: str
    refined_id: str
    changes_made: List[str] = Field(
        default_factory=list,
        description="Description of changes applied"
    )
    pipeline: GeneratedPipeline


# API Request/Response Models

class GeneratePipelineRequest(BaseModel):
    """Request to generate a pipeline from natural language."""

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Natural language description of the desired pipeline"
    )
    mode: GenerationMode = Field(
        default=GenerationMode.DETAILED,
        description="Generation mode"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (available components, constraints, etc.)"
    )
    examples: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Example inputs/outputs to help guide generation"
    )
    preferred_components: Optional[List[str]] = Field(
        default=None,
        description="Components to prefer in generation"
    )
    avoid_components: Optional[List[str]] = Field(
        default=None,
        description="Components to avoid"
    )


class GeneratePipelineResponse(BaseModel):
    """Response from pipeline generation."""

    success: bool
    result: GenerationResult
    message: str


class AnalyzeRequestResponse(BaseModel):
    """Response from request analysis."""

    analysis: GenerationAnalysis
    suggested_approach: str
    estimated_complexity: str  # simple, moderate, complex
    estimated_stages: int


class ComponentMatchRequest(BaseModel):
    """Request to find matching components for a task."""

    task: str = Field(description="Task description")
    limit: int = Field(default=5, ge=1, le=20)


class ComponentMatch(BaseModel):
    """A matched component for a task."""

    component_type: str
    name: str
    description: str
    match_score: float
    match_reason: str


class ComponentMatchResponse(BaseModel):
    """Response with matched components."""

    task: str
    matches: List[ComponentMatch]
