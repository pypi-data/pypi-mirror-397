# Project 01: Smoke Test

Quick validation that the entire FlowMason system is working before deep testing.

## Purpose
Verify basic functionality:
- Studio starts and loads
- Components are available
- Pipelines can be created, executed, saved, and deleted
- At least one LLM provider is configured and working

## Time Required
~15 minutes

## Prerequisites
- FlowMason Studio running at http://localhost:8999
- At least one LLM provider configured with API key

## Pipelines

### 1. hello_world.json
Single generator node that produces a simple greeting.
- **Input:** A topic to greet about
- **Expected:** A friendly greeting message

### 2. two_stage.json
Two-stage pipeline: Generator → Critic
- **Input:** A topic for content
- **Expected:** Generated content with critique feedback

## How to Test

### Via Studio UI
1. Open http://localhost:8999
2. Verify the UI loads without errors
3. Go to Pipelines page
4. Click "Create Pipeline"
5. Import `hello_world.json`
6. In execution panel, paste input from `inputs/hello_input.json`
7. Click Execute
8. Verify output matches structure in `expected/hello_output.json`

### Via CLI
```bash
cd /Users/sam/Documents/CCAT/flow/flowmason
flowmason run manualtesting/01_smoke_test/pipelines/hello_world.json \
  --input-file manualtesting/01_smoke_test/inputs/hello_input.json
```

## Success Criteria
All items in CHECKLIST.md should pass before proceeding to other projects.

## If Tests Fail
1. Check Studio logs (Settings → Logs)
2. Verify provider API key is configured
3. Check network connectivity
4. Restart Studio and try again
