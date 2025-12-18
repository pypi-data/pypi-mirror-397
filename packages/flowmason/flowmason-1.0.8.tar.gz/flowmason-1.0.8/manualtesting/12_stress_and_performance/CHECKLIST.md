# Stress & Performance Checklist

## 12.1 Large Batch Processing

### Sequential
- [ ] 100 items sequential: Completes successfully
- [ ] 500 items: Memory usage reasonable
- [ ] 1000 items: No timeout, completes

### Parallel
- [ ] 100 items parallel (max=10): Faster than sequential
- [ ] Progress updates during long batch

---

## 12.2 Long-Running Pipelines

- [ ] 10-minute pipeline: Completes
- [ ] 30-minute pipeline: Completes
- [ ] Connection stays alive (WebSocket)
- [ ] Progress visible in UI
- [ ] Can cancel long-running pipeline

---

## 12.3 Concurrent Executions

- [ ] 5 pipelines simultaneously: All complete
- [ ] 10 pipelines simultaneously: All complete
- [ ] 20 pipelines simultaneously: Graceful handling
- [ ] Resource usage acceptable
- [ ] No cross-contamination of results

---

## 12.4 Large Payloads

- [ ] 1MB input JSON: Accepted
- [ ] 10MB input JSON: Handled
- [ ] 100KB stage output: Stored correctly
- [ ] Large LLM response (4000+ tokens): Captured
- [ ] Binary data handling (base64 images)

---

## 12.5 Memory & Resource Limits

- [ ] Pipeline with 50 stages: Executes
- [ ] Pipeline with 100 stages: Executes
- [ ] Deep nesting (10 levels): Works
- [ ] Circular dependency detection: Caught
- [ ] Memory leak check (run 100 times): No leak

---

## 12.6 Provider Rate Limits

- [ ] Hit Anthropic rate limit: Retry works
- [ ] Hit OpenAI rate limit: Retry works
- [ ] Concurrent calls respect limits
- [ ] Rate limit error message clear

---

## Performance Benchmarks

Record actual values:

| Test | Duration | Memory | Notes |
|------|----------|--------|-------|
| 100 items seq | | | |
| 100 items par | | | |
| 1000 items | | | |
| 50 stages | | | |
| 100 stages | | | |

---

## Summary

| Area | Tests | Passed |
|------|-------|--------|
| Batch Processing | 5 | ___ |
| Long-Running | 5 | ___ |
| Concurrent | 5 | ___ |
| Large Payloads | 5 | ___ |
| Resource Limits | 5 | ___ |
| Rate Limits | 4 | ___ |
| **Total** | **29** | ___ |
