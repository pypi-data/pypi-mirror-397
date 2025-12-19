# Development Workflow

Flowmason enables a **local-first development** workflow that dramatically speeds up pipeline development and testing.

## The Power of Local Development

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL-FIRST DEVELOPMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DEVELOP LOCALLY                                              │
│     $ fm run pipeline.json --input data.json                     │
│     • Instant feedback (no deployment wait)                      │
│     • Full debugging with breakpoints                            │
│     • Iterate in seconds, not minutes                            │
│                                                                  │
│  2. DEPLOY JSON TO SALESFORCE                                    │
│     • Same JSON works identically in Salesforce                  │
│     • Store in Static Resource or Custom Metadata                │
│     • No code changes needed                                     │
│                                                                  │
│  3. RUN IN PRODUCTION                                            │
│     ExecutionResult result = PipelineRunner.execute(             │
│         pipelineJson,                                            │
│         input                                                    │
│     );                                                           │
│     • Triggers, LWC, Flows, Batch Apex                          │
│     • Same pipeline, same results                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Install Flowmason CLI

First, install the Flowmason CLI for local development:

```bash
# Using npm
npm install -g flowmason

# Or using pip
pip install flowmason

# Verify installation
fm --version
```

## Create a Pipeline File

Create `support-triage.pipeline.json`:

```json
{
  "name": "Support Ticket Triage",
  "stages": [
    {
      "id": "classify",
      "component_type": "generator",
      "config": {
        "system_prompt": "Classify support tickets. Output JSON with category (billing/technical/account) and priority (low/medium/high).",
        "prompt": "Classify this ticket:\n\nSubject: {{input.subject}}\nDescription: {{input.description}}",
        "max_tokens": 100,
        "temperature": 0.1
      },
      "depends_on": []
    },
    {
      "id": "parse",
      "component_type": "json_transform",
      "config": {
        "data": "{{upstream.classify.content}}",
        "jmespath_expression": "@"
      },
      "depends_on": ["classify"]
    }
  ],
  "output_stage_id": "parse"
}
```

Create `test-input.json`:

```json
{
  "subject": "Cannot login to my account",
  "description": "I've been trying to login for 2 hours but keep getting an error. This is urgent as I need to submit a report by EOD."
}
```

## Test Locally

Run the pipeline locally:

```bash
fm run support-triage.pipeline.json --input test-input.json
```

**Output**:
```
✓ Stage: classify (2.3s)
✓ Stage: parse (0.01s)

Output:
{
  "category": "account",
  "priority": "high"
}

Statistics:
  Stages: 2
  LLM Calls: 1
  Tokens: 180
  Cost: $0.002
```

## Debug Mode

Run with verbose debugging:

```bash
fm run support-triage.pipeline.json --input test-input.json --debug
```

This shows:
- Template resolution for each stage
- Full LLM prompts and responses
- Timing for each operation
- Memory and token usage

## Deploy to Salesforce

### Option 1: Static Resource

1. Create a Static Resource in Salesforce:
   - Name: `SupportTriagePipeline`
   - Content: Your pipeline JSON file
   - Cache Control: Public

2. Load and execute in Apex:

```apex
StaticResource sr = [
    SELECT Body
    FROM StaticResource
    WHERE Name = 'SupportTriagePipeline'
    LIMIT 1
];
String pipelineJson = sr.Body.toString();

Map<String, Object> input = new Map<String, Object>{
    'subject' => caseRecord.Subject,
    'description' => caseRecord.Description
};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);
```

### Option 2: Custom Metadata

Store pipeline JSON in Custom Metadata for versioning and environment management:

1. Create Custom Metadata Type `Pipeline__mdt` with a `Definition__c` Long Text field
2. Create records for each pipeline
3. Load and execute:

```apex
Pipeline__mdt pipeline = [
    SELECT Definition__c
    FROM Pipeline__mdt
    WHERE DeveloperName = 'Support_Triage'
    LIMIT 1
];

ExecutionResult result = PipelineRunner.execute(
    pipeline.Definition__c,
    input
);
```

### Option 3: Inline in Apex

For simple pipelines, define inline:

```apex
String pipelineJson = '{"name":"Quick Pipeline",...}';
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);
```

## Development Best Practices

### 1. Use Version Control

Keep pipeline JSON files in Git:

```
my-salesforce-project/
├── force-app/
│   └── main/
│       └── default/
│           └── staticresources/
│               ├── SupportTriagePipeline.json
│               └── ContentGeneratorPipeline.json
├── pipelines/
│   ├── support-triage.pipeline.json
│   └── content-generator.pipeline.json
└── test-inputs/
    ├── support-ticket.json
    └── product-data.json
```

### 2. Create Test Fixtures

Build a library of test inputs:

```bash
# Test different scenarios
fm run support-triage.pipeline.json --input test-inputs/billing-issue.json
fm run support-triage.pipeline.json --input test-inputs/technical-bug.json
fm run support-triage.pipeline.json --input test-inputs/urgent-escalation.json
```

### 3. Compare Local vs Salesforce

Verify identical behavior:

```bash
# Local execution
fm run pipeline.json --input data.json > local-output.json

# Salesforce execution (via sfdx)
sfdx force:apex:execute -f run-pipeline.apex > sf-output.json

# Compare outputs
diff local-output.json sf-output.json
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Pipeline Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Flowmason
        run: npm install -g flowmason

      - name: Test Pipelines
        run: |
          fm run pipelines/support-triage.pipeline.json \
            --input test-inputs/billing-issue.json \
            --assert-output '{"category": "billing"}'

          fm run pipelines/content-generator.pipeline.json \
            --input test-inputs/product.json \
            --assert-success

      - name: Deploy to Salesforce
        if: github.ref == 'refs/heads/main'
        run: sfdx force:source:deploy -p force-app
```

## Next Steps

- [Pipeline Definition](04-pipeline-definition.md) - Complete JSON reference
- [Components](05-components.md) - Available component types
- [Integration Patterns](08-integration-patterns.md) - Triggers, LWC, Flows
