# Studio API Checklist

## 7.1 Pipeline Endpoints

### CRUD
- [ ] POST /api/v1/pipelines - Create pipeline
- [ ] GET /api/v1/pipelines - List with pagination
- [ ] GET /api/v1/pipelines - Filter by category
- [ ] GET /api/v1/pipelines - Filter by tags
- [ ] GET /api/v1/pipelines - Filter by status
- [ ] GET /api/v1/pipelines/{id} - Get single
- [ ] GET /api/v1/pipelines/by-name/{name} - Get by name
- [ ] PUT /api/v1/pipelines/{id} - Update
- [ ] DELETE /api/v1/pipelines/{id} - Delete

### Actions
- [ ] POST /api/v1/pipelines/{id}/validate - Validate
- [ ] POST /api/v1/pipelines/{id}/clone - Clone
- [ ] POST /api/v1/pipelines/{id}/test - Test run
- [ ] POST /api/v1/pipelines/{id}/publish - Publish
- [ ] POST /api/v1/pipelines/{id}/unpublish - Unpublish

---

## 7.2 Execution Endpoints

### Run Management
- [ ] POST /api/v1/pipelines/{id}/run - Execute
- [ ] POST /api/v1/debug/run - Debug execution
- [ ] GET /api/v1/runs - List runs
- [ ] GET /api/v1/runs/{id} - Get run details
- [ ] DELETE /api/v1/runs/{id} - Cancel run

### Debug Controls
- [ ] POST /api/v1/runs/{id}/breakpoints - Set breakpoints
- [ ] PUT /api/v1/runs/{id}/pause - Pause
- [ ] PUT /api/v1/runs/{id}/resume - Resume
- [ ] POST /api/v1/runs/{id}/step - Step execution

### Real-time
- [ ] WebSocket /api/v1/ws/runs - Real-time updates

---

## 7.3 Settings & Providers

### Settings
- [ ] GET /api/v1/settings - Get settings
- [ ] PUT /api/v1/settings - Update settings

### Providers
- [ ] GET /api/v1/providers - List providers
- [ ] GET /api/v1/providers/{name}/models - Get models
- [ ] POST /api/v1/providers/{name}/test - Test provider
- [ ] PUT /api/v1/settings/providers/{name}/key - Set key
- [ ] DELETE /api/v1/settings/providers/{name}/key - Remove key

---

## 7.4 Templates & Registry

### Templates
- [ ] GET /api/v1/templates - List templates
- [ ] GET /api/v1/templates/{id} - Get template
- [ ] POST /api/v1/templates/{id}/instantiate - Create from template

### Registry
- [ ] GET /api/v1/registry/components - List components
- [ ] GET /api/v1/registry/components/{type} - Get component

---

## 7.5 Analytics & Logs

### Analytics
- [ ] GET /api/v1/analytics/overview - Dashboard
- [ ] GET /api/v1/analytics/metrics - Execution metrics
- [ ] GET /api/v1/analytics/daily - Daily stats

### Logs
- [ ] GET /api/v1/logs - Get logs
- [ ] PUT /api/v1/logs/config - Set log level
- [ ] DELETE /api/v1/logs - Clear logs

---

## 7.6 Error Responses

### HTTP Status Codes
- [ ] 400 Bad Request: Invalid input returns error details
- [ ] 401 Unauthorized: Missing/invalid auth handled
- [ ] 404 Not Found: Non-existent resource
- [ ] 409 Conflict: Duplicate name
- [ ] 422 Validation Error: Schema violation
- [ ] 500 Internal Error: Server crash handling

---

## Summary

| Area | Endpoints | Passed |
|------|-----------|--------|
| Pipelines | 14 | ___ |
| Execution | 10 | ___ |
| Settings | 7 | ___ |
| Templates | 5 | ___ |
| Analytics | 6 | ___ |
| Errors | 6 | ___ |
| **Total** | **48** | ___ |
