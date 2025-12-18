# Studio UI Checklist

## 6.1 Pipeline Builder

### Canvas
- [ ] Canvas loads without errors
- [ ] Drag component from palette to canvas
- [ ] Drop creates new stage
- [ ] Connect stages (draw dependency line)
- [ ] Disconnect stages (remove dependency)

### Stage Interactions
- [ ] Select stage: Opens config panel
- [ ] Edit stage config: Updates correctly
- [ ] Delete stage: Removes from canvas

### Navigation
- [ ] Zoom in/out works
- [ ] Pan canvas works
- [ ] Auto-layout arranges stages
- [ ] Undo/redo (if available)
- [ ] Mini-map navigation (if available)
- [ ] Multi-select stages (if available)
- [ ] Copy/paste stages (if available)

---

## 6.2 Stage Configuration

### Input Mapping
- [ ] Input mapping editor works
- [ ] Add/remove input mappings
- [ ] JMESPath syntax highlighting (if available)
- [ ] Upstream output autocomplete (if available)

### Configuration
- [ ] Config parameter inputs work
- [ ] Select component type
- [ ] View component documentation
- [ ] Notes/description field
- [ ] Dependencies dropdown

---

## 6.3 Execution Panel

### Input
- [ ] Sample input JSON editor works
- [ ] JSON syntax validation shown

### Execution
- [ ] Execute button triggers run
- [ ] Real-time stage status updates
- [ ] Execution timeline shows progress

### Results
- [ ] Stage output inspection works
- [ ] Error display with details
- [ ] Run duration displayed
- [ ] Token usage displayed
- [ ] Cost displayed
- [ ] Re-run with same input
- [ ] Re-run with modified input

---

## 6.4 Pipeline Management

### List View
- [ ] Pipeline list displays correctly
- [ ] Search/filter pipelines works
- [ ] Sort by name/date/status
- [ ] Pipeline status badges (draft/published)
- [ ] Pagination (if many pipelines)

### CRUD Operations
- [ ] Create new pipeline modal works
- [ ] Clone pipeline creates copy
- [ ] Delete pipeline with confirmation
- [ ] Edit pipeline opens builder

---

## 6.5 Settings Page

### Provider Cards
- [ ] Provider cards display
- [ ] Add API key (masked input)
- [ ] Test provider connection
- [ ] Remove API key
- [ ] Set default provider
- [ ] Key preview (last 4 chars)

### App Settings
- [ ] Theme toggle (light/dark/system)
- [ ] Auto-save toggle
- [ ] Apply settings to environment
- [ ] Restart backend button

---

## 6.6 Other Pages

### Operations Dashboard
- [ ] Metrics displayed correctly
- [ ] Analytics charts render
- [ ] Data is accurate

### Logs Page
- [ ] Logs page loads entries
- [ ] Log filtering works
- [ ] Log level badges display

### Templates
- [ ] Templates gallery displays
- [ ] Template search/filter
- [ ] Template instantiation works

### API Console
- [ ] Commands execute correctly
- [ ] Output displayed

### Admin
- [ ] API keys management works

---

## Summary

| Area | Tests | Passed |
|------|-------|--------|
| Pipeline Builder | 15 | ___ |
| Stage Config | 9 | ___ |
| Execution Panel | 12 | ___ |
| Pipeline Mgmt | 9 | ___ |
| Settings | 10 | ___ |
| Other Pages | 10 | ___ |
| **Total** | **65** | ___ |
