# Studio API Notes

## Common Request Headers

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <api_key>  (if auth enabled)
```

## Response Format

Success:
```json
{
  "data": { ... },
  "status": "success"
}
```

Error:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "details": { ... }
  },
  "status": "error"
}
```

## Issues Found

<!-- Add issues here -->

## API Observations

<!-- Notes about API behavior -->
