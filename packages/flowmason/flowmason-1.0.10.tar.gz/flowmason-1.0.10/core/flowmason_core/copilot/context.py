"""
Copilot Context for FlowMason.

Serializes pipeline state and context for LLM consumption.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class StageSnapshot:
    """Snapshot of a single stage for context."""
    id: str
    component_type: str
    name: Optional[str] = None
    description: Optional[str] = None
    input_mapping: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class PipelineSnapshot:
    """Snapshot of pipeline state for context."""
    name: str
    version: str
    description: str
    stages: List[StageSnapshot]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    output_stage_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "stages": [
                {
                    "id": s.id,
                    "component_type": s.component_type,
                    "name": s.name,
                    "input_mapping": s.input_mapping,
                    "depends_on": s.depends_on,
                }
                for s in self.stages
            ],
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "output_stage_id": self.output_stage_id,
        }


@dataclass
class ExecutionSnapshot:
    """Snapshot of execution state for debugging context."""
    run_id: str
    status: str
    current_stage: Optional[str] = None
    completed_stages: List[str] = field(default_factory=list)
    failed_stage: Optional[str] = None
    error_message: Optional[str] = None
    stage_outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistrySnapshot:
    """Snapshot of available components."""
    components: List[Dict[str, Any]] = field(default_factory=list)

    def get_component_names(self) -> List[str]:
        """Get list of component names."""
        return [c.get("name", "") for c in self.components]

    def get_component_by_type(self, component_type: str) -> Optional[Dict[str, Any]]:
        """Get component info by type."""
        for c in self.components:
            if c.get("type") == component_type or c.get("name") == component_type:
                return c
        return None


@dataclass
class CopilotContext:
    """
    Context for AI copilot interactions.

    Aggregates all relevant information for the LLM:
    - Current pipeline structure
    - Available components
    - Execution history (if debugging)
    - User request
    """
    pipeline: Optional[PipelineSnapshot] = None
    registry: Optional[RegistrySnapshot] = None
    execution: Optional[ExecutionSnapshot] = None
    selected_stage_id: Optional[str] = None
    user_request: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_pipeline(cls, pipeline: Any) -> "CopilotContext":
        """Create context from a pipeline object."""
        stages = []
        for stage in getattr(pipeline, "stages", []):
            stage_type = (
                getattr(stage, "component_type", None) or
                getattr(stage, "component", None) or
                getattr(stage, "type", "unknown")
            )
            stages.append(StageSnapshot(
                id=getattr(stage, "id", ""),
                component_type=stage_type,
                name=getattr(stage, "name", None),
                description=getattr(stage, "description", None),
                input_mapping=getattr(stage, "input_mapping", {}),
                depends_on=getattr(stage, "depends_on", []),
            ))

        # Get schemas
        input_schema = {}
        output_schema = {}
        if hasattr(pipeline, "input_schema"):
            schema = pipeline.input_schema
            if hasattr(schema, "model_dump"):
                input_schema = schema.model_dump()
            elif isinstance(schema, dict):
                input_schema = schema

        if hasattr(pipeline, "output_schema"):
            schema = pipeline.output_schema
            if hasattr(schema, "model_dump"):
                output_schema = schema.model_dump()
            elif isinstance(schema, dict):
                output_schema = schema

        snapshot = PipelineSnapshot(
            name=getattr(pipeline, "name", ""),
            version=getattr(pipeline, "version", "1.0.0"),
            description=getattr(pipeline, "description", ""),
            stages=stages,
            input_schema=input_schema,
            output_schema=output_schema,
            output_stage_id=getattr(pipeline, "output_stage_id", None),
            tags=getattr(pipeline, "tags", []),
            category=getattr(pipeline, "category", None),
        )

        return cls(pipeline=snapshot)

    def add_registry(self, components: List[Dict[str, Any]]) -> "CopilotContext":
        """Add available components to context."""
        self.registry = RegistrySnapshot(components=components)
        return self

    def add_execution(
        self,
        run_id: str,
        status: str,
        current_stage: Optional[str] = None,
        completed_stages: Optional[List[str]] = None,
        failed_stage: Optional[str] = None,
        error_message: Optional[str] = None,
        stage_outputs: Optional[Dict[str, Any]] = None,
    ) -> "CopilotContext":
        """Add execution state to context."""
        self.execution = ExecutionSnapshot(
            run_id=run_id,
            status=status,
            current_stage=current_stage,
            completed_stages=completed_stages or [],
            failed_stage=failed_stage,
            error_message=error_message,
            stage_outputs=stage_outputs or {},
        )
        return self

    def select_stage(self, stage_id: str) -> "CopilotContext":
        """Select a specific stage for focused assistance."""
        self.selected_stage_id = stage_id
        return self

    def set_request(self, request: str) -> "CopilotContext":
        """Set the user's request."""
        self.user_request = request
        return self

    def add_message(self, role: str, content: str) -> "CopilotContext":
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        return self

    def to_prompt_context(self) -> str:
        """
        Serialize context for inclusion in LLM prompt.

        Returns a formatted string representation of the context.
        """
        parts = []

        # Pipeline context
        if self.pipeline:
            parts.append("## Current Pipeline")
            parts.append(f"Name: {self.pipeline.name}")
            parts.append(f"Version: {self.pipeline.version}")
            if self.pipeline.description:
                parts.append(f"Description: {self.pipeline.description}")
            parts.append("")

            parts.append("### Stages")
            for i, stage in enumerate(self.pipeline.stages):
                deps = f" (depends on: {', '.join(stage.depends_on)})" if stage.depends_on else ""
                parts.append(f"{i+1}. **{stage.id}** ({stage.component_type}){deps}")
            parts.append("")

            parts.append("### Input Schema")
            parts.append(f"```json\n{json.dumps(self.pipeline.input_schema, indent=2)}\n```")
            parts.append("")

            parts.append("### Output Schema")
            parts.append(f"```json\n{json.dumps(self.pipeline.output_schema, indent=2)}\n```")
            parts.append("")

        # Selected stage
        if self.selected_stage_id and self.pipeline:
            selected = next((s for s in self.pipeline.stages if s.id == self.selected_stage_id), None)
            if selected:
                parts.append(f"## Selected Stage: {selected.id}")
                parts.append(f"Type: {selected.component_type}")
                if selected.input_mapping:
                    parts.append(f"Input Mapping: {json.dumps(selected.input_mapping, indent=2)}")
                parts.append("")

        # Execution context
        if self.execution:
            parts.append("## Execution State")
            parts.append(f"Run ID: {self.execution.run_id}")
            parts.append(f"Status: {self.execution.status}")
            if self.execution.current_stage:
                parts.append(f"Current Stage: {self.execution.current_stage}")
            if self.execution.completed_stages:
                parts.append(f"Completed: {', '.join(self.execution.completed_stages)}")
            if self.execution.failed_stage:
                parts.append(f"Failed Stage: {self.execution.failed_stage}")
                if self.execution.error_message:
                    parts.append(f"Error: {self.execution.error_message}")
            parts.append("")

        # Available components
        if self.registry:
            parts.append("## Available Components")
            component_names = self.registry.get_component_names()
            parts.append(", ".join(component_names[:20]))  # Limit to 20
            if len(component_names) > 20:
                parts.append(f"... and {len(component_names) - 20} more")
            parts.append("")

        return "\n".join(parts)

    def to_json(self) -> str:
        """Serialize context to JSON."""
        data = {
            "pipeline": self.pipeline.to_dict() if self.pipeline else None,
            "selected_stage_id": self.selected_stage_id,
            "user_request": self.user_request,
        }
        if self.execution:
            data["execution"] = {
                "run_id": self.execution.run_id,
                "status": self.execution.status,
                "current_stage": self.execution.current_stage,
                "failed_stage": self.execution.failed_stage,
                "error_message": self.execution.error_message,
            }
        return json.dumps(data, indent=2)
