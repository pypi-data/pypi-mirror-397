# Execution

Flowmason supports both synchronous and asynchronous pipeline execution in Salesforce.

## Synchronous Execution

Execute pipelines in the current transaction context.

### Basic Execution

```apex
String pipelineJson = '{"name":"My Pipeline",...}';
Map<String, Object> input = new Map<String, Object>{
    'message' => 'Hello World'
};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.status == 'success') {
    System.debug('Output: ' + result.output);
} else {
    System.debug('Error: ' + result.errorMessage);
}
```

### ExecutionResult Structure

```apex
public class ExecutionResult {
    public String status;           // 'success', 'error', 'yielded'
    public String errorMessage;     // Error details if failed
    public Map<String, Object> output;  // Stage outputs
    public ExecutionTrace trace;    // Debugging information
    public ExecutionState state;    // For continuation (async)
}
```

### Accessing Output

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

// Get final output
Map<String, Object> finalOutput = (Map<String, Object>) result.output.get('_final');
Map<String, Object> finalResult = (Map<String, Object>) finalOutput.get('result');

// Access specific fields
String category = (String) finalResult.get('category');
String priority = (String) finalResult.get('priority');
```

### Execution Statistics

```apex
if (result.trace != null && result.trace.usage != null) {
    System.debug('Input Tokens: ' + result.trace.usage.totalInputTokens);
    System.debug('Output Tokens: ' + result.trace.usage.totalOutputTokens);
    System.debug('Estimated Cost: $' + result.trace.usage.totalCostUsd);
}
```

---

## Asynchronous Execution

For long-running pipelines, use async execution with Queueable.

### Start Async Execution

```apex
String pipelineJson = '{"name":"Long Running Pipeline",...}';
Map<String, Object> input = new Map<String, Object>{'data' => 'large dataset'};

// Returns execution ID immediately
String executionId = PipelineQueueable.enqueue(pipelineJson, input);
System.debug('Execution ID: ' + executionId);
```

### Check Execution Status

```apex
// Query the execution record
PipelineExecution__c exec = [
    SELECT Status__c, Progress__c, CurrentStage__c, ErrorMessage__c
    FROM PipelineExecution__c
    WHERE ExecutionId__c = :executionId
    LIMIT 1
];

System.debug('Status: ' + exec.Status__c);
System.debug('Progress: ' + exec.Progress__c + '%');
System.debug('Current Stage: ' + exec.CurrentStage__c);
```

### Get Completed Results

```apex
PipelineExecution__c exec = [
    SELECT Status__c, Output__c
    FROM PipelineExecution__c
    WHERE ExecutionId__c = :executionId
    LIMIT 1
];

if (exec.Status__c == 'Completed') {
    Map<String, Object> output = (Map<String, Object>) JSON.deserializeUntyped(exec.Output__c);
    System.debug('Output: ' + output);
}
```

### Platform Events for Real-Time Updates

Subscribe to `PipelineStatus__e` for real-time status updates:

```apex
// In a trigger or Platform Event subscriber
trigger PipelineStatusTrigger on PipelineStatus__e (after insert) {
    for (PipelineStatus__e event : Trigger.New) {
        System.debug('Execution: ' + event.ExecutionId__c);
        System.debug('Status: ' + event.Status__c);
        System.debug('Progress: ' + event.Progress__c + '%');
        System.debug('Message: ' + event.Message__c);
    }
}
```

---

## Governor Limits Management

Flowmason automatically manages governor limits during execution.

### Limit Monitoring

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

// Check governor usage
System.debug('Callouts: ' + Limits.getCallouts() + '/' + Limits.getLimitCallouts());
System.debug('CPU Time: ' + Limits.getCpuTime() + '/' + Limits.getLimitCpuTime() + 'ms');
System.debug('Heap Size: ' + Limits.getHeapSize() + '/' + Limits.getLimitHeapSize());
```

### Automatic Yielding

When governor limits approach thresholds, async execution yields and chains:

```apex
// Pipeline automatically yields when limits are near
if (result.status == 'yielded') {
    System.debug('Pipeline yielded - will continue in next transaction');
    // The Queueable automatically chains to continue execution
}
```

### Governor Limit Thresholds

| Resource | Threshold | Action |
|----------|-----------|--------|
| Callouts | 80% of limit | Yield and chain |
| CPU Time | 80% of limit | Yield and chain |
| Heap Size | 80% of limit | Yield and chain |

---

## Execution Contexts

### From Trigger

```apex
trigger CaseTrigger on Case (after insert) {
    String pipelineJson = getPipelineFromStaticResource();

    for (Case c : Trigger.New) {
        Map<String, Object> input = new Map<String, Object>{
            'subject' => c.Subject,
            'description' => c.Description,
            'caseId' => c.Id
        };

        // Use async for trigger context (recommended)
        String executionId = PipelineQueueable.enqueue(pipelineJson, input);
    }
}
```

### From LWC (via Apex)

```apex
@AuraEnabled
public static Map<String, Object> runTriagePipeline(String subject, String description) {
    String pipelineJson = getPipelineFromStaticResource();

    Map<String, Object> input = new Map<String, Object>{
        'subject' => subject,
        'description' => description
    };

    ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

    if (result.status == 'success') {
        Map<String, Object> output = (Map<String, Object>) result.output.get('_final');
        return (Map<String, Object>) output.get('result');
    } else {
        throw new AuraHandledException(result.errorMessage);
    }
}
```

### From Flow (Invocable)

```apex
public class FlowPipelineRunner {
    @InvocableMethod(label='Run Pipeline' description='Execute a Flowmason pipeline')
    public static List<String> runPipeline(List<PipelineInput> inputs) {
        List<String> results = new List<String>();

        for (PipelineInput input : inputs) {
            ExecutionResult result = PipelineRunner.execute(
                input.pipelineJson,
                (Map<String, Object>) JSON.deserializeUntyped(input.inputJson)
            );
            results.add(JSON.serialize(result.output));
        }

        return results;
    }

    public class PipelineInput {
        @InvocableVariable(required=true)
        public String pipelineJson;

        @InvocableVariable(required=true)
        public String inputJson;
    }
}
```

### From Batch Apex

```apex
public class PipelineBatch implements Database.Batchable<SObject>, Database.AllowsCallouts {
    private String pipelineJson;

    public PipelineBatch(String pipelineJson) {
        this.pipelineJson = pipelineJson;
    }

    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator('SELECT Id, Subject, Description FROM Case WHERE Status = \'New\'');
    }

    public void execute(Database.BatchableContext bc, List<Case> cases) {
        for (Case c : cases) {
            Map<String, Object> input = new Map<String, Object>{
                'subject' => c.Subject,
                'description' => c.Description
            };

            ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

            if (result.status == 'success') {
                // Update case with results
                Map<String, Object> output = (Map<String, Object>) result.output.get('_final');
                // ... process output
            }
        }
    }

    public void finish(Database.BatchableContext bc) {
        System.debug('Batch complete');
    }
}
```

---

## Error Handling

### Handling Execution Errors

```apex
try {
    ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

    if (result.status == 'error') {
        // Pipeline execution error
        System.debug('Pipeline Error: ' + result.errorMessage);
        // Log, notify, or take corrective action
    }
} catch (RuleEngineException e) {
    // Configuration or system error
    System.debug('System Error: ' + e.getMessage());
} catch (Exception e) {
    // Unexpected error
    System.debug('Unexpected Error: ' + e.getMessage());
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Unauthorized endpoint` | Missing Remote Site Setting | Add endpoint to Remote Site Settings |
| `Invalid template` | Malformed `{{...}}` expression | Check template syntax |
| `Stage not found` | Invalid `depends_on` reference | Verify stage IDs |
| `Callout limit exceeded` | Too many LLM calls | Use async execution or reduce calls |

## Next Steps

- [Providers](07-providers.md) - Configure LLM providers
- [Integration Patterns](08-integration-patterns.md) - Triggers, LWC, Flows
- [Examples](09-examples.md) - Complete pipeline examples
