# Project 02: Control Flow Mastery

Exhaustive testing of all 6 control flow mechanisms in FlowMason.

## Purpose
Test every control flow type with various configurations and edge cases:
1. **Conditional** - If/else branching
2. **Router** - Switch/case routing
3. **ForEach** - Loop iteration (sequential & parallel)
4. **TryCatch** - Error handling with recovery
5. **SubPipeline** - Nested pipeline execution
6. **Return** - Early exit from pipeline

## Time Required
~2 hours

## Prerequisites
- FlowMason Studio running
- At least one LLM provider configured
- Understanding of JMESPath expressions

## Control Flow Types

### 2.1 Conditional (If/Else)
Branching based on boolean conditions.

**Pipelines:**
- `conditional_basic.json` - Simple true/false
- `conditional_complex.json` - Nested conditions
- `conditional_edge_cases.json` - Null, empty values

**Key Tests:**
- True branch executes, false skipped
- Condition referencing upstream output
- Boolean coercion

### 2.2 Router (Switch/Case)
Multi-way branching based on value matching.

**Pipelines:**
- `router_basic.json` - 3-way routing
- `router_default.json` - Default branch
- `router_many_branches.json` - 10+ branches

**Key Tests:**
- Correct branch selected
- Default when no match
- Case sensitivity

### 2.3 ForEach (Loop)
Iterate over arrays with sequential or parallel execution.

**Pipelines:**
- `foreach_sequential.json` - Items in order
- `foreach_parallel.json` - Concurrent processing
- `foreach_nested.json` - Loop inside loop
- `foreach_error_handling.json` - break_on_error behavior

**Key Tests:**
- Loop variables (item, index, loop_total)
- Parallel concurrency limits
- Empty array handling
- Error continuation

### 2.4 TryCatch (Error Handling)
Graceful error handling with recovery.

**Pipelines:**
- `trycatch_success.json` - No error path
- `trycatch_catch.json` - Error caught
- `trycatch_finally.json` - Finally block
- `trycatch_propagate.json` - Error re-raised

**Key Tests:**
- Error context in catch block
- Finally always executes
- Error scope modes

### 2.5 SubPipeline (Nested)
Call another pipeline as a step.

**Pipelines:**
- `subpipeline_basic.json` - Simple nested call
- `subpipeline_timeout.json` - Timeout handling
- `subpipeline_error.json` - Error modes
- `child_pipeline.json` - The called pipeline

**Key Tests:**
- Input/output mapping
- Timeout behavior
- on_error modes

### 2.6 Return (Early Exit)
Stop pipeline execution and return a value.

**Pipelines:**
- `return_success.json` - Early exit
- `return_conditional.json` - Return in branch
- `return_in_loop.json` - Return from foreach

**Key Tests:**
- Subsequent stages skipped
- Return value captured
- Loop interruption

## How to Test

1. Import each pipeline into Studio
2. Execute with provided inputs
3. Verify behavior matches expected outcomes
4. Check CHECKLIST.md items as you go
5. Document any issues in NOTES.md

## Success Criteria
All 60 test cases in CHECKLIST.md should pass.
