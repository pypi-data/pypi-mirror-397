# Smoke Test Checklist

## Studio Startup
- [ ] Studio starts without errors (http://localhost:8999)
- [ ] Web UI loads at http://localhost:8999
- [ ] No console errors in browser dev tools
- [ ] Component palette loads with all components visible

## Pipeline CRUD
- [ ] Create pipeline via UI succeeds
- [ ] Save pipeline persists to database
- [ ] Load saved pipeline shows correct stages
- [ ] Delete pipeline removes from list

## Execution
- [ ] Execute pipeline returns valid output
- [ ] Output structure matches expected format
- [ ] Token usage is tracked and displayed

## Provider Configuration
- [ ] Provider settings page loads
- [ ] At least one provider configured and working
- [ ] Test provider connection succeeds

## Quick Validation Pipelines

### hello_world.json
- [ ] Pipeline loads without errors
- [ ] Executes successfully
- [ ] Output contains greeting text
- [ ] Duration and cost metrics shown

### two_stage.json
- [ ] Pipeline loads without errors
- [ ] Both stages execute in order
- [ ] Generator output flows to Critic
- [ ] Final output contains critique

---

**Tester:** _________________
**Date:** _________________
**Pass/Fail:** _________________
