# API Reference

Public Apex API for the Flowmason managed package.

## PipelineRunner

Main class for synchronous pipeline execution.

### execute

```apex
global static ExecutionResult execute(String pipelineJson, Map<String, Object> input)
```

Execute a pipeline synchronously.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `pipelineJson` | String | Pipeline definition as JSON |
| `input` | Map<String, Object> | Pipeline input data |

**Returns**: `ExecutionResult` - Execution result with status and output

**Example**:
```apex
String pipelineJson = '{"name":"Test","stages":[...],"output_stage_id":"output"}';
Map<String, Object> input = new Map<String, Object>{'message' => 'Hello'};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.status == 'success') {
    System.debug('Output: ' + result.output);
}
```

**Throws**:
- `RuleEngineException` - Pipeline configuration error
- `ProviderException` - LLM provider error

---

### continueExecution

```apex
global static ExecutionResult continueExecution(ExecutionState state)
```

Continue execution from a saved state (for async/yielded pipelines).

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | ExecutionState | Saved execution state |

**Returns**: `ExecutionResult` - Execution result

---

## PipelineQueueable

Async pipeline executor using Queueable interface.

### enqueue

```apex
global static String enqueue(String pipelineJson, Map<String, Object> input)
```

Start asynchronous pipeline execution.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `pipelineJson` | String | Pipeline definition as JSON |
| `input` | Map<String, Object> | Pipeline input data |

**Returns**: `String` - Execution ID for tracking

**Example**:
```apex
String executionId = PipelineQueueable.enqueue(pipelineJson, input);
System.debug('Execution ID: ' + executionId);

// Query status later
PipelineExecution__c exec = [
    SELECT Status__c, Progress__c, Output__c
    FROM PipelineExecution__c
    WHERE ExecutionId__c = :executionId
    LIMIT 1
];
```

---

### resume

```apex
global static void resume(String executionId)
```

Resume a yielded execution.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `executionId` | String | Execution ID to resume |

**Throws**:
- `RuleEngineException` - If execution is already completed or failed

---

## ExecutionResult

Result of pipeline execution.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `status` | String | `'success'`, `'error'`, or `'yielded'` |
| `errorMessage` | String | Error details if status is `'error'` |
| `output` | Map<String, Object> | Stage outputs including `_final` |
| `trace` | ExecutionTrace | Debugging and statistics |
| `state` | ExecutionState | State for continuation |

### Accessing Output

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.status == 'success') {
    // Get final output
    Map<String, Object> finalOutput = (Map<String, Object>) result.output.get('_final');
    Map<String, Object> finalResult = (Map<String, Object>) finalOutput.get('result');

    // Access fields
    String category = (String) finalResult.get('category');

    // Access intermediate stage outputs
    Map<String, Object> classifyOutput = (Map<String, Object>) result.output.get('classify');
}
```

---

## ExecutionTrace

Debugging and usage statistics.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `usage` | UsageStats | Token usage and cost |
| `stages` | List<StageTrace> | Per-stage execution details |

### UsageStats

| Property | Type | Description |
|----------|------|-------------|
| `totalInputTokens` | Integer | Total input tokens used |
| `totalOutputTokens` | Integer | Total output tokens used |
| `totalCostUsd` | Decimal | Estimated cost in USD |

### Example

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.trace != null && result.trace.usage != null) {
    System.debug('Input Tokens: ' + result.trace.usage.totalInputTokens);
    System.debug('Output Tokens: ' + result.trace.usage.totalOutputTokens);
    System.debug('Estimated Cost: $' + result.trace.usage.totalCostUsd.setScale(4));
}
```

---

## ExecutionState

Serializable execution state for async/continuation.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `executionId` | String | Unique execution identifier |
| `pipelineJson` | String | Pipeline definition |
| `pipelineName` | String | Pipeline name |
| `input` | Map<String, Object> | Original input |
| `currentStageId` | String | Currently executing stage |
| `completedStages` | Set<String> | Completed stage IDs |
| `totalStages` | Integer | Total number of stages |
| `yieldCount` | Integer | Number of times execution yielded |

### Methods

#### getProgress

```apex
global Integer getProgress()
```

Get execution progress as percentage (0-100).

#### serialize

```apex
global String serialize()
```

Serialize state to JSON string for storage.

#### deserialize

```apex
global static ExecutionState deserialize(String json)
```

Deserialize state from JSON string.

---

## RuleEngineException

Exception thrown for pipeline configuration and execution errors.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | String | Error message |
| `stageId` | String | Stage where error occurred (if applicable) |

### Example

```apex
try {
    ExecutionResult result = PipelineRunner.execute(pipelineJson, input);
} catch (RuleEngineException e) {
    System.debug('Pipeline Error: ' + e.getMessage());
    // Log, notify, or take corrective action
}
```

---

## Custom Metadata Types

### LLMProviderConfig__mdt

LLM provider configuration.

| Field | Type | Description |
|-------|------|-------------|
| `DeveloperName` | String | Unique identifier |
| `Provider__c` | String | Provider type: `anthropic`, `openai` |
| `Endpoint__c` | String | API endpoint URL |
| `Model__c` | String | Model identifier |
| `ApiKey__c` | String | API key (use Named Credentials in production) |
| `MaxTokens__c` | Number | Default max tokens |
| `Temperature__c` | Number | Default temperature |

---

## Platform Events

### PipelineStatus__e

Real-time execution status updates.

| Field | Type | Description |
|-------|------|-------------|
| `ExecutionId__c` | String | Execution identifier |
| `Status__c` | String | Current status |
| `StageId__c` | String | Current stage ID |
| `Progress__c` | Number | Progress percentage (0-100) |
| `Message__c` | String | Status message |

### Subscribing to Events

```apex
// Trigger
trigger PipelineStatusTrigger on PipelineStatus__e (after insert) {
    for (PipelineStatus__e event : Trigger.New) {
        System.debug('Execution ' + event.ExecutionId__c +
            ': ' + event.Status__c + ' (' + event.Progress__c + '%)');
    }
}
```

---

## Custom Objects

### PipelineExecution__c

Async execution tracking record.

| Field | Type | Description |
|-------|------|-------------|
| `ExecutionId__c` | String | Unique execution identifier |
| `PipelineName__c` | String | Pipeline name |
| `Status__c` | String | Pending, Running, Yielded, Completed, Failed |
| `Progress__c` | Number | Progress percentage |
| `CurrentStage__c` | String | Current stage ID |
| `TotalStages__c` | Number | Total stages |
| `CompletedStages__c` | Number | Completed stages |
| `Input__c` | Long Text | Serialized input |
| `Output__c` | Long Text | Serialized output |
| `Context__c` | Long Text | Serialized execution state |
| `ErrorMessage__c` | Long Text | Error details |
| `StartTime__c` | DateTime | Execution start time |
| `EndTime__c` | DateTime | Execution end time |
| `GovernorStats__c` | Long Text | Governor limit usage |

### Query Examples

```apex
// Get execution by ID
PipelineExecution__c exec = [
    SELECT Status__c, Progress__c, Output__c
    FROM PipelineExecution__c
    WHERE ExecutionId__c = :executionId
    LIMIT 1
];

// Get recent executions
List<PipelineExecution__c> recent = [
    SELECT ExecutionId__c, PipelineName__c, Status__c, StartTime__c
    FROM PipelineExecution__c
    ORDER BY StartTime__c DESC
    LIMIT 10
];

// Get failed executions
List<PipelineExecution__c> failed = [
    SELECT ExecutionId__c, PipelineName__c, ErrorMessage__c
    FROM PipelineExecution__c
    WHERE Status__c = 'Failed'
    AND StartTime__c = TODAY
];
```

---

## Governor Limits

### GovernorMonitor

Utility class for monitoring governor limits.

#### getStats

```apex
global static Map<String, Object> getStats()
```

Get current governor limit usage.

**Returns**: Map containing:
- `callouts` - Callouts used / limit
- `cpuTime` - CPU time used / limit
- `heapSize` - Heap used / limit
- `queries` - SOQL queries used / limit

---

## Version Information

| Version | API Version | Release Date |
|---------|-------------|--------------|
| 1.0.0 | 62.0 | Coming Soon |

---

## Support

- **Documentation**: [flowmason.dev/docs/salesforce](https://flowmason.dev/docs/salesforce)
- **Issues**: [github.com/flowmason/salesforce/issues](https://github.com/flowmason/salesforce/issues)
- **Community**: [discord.gg/flowmason](https://discord.gg/flowmason)
