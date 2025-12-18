# Getting Started

Create and run your first AI pipeline in Salesforce in 5 minutes.

## Your First Pipeline

### Step 1: Create a Simple Pipeline

Open Developer Console (or VS Code with Salesforce extensions) and run this anonymous Apex:

```apex
// Simple greeting pipeline
String pipelineJson = '{' +
    '"name": "Hello Pipeline",' +
    '"stages": [' +
        '{' +
            '"id": "greet",' +
            '"component_type": "json_transform",' +
            '"config": {' +
                '"data": {' +
                    '"greeting": "Hello, {{input.name}}!",' +
                    '"timestamp": "{{input.timestamp}}"' +
                '},' +
                '"jmespath_expression": "@"' +
            '},' +
            '"depends_on": []' +
        '}' +
    '],' +
    '"output_stage_id": "greet"' +
'}';

// Execute with input
Map<String, Object> input = new Map<String, Object>{
    'name' => 'World',
    'timestamp' => String.valueOf(DateTime.now())
};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

System.debug('Status: ' + result.status);
System.debug('Output: ' + JSON.serializePretty(result.output));
```

**Output**:
```json
{
  "_final": {
    "result": {
      "greeting": "Hello, World!",
      "timestamp": "2025-12-14 10:30:00"
    }
  }
}
```

### Step 2: Add AI Generation

Now let's add an AI component that generates a personalized message:

```apex
String pipelineJson = '{' +
    '"name": "AI Greeting Pipeline",' +
    '"stages": [' +
        '{' +
            '"id": "generate",' +
            '"component_type": "generator",' +
            '"config": {' +
                '"system_prompt": "You are a friendly assistant.",' +
                '"prompt": "Write a brief, warm greeting for {{input.name}} who works as a {{input.role}}.",' +
                '"max_tokens": 100,' +
                '"temperature": 0.7' +
            '},' +
            '"depends_on": []' +
        '},' +
        '{' +
            '"id": "format",' +
            '"component_type": "json_transform",' +
            '"config": {' +
                '"data": {' +
                    '"name": "{{input.name}}",' +
                    '"message": "{{upstream.generate.content}}"' +
                '},' +
                '"jmespath_expression": "@"' +
            '},' +
            '"depends_on": ["generate"]' +
        '}' +
    '],' +
    '"output_stage_id": "format"' +
'}';

Map<String, Object> input = new Map<String, Object>{
    'name' => 'Sarah',
    'role' => 'Software Engineer'
};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.status == 'success') {
    Map<String, Object> output = (Map<String, Object>) result.output.get('_final');
    Map<String, Object> finalResult = (Map<String, Object>) output.get('result');
    System.debug('Generated message: ' + finalResult.get('message'));
}
```

**Sample Output**:
```
Generated message: Hello Sarah! It's wonderful to connect with a fellow
Software Engineer. May your code compile on the first try and your bugs
be easy to squash today!
```

## Understanding the Pipeline Structure

Every pipeline has three main parts:

```json
{
  "name": "Pipeline Name",
  "stages": [
    {
      "id": "unique-stage-id",
      "component_type": "generator|json_transform|...",
      "config": { ... },
      "depends_on": ["previous-stage-id"]
    }
  ],
  "output_stage_id": "final-stage-id"
}
```

### Stage Dependencies

Stages declare dependencies via `depends_on`. The engine executes stages in dependency order:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Stage A │────→│ Stage B │────→│ Stage C │
│         │     │         │     │ (output)│
└─────────┘     └─────────┘     └─────────┘
```

Parallel execution when no dependencies:

```
┌─────────┐
│ Stage A │───┐
└─────────┘   │     ┌─────────┐
              ├────→│ Stage D │
┌─────────┐   │     │ (output)│
│ Stage B │───┤     └─────────┘
└─────────┘   │
              │
┌─────────┐   │
│ Stage C │───┘
└─────────┘
```

### Template Syntax

Reference data using `{{...}}` expressions:

| Expression | Description | Example |
|------------|-------------|---------|
| `{{input.field}}` | Pipeline input | `{{input.name}}` |
| `{{upstream.stageId.field}}` | Previous stage output | `{{upstream.generate.content}}` |
| `{{context.var}}` | Loop context variable | `{{context.current_item}}` |

## Check Execution Statistics

Access token usage and cost information:

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.trace != null && result.trace.usage != null) {
    System.debug('Input Tokens: ' + result.trace.usage.totalInputTokens);
    System.debug('Output Tokens: ' + result.trace.usage.totalOutputTokens);
    System.debug('Estimated Cost: $' + result.trace.usage.totalCostUsd);
}
```

## Error Handling

Check for errors in the result:

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.status == 'success') {
    // Process output
    System.debug('Success: ' + result.output);
} else if (result.status == 'error') {
    // Handle error
    System.debug('Error: ' + result.errorMessage);
}
```

## Next Steps

- [Development Workflow](03-development-workflow.md) - Set up local development
- [Pipeline Definition](04-pipeline-definition.md) - Complete JSON reference
- [Components](05-components.md) - Available component types
- [Examples](09-examples.md) - Complete pipeline examples
