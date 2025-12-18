# Project 06: Studio UI

Comprehensive web UI testing for FlowMason Studio.

## Purpose
Test all UI components and interactions:
- Pipeline Builder (canvas, stages, connections)
- Stage Configuration panel
- Execution Panel
- Pipeline Management
- Settings Page
- Other pages (Operations, Logs, Templates, Admin)

## Time Required
~2 hours

## Prerequisites
- Studio running at http://localhost:8999
- At least one provider configured
- Some existing pipelines (from earlier tests)

## Test Areas

### 6.1 Pipeline Builder
- Canvas interactions
- Drag-and-drop
- Stage connections
- Zoom/pan

### 6.2 Stage Configuration
- Input mapping
- Config parameters
- Dependencies

### 6.3 Execution Panel
- JSON editor
- Execute and monitor
- Results display

### 6.4 Pipeline Management
- CRUD operations
- Search/filter
- Status badges

### 6.5 Settings Page
- Provider configuration
- Theme settings
- API keys

### 6.6 Other Pages
- Operations dashboard
- Logs viewer
- Templates gallery
- Admin panel

## Testing Approach
This project is primarily manual UI testing. Open each page and verify the behaviors listed in CHECKLIST.md.
