# Data Operators Checklist

## 4.1 json_transform

### Field Operations
- [ ] Field rename: { old_name → new_name }
- [ ] Field extraction: $.nested.field
- [ ] Array mapping: items[*].name

### Transformations
- [ ] Conditional transform: if/then/else
- [ ] Type conversion in transform
- [ ] Null handling in paths
- [ ] Missing field handling

### JMESPath
- [ ] Complex JMESPath: sort, filter, projection

---

## 4.2 filter

### Conditions
- [ ] Filter by equality: status == "active"
- [ ] Filter by comparison: age > 18
- [ ] Filter by contains: tags contains "important"

### Boolean Logic
- [ ] AND conditions: a && b
- [ ] OR conditions: a || b
- [ ] NOT conditions: !a

### Edge Cases
- [ ] Empty array input: Returns empty
- [ ] All filtered out: Returns empty
- [ ] None filtered: Returns all
- [ ] Null values in filter field

---

## 4.3 http_request

### Methods
- [ ] GET: Returns response body
- [ ] POST: Sends JSON body correctly
- [ ] PUT/PATCH/DELETE methods work

### Features
- [ ] Custom headers (Authorization, Content-Type)
- [ ] Query parameters appended correctly
- [ ] Timeout handling works

### Error Handling
- [ ] 4xx error: Returns error details
- [ ] 5xx error: Retry behavior
- [ ] Network error: Handled gracefully
- [ ] Large response handling

---

## 4.4 schema_validate

### Validation Types
- [ ] Valid data: Passes through unchanged
- [ ] Invalid data: Returns validation errors
- [ ] Required field missing: Error shown
- [ ] Type mismatch: Error shown

### Schema Features
- [ ] Pattern validation (regex)
- [ ] Enum validation
- [ ] Nested object validation
- [ ] Array item validation

---

## 4.5 variable_set

### Basic Operations
- [ ] Set variable: Available in downstream stages
- [ ] Override variable: New value used
- [ ] Variable not found: Appropriate error

### Data Types
- [ ] String variables
- [ ] Number variables
- [ ] Object variables
- [ ] Array variables
- [ ] Variable in JMESPath expressions

---

## 4.6 logger

### Log Levels
- [ ] DEBUG level: Captured in logs
- [ ] INFO level: Standard logging
- [ ] WARNING level: Warning highlight
- [ ] ERROR level: Error highlight

### Content
- [ ] Context object logged correctly
- [ ] Large message handling
- [ ] Special characters in message

---

## Summary

| Operator | Tests | Passed |
|----------|-------|--------|
| json_transform | 8 | ___ |
| filter | 10 | ___ |
| http_request | 11 | ___ |
| schema_validate | 8 | ___ |
| variable_set | 8 | ___ |
| logger | 7 | ___ |
| **Total** | **52** | ___ |
