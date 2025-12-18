# Control Flow Mastery Checklist

## 2.1 Conditional (If/Else)

### Basic Behavior
- [ ] True branch executes, false branch skipped
- [ ] False branch executes, true branch skipped
- [ ] Nested conditionals (if inside if)
- [ ] Condition with complex JMESPath expression

### Edge Cases
- [ ] Condition referencing upstream output
- [ ] Empty condition value handling
- [ ] Null input handling
- [ ] Boolean coercion (strings "true"/"false")

---

## 2.2 Router (Switch/Case)

### Basic Behavior
- [ ] Routes to correct branch based on value
- [ ] Default branch when no match
- [ ] Case-sensitive matching works

### Value Types
- [ ] Numeric routing values
- [ ] String routing values
- [ ] Empty string routing
- [ ] Null value routing (→ default)

### Scale
- [ ] Many branches (10+) performance acceptable

---

## 2.3 ForEach (Loop)

### Sequential Execution
- [ ] Items processed in order
- [ ] Results collected correctly
- [ ] Duration reflects sequential timing

### Parallel Execution
- [ ] max_parallel=3 limits concurrency
- [ ] max_parallel=1 (effectively sequential)
- [ ] All items processed (order may vary)
- [ ] Duration reflects parallel speedup

### Loop Variables
- [ ] `item` contains current item
- [ ] `index` contains current position (0-based)
- [ ] `loop_total` shows total item count
- [ ] `loop_remaining` shows remaining count
- [ ] `loop_results` accumulates as loop progresses
- [ ] Custom item_variable and index_variable names work

### Edge Cases
- [ ] Empty array: No iterations, empty results
- [ ] Single item array: One iteration
- [ ] Large array (100 items): All processed

### Error Handling
- [ ] break_on_error=true: Stops on first error
- [ ] break_on_error=false: Continues, collects errors

### Nesting
- [ ] Nested foreach: Inner loop per outer item

---

## 2.4 TryCatch (Error Handling)

### Success Path
- [ ] Try block completes successfully
- [ ] Catch block skipped when no error
- [ ] Finally runs after success

### Error Path
- [ ] Catch block receives error context
- [ ] error_message available in catch
- [ ] error_type available in catch
- [ ] error_occurred flag set correctly

### Finally Behavior
- [ ] Finally runs after success
- [ ] Finally runs after catch
- [ ] Finally runs even if catch throws

### Error Scope
- [ ] error_scope="continue": Swallows error
- [ ] error_scope="propagate": Re-raises after catch

### Filtering
- [ ] catch_error_types filter: Only catches specified types

### Nesting
- [ ] Nested try-catch: Inner catches before outer

### Multiple Errors
- [ ] Multiple errors in try: First error triggers catch

---

## 2.5 SubPipeline (Nested Execution)

### Basic Execution
- [ ] Child pipeline executes with inputs
- [ ] Input mapping: Data passed correctly
- [ ] Output mapping: Results available in parent

### Timeout
- [ ] timeout_ms triggers timeout error when exceeded

### Error Handling
- [ ] on_error="propagate": Child error bubbles up
- [ ] on_error="default": default_result used on failure
- [ ] on_error="ignore": Failure ignored, continues

### Edge Cases
- [ ] Non-existent pipeline: Appropriate error message
- [ ] Recursive call (A calls A): Max depth protection

---

## 2.6 Return (Early Exit)

### Basic Behavior
- [ ] Return stops pipeline execution immediately
- [ ] Return value becomes pipeline output
- [ ] Return message captured in results
- [ ] Stages after return are skipped

### Conditional Return
- [ ] Return in conditional: Only exits if branch taken
- [ ] Return in false branch: Continues if true taken

### Loop Return
- [ ] Return in foreach: Exits entire pipeline (not just loop)

---

## Summary

| Section | Tests | Passed |
|---------|-------|--------|
| Conditional | 8 | ___ |
| Router | 8 | ___ |
| ForEach | 14 | ___ |
| TryCatch | 13 | ___ |
| SubPipeline | 9 | ___ |
| Return | 7 | ___ |
| **Total** | **59** | ___ |

---

**Tester:** _________________
**Date:** _________________
**Overall Status:** _________________
