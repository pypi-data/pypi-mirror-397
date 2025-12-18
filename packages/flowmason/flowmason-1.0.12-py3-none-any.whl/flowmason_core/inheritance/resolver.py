"""
Inheritance Resolver for FlowMason.

Resolves pipeline inheritance chains and produces fully-resolved pipeline configs.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Set

from flowmason_core.config.types import PipelineConfig

logger = logging.getLogger(__name__)


class CircularInheritanceError(Exception):
    """Raised when circular inheritance is detected."""

    def __init__(self, chain: List[str]):
        self.chain = chain
        super().__init__(f"Circular inheritance detected: {' -> '.join(chain)}")


class PipelineNotFoundError(Exception):
    """Raised when a referenced pipeline cannot be found."""

    def __init__(self, pipeline_ref: str, context: Optional[str] = None):
        self.pipeline_ref = pipeline_ref
        self.context = context
        msg = f"Pipeline not found: {pipeline_ref}"
        if context:
            msg += f" (referenced from {context})"
        super().__init__(msg)


class AbstractPipelineError(Exception):
    """Raised when attempting to execute an abstract pipeline."""

    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        super().__init__(
            f"Cannot execute abstract pipeline '{pipeline_id}'. "
            "Abstract pipelines must be extended."
        )


# Type for pipeline loader function
PipelineLoader = Callable[[str], Optional[PipelineConfig]]


class InheritanceResolver:
    """
    Resolves pipeline inheritance to produce fully-resolved pipeline configs.

    Handles:
    - Loading parent pipelines from various sources
    - Detecting and preventing circular inheritance
    - Building the inheritance chain
    - Caching resolved pipelines for performance
    """

    def __init__(self, loader: PipelineLoader):
        """
        Initialize the resolver.

        Args:
            loader: Function that loads a PipelineConfig given a reference string.
                   The reference can be a name, name@version, or path.
                   Returns None if the pipeline is not found.
        """
        self.loader = loader
        self._cache: Dict[str, PipelineConfig] = {}
        self._resolution_stack: Set[str] = set()

    def resolve(
        self,
        pipeline: PipelineConfig,
        check_abstract: bool = True,
    ) -> PipelineConfig:
        """
        Resolve a pipeline's inheritance chain and return the fully-resolved config.

        Args:
            pipeline: The pipeline config to resolve
            check_abstract: If True, raise error for abstract pipelines

        Returns:
            Fully-resolved PipelineConfig with all inherited stages merged

        Raises:
            CircularInheritanceError: If circular inheritance is detected
            PipelineNotFoundError: If a parent pipeline cannot be found
            AbstractPipelineError: If trying to execute an abstract pipeline
        """
        # Check if this is an abstract pipeline being executed directly
        if check_abstract and pipeline.abstract:
            raise AbstractPipelineError(pipeline.id)

        # If no inheritance, return as-is
        if not pipeline.extends:
            return pipeline

        # Build inheritance chain
        chain = self._build_inheritance_chain(pipeline)

        # Merge from base to child
        from flowmason_core.inheritance.merger import PipelineMerger

        merger = PipelineMerger()
        resolved = merger.merge_chain(chain)

        return resolved

    def _build_inheritance_chain(self, pipeline: PipelineConfig) -> List[PipelineConfig]:
        """
        Build the inheritance chain from base to child.

        Returns a list where the first element is the root base pipeline
        and the last element is the provided pipeline.
        """
        chain: List[PipelineConfig] = []
        visited: Set[str] = set()
        current = pipeline

        # Walk up the inheritance chain
        while current is not None:
            # Check for circular inheritance
            pipeline_key = f"{current.name}@{current.version}"
            if pipeline_key in visited:
                # Build the cycle path for error message
                cycle_path = [p.name for p in chain] + [current.name]
                raise CircularInheritanceError(cycle_path)

            visited.add(pipeline_key)
            chain.append(current)

            # Load parent if exists
            if current.extends:
                parent = self._load_pipeline(current.extends, current.name)
                current = parent
            else:
                current = None

        # Reverse so base is first
        chain.reverse()

        logger.debug(
            f"Built inheritance chain for '{pipeline.name}': "
            f"{' -> '.join(p.name for p in chain)}"
        )

        return chain

    def _load_pipeline(self, ref: str, context: str) -> PipelineConfig:
        """
        Load a pipeline by reference.

        Args:
            ref: Pipeline reference (name, name@version, or path)
            context: Name of the pipeline requesting this (for error messages)

        Returns:
            Loaded PipelineConfig

        Raises:
            PipelineNotFoundError: If pipeline cannot be found
        """
        # Check cache first
        if ref in self._cache:
            return self._cache[ref]

        # Load via loader function
        pipeline = self.loader(ref)
        if pipeline is None:
            raise PipelineNotFoundError(ref, context)

        # Cache and return
        self._cache[ref] = pipeline
        return pipeline

    def get_inheritance_chain(self, pipeline: PipelineConfig) -> List[str]:
        """
        Get the names in the inheritance chain (for display/debugging).

        Returns list from base to child.
        """
        if not pipeline.extends:
            return [pipeline.name]

        chain = self._build_inheritance_chain(pipeline)
        return [p.name for p in chain]

    def clear_cache(self) -> None:
        """Clear the pipeline cache."""
        self._cache.clear()
