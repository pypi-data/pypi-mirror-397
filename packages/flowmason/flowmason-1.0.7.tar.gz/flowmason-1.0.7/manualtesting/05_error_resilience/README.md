# Project 05: Error & Resilience

Exhaustive testing of failure modes and recovery mechanisms.

## Purpose
Test FlowMason's resilience:
- Timeout handling
- Retry logic with exponential backoff
- Cancellation support
- Error classification
- Invalid input handling

## Time Required
~1.5 hours

## Test Areas

### 5.1 Timeout Testing
- Node default timeout (60s)
- Operator default timeout (30s)
- Custom timeout values

### 5.2 Retry Logic
- Exponential backoff
- Jitter
- Max retries
- Retryable vs non-retryable errors

### 5.3 Cancellation
- Cancel via API
- Cancel via UI
- Cancel during loops

### 5.4 Error Classification
- 11 error types
- 4 severity levels
- Error context preservation

### 5.5 Invalid Input
- Missing fields
- Wrong types
- Malformed JSON

## Notes
Some tests require simulating failures - use test endpoints or invalid configs.
