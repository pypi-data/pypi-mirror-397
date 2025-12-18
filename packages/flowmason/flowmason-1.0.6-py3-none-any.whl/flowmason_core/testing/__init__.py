"""FlowMason Testing Framework.

Provides utilities for testing FlowMason components including:
- Mock providers for LLM testing
- Component and stage mocking
- Snapshot testing for pipeline outputs
- LLM call recording and replay
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional

from flowmason_core.providers.base import (
    ProviderBase,
    ProviderCapability,
    ProviderResponse,
)

# Import mocking utilities
from .mocking import (
    MockResponse,
    StageMock,
    ComponentMocker,
    LLMCallRecorder,
    create_mock_executor,
)

# Import snapshot utilities
from .snapshots import (
    SnapshotDiff,
    SnapshotResult,
    SnapshotManager,
    assert_snapshot,
    snapshot_stage_outputs,
    format_diff_report,
)


class MockProvider(ProviderBase):
    """
    Mock provider for testing FlowMason components.

    Allows you to specify pre-defined responses that will be returned
    in sequence when the provider is called.

    Example:
        provider = MockProvider(responses=[
            "First response",
            "Second response",
        ])

        # Or with full ProviderResponse objects:
        provider = MockProvider(responses=[
            ProviderResponse(content="Hello", model="mock"),
        ])
    """

    def __init__(
        self,
        responses: Optional[List[Any]] = None,
        model: str = "mock-model",
        **kwargs
    ):
        """
        Initialize MockProvider.

        Args:
            responses: List of responses to return. Can be strings or ProviderResponse objects.
            model: Model name to report in responses.
        """
        # Don't call super().__init__() as it requires api_key
        self._model = model
        self._responses = responses or []
        self._call_index = 0
        self._call_history: List[Dict[str, Any]] = []
        self.api_key = "mock-key"
        self.timeout = 30
        self.max_retries = 0
        self.pricing = {"input": 0.0, "output": 0.0}

    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return self._model

    @property
    def available_models(self) -> List[str]:
        return [self._model]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STREAMING,
            ProviderCapability.FUNCTION_CALLING,
        ]

    @property
    def call_history(self) -> List[Dict[str, Any]]:
        """Get the history of all calls made to this provider."""
        return self._call_history

    @property
    def call_count(self) -> int:
        """Get the number of calls made to this provider."""
        return len(self._call_history)

    def add_response(self, response: Any) -> None:
        """Add a response to the queue."""
        self._responses.append(response)

    def reset(self) -> None:
        """Reset the provider state."""
        self._call_index = 0
        self._call_history = []

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any
    ) -> ProviderResponse:
        """
        Make a mock call and return the next response.

        Args:
            prompt: The prompt text
            system: Optional system prompt
            model: Optional model override
            **kwargs: Additional arguments (ignored)

        Returns:
            The next ProviderResponse in the queue
        """
        # Record the call
        self._call_history.append({
            "prompt": prompt,
            "system": system,
            "model": model or self._model,
            "kwargs": kwargs,
        })

        # Get the response
        if self._call_index < len(self._responses):
            response = self._responses[self._call_index]
            self._call_index += 1
        else:
            # Default response if no more in queue
            response = f"Mock response {self._call_index + 1}"
            self._call_index += 1

        # Convert string to ProviderResponse if needed
        if isinstance(response, str):
            return ProviderResponse(
                content=response,
                model=model or self._model,
                usage={"input_tokens": 10, "output_tokens": 20},
                success=True,
            )
        elif isinstance(response, ProviderResponse):
            return response
        else:
            # Assume it's a dict-like
            return ProviderResponse(
                content=str(response.get("content", response)),
                model=model or self._model,
                usage=response.get("usage", {}),
                success=True,
            )

    async def call_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any
    ) -> ProviderResponse:
        """Async version of call (just wraps sync version)."""
        return self.call(prompt, system, model, temperature, max_tokens, **kwargs)

    def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """Mock streaming - yields the response in chunks."""
        response = self.call(prompt, system, model, temperature, max_tokens, **kwargs)
        # Yield in small chunks
        content = response.content
        chunk_size = 10
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]


@dataclass
class MockContext:
    """
    Mock execution context for testing.

    Provides a minimal context object that can be used when testing
    components that require an execution context.
    """
    run_id: str = "test-run-001"
    pipeline_id: str = "test-pipeline"
    pipeline_version: str = "1.0.0"
    pipeline_input: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    providers: Dict[str, Any] = field(default_factory=dict)

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value."""
        return self.variables.get(name, default)

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable value."""
        self.variables[name] = value

    def get_provider(self, name: str) -> Optional[Any]:
        """Get a provider by name."""
        return self.providers.get(name)


__all__ = [
    # Mock provider
    "MockProvider",
    "MockContext",
    "ProviderResponse",
    # Mocking utilities
    "MockResponse",
    "StageMock",
    "ComponentMocker",
    "LLMCallRecorder",
    "create_mock_executor",
    # Snapshot testing
    "SnapshotDiff",
    "SnapshotResult",
    "SnapshotManager",
    "assert_snapshot",
    "snapshot_stage_outputs",
    "format_diff_report",
]
