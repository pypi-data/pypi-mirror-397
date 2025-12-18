# Advanced Patterns Checklist

## 11.1 Multi-Stage Content Pipeline

- [ ] Full pipeline executes end-to-end
- [ ] Each stage receives correct input from previous
- [ ] Critique provides useful feedback
- [ ] Improver uses critique to enhance
- [ ] Synthesizer combines outputs
- [ ] Validator catches issues

---

## 11.2 ETL Workflow

- [ ] External API data fetched successfully
- [ ] Data transformed correctly
- [ ] Invalid records identified
- [ ] Schema validation works
- [ ] Filter removes bad records
- [ ] Final output correct format

---

## 11.3 Nested Control Flow

- [ ] Nested structure executes correctly
- [ ] Inner try-catch handles item errors
- [ ] Outer foreach continues on error
- [ ] Conditional routes each item correctly
- [ ] Finally runs for each item
- [ ] Results collected properly

---

## 11.4 Pipeline Inheritance

- [ ] Child inherits base stages
- [ ] Child can override stage config
- [ ] Child can add new stages
- [ ] Child can remove stages
- [ ] Diamond inheritance (if supported)

---

## 11.5 Dynamic Routing

- [ ] Route based on input field value
- [ ] Route based on previous output
- [ ] Route based on expression result
- [ ] Multiple sequential routers work
- [ ] Fallback/default route used when needed

---

## Summary

| Pattern | Tests | Passed |
|---------|-------|--------|
| Content Pipeline | 6 | ___ |
| ETL Workflow | 6 | ___ |
| Nested Control | 6 | ___ |
| Inheritance | 5 | ___ |
| Dynamic Routing | 5 | ___ |
| **Total** | **28** | ___ |
