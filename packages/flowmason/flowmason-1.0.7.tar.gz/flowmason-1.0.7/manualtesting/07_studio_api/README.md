# Project 07: Studio API

Exhaustive testing of all Studio API endpoints.

## Purpose
Test every REST API endpoint:
- Pipeline CRUD
- Execution endpoints
- Settings & Providers
- Templates & Registry
- Analytics & Logs
- Error responses

## Time Required
~2 hours

## Prerequisites
- Studio backend running at http://localhost:8999
- API client (curl, httpie, Postman, or Bruno)
- Some pipelines created for testing

## Testing Tools

### curl Examples
```bash
# List pipelines
curl http://localhost:8999/api/v1/pipelines

# Create pipeline
curl -X POST http://localhost:8999/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "stages": {}}'

# Execute pipeline
curl -X POST http://localhost:8999/api/v1/pipelines/{id}/run \
  -H "Content-Type: application/json" \
  -d '{"input": {}}'
```

### httpie Examples
```bash
http GET localhost:8999/api/v1/pipelines
http POST localhost:8999/api/v1/pipelines name=test stages:='{}'
```

## API Base URL
`http://localhost:8999/api/v1`

## Endpoints Covered
See CHECKLIST.md for complete list of endpoints to test.
