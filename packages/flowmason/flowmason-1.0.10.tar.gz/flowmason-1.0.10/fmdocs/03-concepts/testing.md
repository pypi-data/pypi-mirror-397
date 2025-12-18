# Pipeline Testing

FlowMason provides a comprehensive testing framework for pipeline development, including mocking, snapshot testing, and LLM call recording.

## Overview

The testing module includes:
- **MockProvider**: Mock LLM providers for deterministic testing
- **ComponentMocker**: Mock individual components and stages
- **SnapshotManager**: Snapshot testing for pipeline outputs
- **LLMCallRecorder**: Record and replay LLM calls

## Quick Start

```python
from flowmason_core.testing import (
    MockProvider,
    MockContext,
    ComponentMocker,
    assert_snapshot,
)

# Create a mock provider with predetermined responses
provider = MockProvider(responses=[
    "First LLM response",
    "Second LLM response",
])

# Test with the mock provider
response = provider.call("What is AI?")
assert response.content == "First LLM response"
assert provider.call_count == 1
```

## Mock Provider

The `MockProvider` allows you to test pipelines without making actual LLM calls.

### Basic Usage

```python
from flowmason_core.testing import MockProvider, ProviderResponse

# Create with simple string responses
provider = MockProvider(responses=[
    "Hello, world!",
    "How can I help you?",
])

# Or with full ProviderResponse objects
provider = MockProvider(responses=[
    ProviderResponse(
        content="Hello, world!",
        model="gpt-4",
        usage={"input_tokens": 10, "output_tokens": 20},
        success=True,
    ),
])

# Use in your pipeline
result = provider.call("Say hello")
print(result.content)  # "Hello, world!"
```

### Tracking Calls

```python
provider = MockProvider(responses=["Response 1", "Response 2"])

# Make some calls
provider.call("First prompt")
provider.call("Second prompt", system="Be helpful")

# Check call history
print(provider.call_count)  # 2
print(provider.call_history[0]["prompt"])  # "First prompt"
print(provider.call_history[1]["system"])  # "Be helpful"

# Reset for next test
provider.reset()
```

## Component Mocking

The `ComponentMocker` allows you to mock specific components or stages.

### Mock by Component Type

```python
from flowmason_core.testing import ComponentMocker

mocker = ComponentMocker()

# Mock all generators
mocker.mock_component("generator", responses=[
    {"content": "Generated content 1"},
    {"content": "Generated content 2"},
])

# Mock with custom handler
mocker.mock_component(
    "filter",
    handler=lambda input: {"filtered": input.get("items", [])[:3]}
)

# Apply mocks during test
with mocker.apply():
    result = await run_pipeline(...)

# Check calls
print(mocker.get_component_calls("generator"))
```

### Mock by Stage ID

```python
mocker = ComponentMocker()

# Mock specific stages
stage_mock = mocker.mock_stage(
    "extract-data",
    responses=[{"data": [1, 2, 3]}],
)

stage_mock = mocker.mock_stage(
    "validate-data",
    should_fail=True,
    error_message="Validation failed",
)

# Check stage calls
print(stage_mock.call_count)
print(stage_mock.call_history)
```

## Snapshot Testing

Snapshot testing captures pipeline outputs and compares them against saved baselines.

### Basic Snapshot Testing

```python
from flowmason_core.testing import assert_snapshot

# Run pipeline and capture output
result = await run_pipeline("my-pipeline", input_data)

# Assert against snapshot
assert_snapshot(
    name="my_pipeline_output",
    actual=result,
    snapshot_dir="tests/snapshots",
)
```

### Using SnapshotManager

```python
from flowmason_core.testing import SnapshotManager, format_diff_report

snapshots = SnapshotManager("tests/snapshots")

# Save initial snapshot
snapshots.save("pipeline_v1", result, metadata={
    "pipeline_version": "1.0.0",
    "test_date": "2024-01-15",
})

# Compare new output
comparison = snapshots.compare("pipeline_v1", new_result)

if not comparison.matches:
    print(format_diff_report(comparison))

    # Optionally update if changes are expected
    # snapshots.update("pipeline_v1", new_result)
```

### Ignoring Dynamic Fields

```python
# Ignore timestamps and IDs that change between runs
snapshots = SnapshotManager(
    "tests/snapshots",
    ignore_keys=[
        "timestamp",
        "run_id",
        "created_at",
        "duration_ms",
    ],
)
```

### Snapshot All Stages

```python
from flowmason_core.testing import snapshot_stage_outputs

# Snapshot each stage output separately
results = snapshot_stage_outputs(
    stage_results=pipeline_result["stage_results"],
    snapshot_dir="tests/snapshots/stages",
    prefix="test_case_1_",
)

# Check which stages match
for stage_id, result in results.items():
    if not result.matches:
        print(f"Stage {stage_id} output changed")
```

## LLM Call Recording

Record actual LLM calls for deterministic replay in tests.

### Recording Calls

```python
from flowmason_core.testing import LLMCallRecorder

recorder = LLMCallRecorder()

# Record calls during execution
with recorder.record():
    result = await run_pipeline(...)

# Save recorded calls
recorder.save("tests/fixtures/llm_calls.json")
print(f"Recorded {len(recorder.calls)} LLM calls")
```

### Replaying Calls

```python
recorder = LLMCallRecorder()

# Replay recorded calls
with recorder.replay("tests/fixtures/llm_calls.json"):
    result = await run_pipeline(...)
    # LLM calls return recorded responses instead of making real calls
```

## Mock Context

Use `MockContext` when testing components that require execution context.

```python
from flowmason_core.testing import MockContext, MockProvider

context = MockContext(
    run_id="test-run-001",
    pipeline_id="test-pipeline",
    pipeline_input={"query": "test input"},
    variables={"api_key": "test-key"},
    providers={"default": MockProvider(responses=["Test response"])},
)

# Use context in component tests
result = await my_component.execute(input_data, context=context)
```

## Creating Test Executors

For testing pipeline execution logic, create mock executors:

```python
from flowmason_core.testing import create_mock_executor

# Define expected stage outputs
mock_executor = create_mock_executor({
    "extract": {"data": [1, 2, 3]},
    "transform": {"result": [2, 4, 6]},
    "load": {"status": "success"},
})

# Use in pipeline tests
result = await run_with_executor(pipeline, mock_executor)

# Check what was called
print(mock_executor.call_history)
```

## Best Practices

### 1. Use Deterministic Tests

```python
# Good: Deterministic mock responses
provider = MockProvider(responses=["Fixed response"])

# Avoid: Random or time-dependent tests
```

### 2. Isolate LLM Calls

```python
# Mock LLM calls for fast, reliable tests
mocker = ComponentMocker()
mocker.mock_component("generator", responses=["Mocked LLM output"])
```

### 3. Update Snapshots Intentionally

```python
# Only update when changes are expected
if os.environ.get("UPDATE_SNAPSHOTS"):
    snapshots.update("test_name", result)
else:
    comparison = snapshots.compare("test_name", result)
    assert comparison.matches
```

### 4. Record Once, Replay Often

```python
# Record LLM calls in integration tests
if os.environ.get("RECORD_LLM_CALLS"):
    with recorder.record():
        result = await run_pipeline(...)
    recorder.save("fixtures/llm_calls.json")
else:
    # Replay in unit tests
    with recorder.replay("fixtures/llm_calls.json"):
        result = await run_pipeline(...)
```

### 5. Test Error Handling

```python
# Test failure scenarios
mocker.mock_stage(
    "validate",
    should_fail=True,
    error_message="Invalid input format",
)

with pytest.raises(PipelineError) as exc:
    await run_pipeline(...)

assert "Invalid input format" in str(exc.value)
```

## Complete Test Example

```python
import pytest
from flowmason_core.testing import (
    MockProvider,
    MockContext,
    ComponentMocker,
    SnapshotManager,
    assert_snapshot,
)

@pytest.fixture
def mock_provider():
    return MockProvider(responses=[
        "Summary of the input text",
        "Key points: 1, 2, 3",
    ])

@pytest.fixture
def mocker():
    m = ComponentMocker()
    m.mock_component("generator", responses=[
        {"summary": "Test summary"},
    ])
    return m

@pytest.fixture
def snapshots():
    return SnapshotManager("tests/snapshots")

async def test_pipeline_output(mock_provider, mocker, snapshots):
    """Test pipeline produces expected output."""
    context = MockContext(
        providers={"default": mock_provider},
    )

    with mocker.apply():
        result = await run_pipeline(
            "summarizer",
            input_data={"text": "Long document..."},
            context=context,
        )

    # Assert structure
    assert result["success"] is True
    assert "summary" in result["output"]

    # Assert against snapshot
    assert_snapshot("summarizer_output", result["output"])

    # Verify LLM was called correctly
    assert mock_provider.call_count == 1
    assert "Long document" in mock_provider.call_history[0]["prompt"]

async def test_pipeline_handles_errors(mocker):
    """Test pipeline error handling."""
    mocker.mock_stage("validate", should_fail=True)

    with pytest.raises(StageError) as exc:
        await run_pipeline("validator", {"data": "test"})

    assert "Mocked error" in str(exc.value)
```
