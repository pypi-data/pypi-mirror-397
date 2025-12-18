# Error & Resilience Notes

## Error Type Reference

| Type | Retryable | Typical Cause |
|------|-----------|---------------|
| CONNECTIVITY | Yes | Network issues, provider down |
| TIMEOUT | Yes | Slow response, large payload |
| VALIDATION | No | Schema mismatch, wrong type |
| EXPRESSION | No | Bad JMESPath, template error |
| TRANSFORMATION | No | Data conversion failure |
| EXECUTION | No | Component logic error |
| ROUTING | No | Missing dependency |
| SECURITY | No | Auth failure, bad API key |
| RETRY_EXHAUSTED | No | All retries failed |
| CONTROL_FLOW | No | Bad condition, loop error |
| UNKNOWN | No | Unclassified |

## Retry Formula

```
delay = min(initial_delay * (multiplier ^ attempt) + jitter, max_delay)
```

Default values:
- initial_delay: 1000ms
- multiplier: 2
- max_delay: 30000ms
- jitter: random(0, 1000)ms

## Issues Found

<!-- Add issues here -->
