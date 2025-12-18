# Error & Resilience Checklist

## 5.1 Timeout Testing

### Default Timeouts
- [ ] Node default timeout (60s): Triggers on slow response
- [ ] Operator default timeout (30s): Triggers appropriately

### Custom Timeouts
- [ ] Custom timeout_ms: Overrides default
- [ ] Very short timeout (100ms): Immediate timeout
- [ ] Timeout during streaming

### Error Behavior
- [ ] Timeout error type: TIMEOUT
- [ ] Timeout is retryable (retry logic kicks in)

---

## 5.2 Retry Logic

### Backoff Behavior
- [ ] Default max_retries (3): Retries 3 times
- [ ] Exponential backoff: Delays increase
- [ ] Jitter: Delays vary slightly
- [ ] max_delay ceiling: Backoff doesn't exceed

### Retryable Errors
- [ ] TIMEOUT: Retried
- [ ] CONNECTIVITY: Retried
- [ ] RATE_LIMIT: Retried

### Non-Retryable Errors
- [ ] VALIDATION: Not retried
- [ ] SECURITY: Not retried

### Final State
- [ ] RetryExhaustedError: After all retries fail
- [ ] Retry statistics in results

---

## 5.3 Cancellation

### Cancel Methods
- [ ] Cancel via API: Execution stops
- [ ] Cancel via UI: Stop button works

### Cancellation Behavior
- [ ] Cancellation reason captured
- [ ] CancellationError raised
- [ ] In-progress stages: Cancelled or completed
- [ ] Pending stages: Not started

### Complex Scenarios
- [ ] Cleanup runs on cancellation
- [ ] Cancel during foreach: Loop stops

---

## 5.4 Error Classification

### Error Types
- [ ] CONNECTIVITY: Network/provider unavailable
- [ ] TIMEOUT: Execution time exceeded
- [ ] VALIDATION: Schema mismatch
- [ ] EXPRESSION: JMESPath/template error
- [ ] TRANSFORMATION: Data transform failure
- [ ] EXECUTION: Generic component error
- [ ] ROUTING: Missing dependencies
- [ ] SECURITY: Auth/API key failure
- [ ] RETRY_EXHAUSTED: All retries failed
- [ ] CONTROL_FLOW: Control flow logic error
- [ ] UNKNOWN: Unclassified error

### Severity Levels
- [ ] CRITICAL: Appropriate for fatal errors
- [ ] ERROR: Appropriate for stage failures
- [ ] WARNING: Appropriate for non-fatal issues
- [ ] INFO: Appropriate for informational

### Error Context
- [ ] component_id tracked
- [ ] cause exception chained
- [ ] details dictionary populated

---

## 5.5 Invalid Input

### Missing Data
- [ ] Missing required field: Validation error
- [ ] Empty string where required: Handled

### Type Mismatches
- [ ] Wrong type: Type error shown
- [ ] Null where not nullable: Error
- [ ] Array instead of object: Error

### Format Issues
- [ ] Extra fields: Handled appropriately
- [ ] Malformed JSON: Clear error

---

## Summary

| Area | Tests | Passed |
|------|-------|--------|
| Timeout | 7 | ___ |
| Retry | 12 | ___ |
| Cancellation | 8 | ___ |
| Error Classification | 18 | ___ |
| Invalid Input | 7 | ___ |
| **Total** | **52** | ___ |
