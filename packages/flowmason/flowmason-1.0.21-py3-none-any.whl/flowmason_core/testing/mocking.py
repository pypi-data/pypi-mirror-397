"""
FlowMason Component Mocking

Provides utilities for mocking components, stages, and dependencies during testing.
"""

import functools
import json
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, List, Optional, Union
from unittest.mock import MagicMock, patch


@dataclass
class MockResponse:
    """A configurable mock response for stages or components."""
    output: Any
    success: bool = True
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration_ms: int = 100
    usage: Optional[Dict[str, Any]] = None


@dataclass
class StageMock:
    """
    Mock configuration for a pipeline stage.

    Usage:
        mock = StageMock(
            stage_id="my-stage",
            responses=[{"result": "mocked output"}],
        )
    """
    stage_id: str
    responses: List[Any] = field(default_factory=list)
    should_fail: bool = False
    error_message: str = "Mocked error"
    call_history: List[Dict[str, Any]] = field(default_factory=list)
    _call_index: int = 0

    def get_response(self, input_data: Dict[str, Any]) -> MockResponse:
        """Get the next response for this stage."""
        self.call_history.append(input_data)

        if self.should_fail:
            return MockResponse(
                output=None,
                success=False,
                error=self.error_message,
                error_type="MockError",
            )

        if self._call_index < len(self.responses):
            response = self.responses[self._call_index]
            self._call_index += 1
        else:
            response = {"mocked": True, "stage": self.stage_id}

        return MockResponse(output=response)

    @property
    def call_count(self) -> int:
        """Number of times this stage was called."""
        return len(self.call_history)

    def reset(self) -> None:
        """Reset the mock state."""
        self._call_index = 0
        self.call_history = []


class ComponentMocker:
    """
    Mock components during pipeline testing.

    Usage:
        mocker = ComponentMocker()

        # Mock a specific component type
        mocker.mock_component("generator", responses=["Hello, world!"])

        # Mock with custom function
        mocker.mock_component(
            "filter",
            handler=lambda input: {"filtered": input["items"][:5]}
        )

        # Apply mocks and run tests
        with mocker.apply():
            result = await run_pipeline(...)
    """

    def __init__(self):
        self._component_mocks: Dict[str, Dict[str, Any]] = {}
        self._stage_mocks: Dict[str, StageMock] = {}
        self._patches: List[Any] = []

    def mock_component(
        self,
        component_type: str,
        responses: Optional[List[Any]] = None,
        handler: Optional[Callable[[Dict[str, Any]], Any]] = None,
        should_fail: bool = False,
        error_message: str = "Component mock error",
    ) -> None:
        """
        Mock a component type.

        Args:
            component_type: The component type to mock (e.g., "generator")
            responses: List of responses to return in sequence
            handler: Custom handler function for generating responses
            should_fail: If True, always return failure
            error_message: Error message when should_fail is True
        """
        self._component_mocks[component_type] = {
            "responses": responses or [],
            "handler": handler,
            "should_fail": should_fail,
            "error_message": error_message,
            "call_index": 0,
            "call_history": [],
        }

    def mock_stage(
        self,
        stage_id: str,
        responses: Optional[List[Any]] = None,
        should_fail: bool = False,
        error_message: str = "Stage mock error",
    ) -> StageMock:
        """
        Mock a specific stage by ID.

        Args:
            stage_id: The stage ID to mock
            responses: List of responses to return
            should_fail: If True, always return failure
            error_message: Error message when should_fail is True

        Returns:
            StageMock instance for further configuration
        """
        mock = StageMock(
            stage_id=stage_id,
            responses=responses or [],
            should_fail=should_fail,
            error_message=error_message,
        )
        self._stage_mocks[stage_id] = mock
        return mock

    def get_component_calls(self, component_type: str) -> List[Dict[str, Any]]:
        """Get call history for a component type."""
        mock = self._component_mocks.get(component_type)
        if mock:
            history: List[Dict[str, Any]] = mock["call_history"]
            return history
        return []

    def get_stage_calls(self, stage_id: str) -> List[Dict[str, Any]]:
        """Get call history for a stage."""
        mock = self._stage_mocks.get(stage_id)
        return mock.call_history if mock else []

    def _get_mock_response(
        self,
        component_type: str,
        input_data: Dict[str, Any],
    ) -> MockResponse:
        """Get mock response for a component call."""
        mock = self._component_mocks.get(component_type)

        if not mock:
            return MockResponse(output={"unmocked": True})

        mock["call_history"].append(input_data)

        if mock["should_fail"]:
            return MockResponse(
                output=None,
                success=False,
                error=mock["error_message"],
                error_type="MockError",
            )

        if mock["handler"]:
            try:
                result = mock["handler"](input_data)
                return MockResponse(output=result)
            except Exception as e:
                return MockResponse(
                    output=None,
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__,
                )

        if mock["call_index"] < len(mock["responses"]):
            response = mock["responses"][mock["call_index"]]
            mock["call_index"] += 1
            return MockResponse(output=response)

        return MockResponse(output={"mocked": True, "component": component_type})

    def is_stage_mocked(self, stage_id: str) -> bool:
        """Check if a stage is mocked."""
        return stage_id in self._stage_mocks

    def is_component_mocked(self, component_type: str) -> bool:
        """Check if a component type is mocked."""
        return component_type in self._component_mocks

    @contextmanager
    def apply(self) -> Generator["ComponentMocker", None, None]:
        """
        Apply mocks for the duration of a test.

        Usage:
            with mocker.apply():
                result = await run_pipeline(...)
        """
        # Store self reference for nested contexts
        yield self

    def reset(self) -> None:
        """Reset all mocks to initial state."""
        for mock in self._component_mocks.values():
            mock["call_index"] = 0
            mock["call_history"] = []

        for stage_mock in self._stage_mocks.values():
            stage_mock.reset()


class LLMCallRecorder:
    """
    Records LLM calls for replay testing.

    Usage:
        recorder = LLMCallRecorder()

        # Record calls
        with recorder.record():
            result = await run_pipeline(...)

        # Save for replay
        recorder.save("llm_calls.json")

        # Later, replay recorded calls
        with recorder.replay("llm_calls.json"):
            result = await run_pipeline(...)
    """

    def __init__(self):
        self._recorded_calls: List[Dict[str, Any]] = []
        self._replay_index = 0
        self._is_recording = False
        self._is_replaying = False

    def record_call(
        self,
        provider: str,
        model: str,
        prompt: str,
        system: Optional[str],
        response: str,
        usage: Dict[str, Any],
    ) -> None:
        """Record an LLM call."""
        if self._is_recording:
            self._recorded_calls.append({
                "provider": provider,
                "model": model,
                "prompt": prompt,
                "system": system,
                "response": response,
                "usage": usage,
            })

    def get_replay_response(self) -> Optional[Dict[str, Any]]:
        """Get the next recorded response for replay."""
        if not self._is_replaying:
            return None

        if self._replay_index >= len(self._recorded_calls):
            return None

        call: Dict[str, Any] = self._recorded_calls[self._replay_index]
        self._replay_index += 1
        return call

    @contextmanager
    def record(self) -> Generator["LLMCallRecorder", None, None]:
        """Start recording LLM calls."""
        self._is_recording = True
        self._recorded_calls = []
        try:
            yield self
        finally:
            self._is_recording = False

    @contextmanager
    def replay(
        self,
        file_path: Optional[str] = None,
    ) -> Generator["LLMCallRecorder", None, None]:
        """Replay recorded LLM calls."""
        if file_path:
            self.load(file_path)

        self._is_replaying = True
        self._replay_index = 0
        try:
            yield self
        finally:
            self._is_replaying = False

    def save(self, file_path: str) -> None:
        """Save recorded calls to a file."""
        with open(file_path, "w") as f:
            json.dump(self._recorded_calls, f, indent=2)

    def load(self, file_path: str) -> None:
        """Load recorded calls from a file."""
        with open(file_path, "r") as f:
            self._recorded_calls = json.load(f)

    @property
    def calls(self) -> List[Dict[str, Any]]:
        """Get all recorded calls."""
        return self._recorded_calls


def create_mock_executor(
    stage_responses: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Create a mock executor function for testing.

    Args:
        stage_responses: Map of stage_id to response values

    Returns:
        Mock executor function
    """
    responses = stage_responses or {}
    call_history: List[Dict[str, Any]] = []

    async def mock_executor(
        stage_id: str,
        component_type: str,
        input_data: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        call_history.append({
            "stage_id": stage_id,
            "component_type": component_type,
            "input": input_data,
            "config": config,
        })

        if stage_id in responses:
            return {
                "output": responses[stage_id],
                "success": True,
            }

        return {
            "output": {"mocked": True, "stage": stage_id},
            "success": True,
        }

    mock_executor.call_history = call_history  # type: ignore
    return mock_executor


__all__ = [
    "MockResponse",
    "StageMock",
    "ComponentMocker",
    "LLMCallRecorder",
    "create_mock_executor",
]
