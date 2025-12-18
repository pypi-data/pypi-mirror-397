"""
Inheritance Validator for FlowMason.

Validates pipeline inheritance configurations.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from flowmason_core.config.types import PipelineConfig

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """A single validation issue."""

    level: str  # "error" or "warning"
    code: str  # Machine-readable code
    message: str  # Human-readable message
    pipeline: Optional[str] = None
    stage: Optional[str] = None
    field: Optional[str] = None


@dataclass
class InheritanceValidationResult:
    """Result of inheritance validation."""

    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)

    def add_error(
        self,
        code: str,
        message: str,
        pipeline: Optional[str] = None,
        stage: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        """Add a validation error."""
        self.issues.append(
            ValidationIssue(
                level="error",
                code=code,
                message=message,
                pipeline=pipeline,
                stage=stage,
                field=field,
            )
        )
        self.is_valid = False

    def add_warning(
        self,
        code: str,
        message: str,
        pipeline: Optional[str] = None,
        stage: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        """Add a validation warning."""
        self.issues.append(
            ValidationIssue(
                level="warning",
                code=code,
                message=message,
                pipeline=pipeline,
                stage=stage,
                field=field,
            )
        )

    @property
    def errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.level == "warning"]


# Type for pipeline loader function
PipelineLoader = Callable[[str], Optional[PipelineConfig]]


class InheritanceValidator:
    """
    Validates pipeline inheritance configurations.

    Checks for:
    - Circular inheritance
    - Missing parent pipelines
    - Invalid override targets
    - Abstract stage requirements
    - Composition validity
    - Schema compatibility
    """

    def __init__(self, loader: Optional[PipelineLoader] = None):
        """
        Initialize the validator.

        Args:
            loader: Optional function to load parent pipelines by reference.
                   If not provided, only local validation is performed.
        """
        self.loader = loader

    def validate(
        self,
        pipeline: PipelineConfig,
        deep: bool = True,
    ) -> InheritanceValidationResult:
        """
        Validate a pipeline's inheritance configuration.

        Args:
            pipeline: Pipeline to validate
            deep: If True, load and validate parent pipelines

        Returns:
            InheritanceValidationResult with any issues found
        """
        result = InheritanceValidationResult()

        # Basic validation
        self._validate_basic(pipeline, result)

        # Inheritance validation
        if pipeline.extends:
            self._validate_inheritance(pipeline, result, deep)

        # Override validation
        if pipeline.overrides:
            self._validate_overrides(pipeline, result)

        # Composition validation
        if pipeline.compositions:
            self._validate_compositions(pipeline, result)

        # Abstract pipeline validation
        if pipeline.abstract:
            self._validate_abstract(pipeline, result)

        return result

    def _validate_basic(
        self,
        pipeline: PipelineConfig,
        result: InheritanceValidationResult,
    ) -> None:
        """Validate basic pipeline structure."""
        # Check for duplicate stage IDs
        stage_ids = [s.id for s in pipeline.stages]
        comp_ids = [c.id for c in pipeline.compositions]
        all_ids = stage_ids + comp_ids

        duplicates = [id for id in all_ids if all_ids.count(id) > 1]
        if duplicates:
            result.add_error(
                code="DUPLICATE_STAGE_ID",
                message=f"Duplicate stage/composition IDs: {set(duplicates)}",
                pipeline=pipeline.name,
            )

    def _validate_inheritance(
        self,
        pipeline: PipelineConfig,
        result: InheritanceValidationResult,
        deep: bool,
    ) -> None:
        """Validate inheritance configuration."""
        if not self.loader:
            if deep:
                result.add_warning(
                    code="NO_LOADER",
                    message="Cannot validate inheritance without pipeline loader",
                    pipeline=pipeline.name,
                )
            return

        # Check for circular inheritance
        visited: Set[str] = set()
        current_ref = pipeline.extends
        chain: List[str] = [pipeline.name]

        while current_ref:
            # Parse reference
            ref_key = current_ref

            if ref_key in visited:
                result.add_error(
                    code="CIRCULAR_INHERITANCE",
                    message=f"Circular inheritance detected: {' -> '.join(chain + [current_ref])}",
                    pipeline=pipeline.name,
                )
                return

            visited.add(ref_key)
            chain.append(current_ref)

            # Load parent
            parent = self.loader(current_ref)
            if parent is None:
                result.add_error(
                    code="PARENT_NOT_FOUND",
                    message=f"Parent pipeline not found: {current_ref}",
                    pipeline=pipeline.name,
                    field="extends",
                )
                return

            # Continue up the chain
            current_ref = parent.extends

    def _validate_overrides(
        self,
        pipeline: PipelineConfig,
        result: InheritanceValidationResult,
    ) -> None:
        """Validate override configurations."""
        if not pipeline.extends:
            if pipeline.overrides:
                result.add_warning(
                    code="ORPHAN_OVERRIDES",
                    message="Pipeline has overrides but no parent (extends)",
                    pipeline=pipeline.name,
                )
            return

        # If we have a loader, check that override targets exist in parent
        if self.loader:
            parent = self.loader(pipeline.extends)
            if parent:
                parent_stage_ids = {s.id for s in parent.stages}
                for override_id in pipeline.overrides:
                    if override_id not in parent_stage_ids:
                        result.add_error(
                            code="INVALID_OVERRIDE_TARGET",
                            message=f"Override target '{override_id}' not found in parent",
                            pipeline=pipeline.name,
                            stage=override_id,
                        )

        # Validate override structure
        for stage_id, override_config in pipeline.overrides.items():
            if not isinstance(override_config, dict):
                result.add_error(
                    code="INVALID_OVERRIDE_CONFIG",
                    message=f"Override for '{stage_id}' must be a dictionary",
                    pipeline=pipeline.name,
                    stage=stage_id,
                )

    def _validate_compositions(
        self,
        pipeline: PipelineConfig,
        result: InheritanceValidationResult,
    ) -> None:
        """Validate composition configurations."""
        for comp in pipeline.compositions:
            # Check composition has required fields
            if not comp.pipeline:
                result.add_error(
                    code="MISSING_COMPOSITION_PIPELINE",
                    message=f"Composition '{comp.id}' missing pipeline reference",
                    pipeline=pipeline.name,
                    stage=comp.id,
                )

            # Check dependencies reference valid stages
            all_stage_ids = {s.id for s in pipeline.stages}
            all_stage_ids.update(c.id for c in pipeline.compositions)

            for dep in comp.depends_on:
                if dep not in all_stage_ids and dep != comp.id:
                    result.add_error(
                        code="INVALID_COMPOSITION_DEPENDENCY",
                        message=f"Composition '{comp.id}' depends on unknown stage '{dep}'",
                        pipeline=pipeline.name,
                        stage=comp.id,
                    )

            # If we have a loader, check that composed pipeline exists
            if self.loader:
                composed = self.loader(comp.pipeline)
                if composed is None:
                    result.add_error(
                        code="COMPOSED_PIPELINE_NOT_FOUND",
                        message=f"Composed pipeline not found: {comp.pipeline}",
                        pipeline=pipeline.name,
                        stage=comp.id,
                    )
                elif composed.abstract:
                    result.add_error(
                        code="CANNOT_COMPOSE_ABSTRACT",
                        message=f"Cannot compose abstract pipeline: {comp.pipeline}",
                        pipeline=pipeline.name,
                        stage=comp.id,
                    )

    def _validate_abstract(
        self,
        pipeline: PipelineConfig,
        result: InheritanceValidationResult,
    ) -> None:
        """Validate abstract pipeline configuration."""
        # Check for abstract stages (component_type: "abstract")
        # Support both 'type' (PipelineConfig) and 'component_type' (PipelineFile/PipelineStage)
        abstract_stages = []
        for s in pipeline.stages:
            stage_type = getattr(s, "type", None) or getattr(s, "component_type", None)
            if stage_type == "abstract":
                abstract_stages.append(s)

        if not abstract_stages and not pipeline.extends:
            result.add_warning(
                code="UNNECESSARY_ABSTRACT",
                message="Abstract pipeline has no abstract stages - consider removing 'abstract: true'",
                pipeline=pipeline.name,
            )

        # Abstract stages should have minimal config
        for stage in abstract_stages:
            stage_input_mapping = getattr(stage, "input_mapping", None)
            if stage_input_mapping:
                result.add_warning(
                    code="ABSTRACT_STAGE_HAS_CONFIG",
                    message=f"Abstract stage '{stage.id}' has input_mapping which will be ignored",
                    pipeline=pipeline.name,
                    stage=stage.id,
                )


def validate_inheritance(
    pipeline: PipelineConfig,
    loader: Optional[PipelineLoader] = None,
) -> InheritanceValidationResult:
    """
    Convenience function to validate pipeline inheritance.

    Args:
        pipeline: Pipeline to validate
        loader: Optional loader for parent pipelines

    Returns:
        Validation result
    """
    validator = InheritanceValidator(loader)
    return validator.validate(pipeline)
