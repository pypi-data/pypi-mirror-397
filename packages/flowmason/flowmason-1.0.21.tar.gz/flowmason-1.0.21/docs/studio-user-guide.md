# FlowMason Studio User Guide

This guide covers how to use FlowMason Studio to build, test, and publish AI pipelines.

## Overview

FlowMason Studio is a visual composition tool for building AI workflows. It consists of:

- **Pipeline Canvas** - Visual editor for connecting components
- **Component Palette** - Library of available nodes and operators
- **Stage Configuration Panel** - Configure selected components
- **Execution Panel** - Test and run pipelines

---

## Pipeline Builder

### Canvas Navigation

The pipeline canvas is your workspace for building workflows.

**Basic Controls:**
- **Pan**: Click and drag on empty space
- **Zoom**: Scroll wheel or pinch gestures
- **Select stage**: Click on a stage node
- **Delete stage**: Select a stage and press `Delete` or `Backspace`

**Canvas Controls (top-right):**
- **Zoom In/Out**: Adjust canvas zoom level
- **Fit View**: Auto-fit all stages in view
- **Toggle Notes**: Show/hide stage notes on the canvas

### Sidebar

The left sidebar contains the Component Palette and can be collapsed to give more canvas space.

**Collapse/Expand:** Click the sidebar toggle button in the bottom-left to collapse the sidebar, giving the canvas more room for complex pipelines.

**Component Categories:**
- **Core Nodes**: AI-powered components (Generator, Critic, Improver, etc.)
- **Transform Operators**: Data manipulation (JSON Transform, Filter, etc.)
- **Data Operators**: External integrations (HTTP Request, Logger, etc.)

### Adding Stages

1. Browse or search for a component in the palette
2. Drag the component onto the canvas
3. Drop to create a new stage

### Connecting Stages

Stages have **input** (top) and **output** (bottom) handles:

1. Hover over a stage to see connection handles
2. Click and drag from an output handle
3. Drop onto another stage's input handle
4. The connection appears as an animated edge

**Dependencies:** A stage will only execute after all its upstream dependencies complete.

---

## Stage Configuration

Click on a stage to open its configuration panel.

### Basic Settings

- **Stage Name**: Display name for the stage
- **Stage Notes**: Optional notes (toggle visibility with the Notes button)

### Input Mapping

Configure how data flows into the stage using template variables:

```
{{input.field_name}}        - Pipeline input
{{upstream.stage_id.field}} - Output from another stage
{{env.VAR_NAME}}            - Environment variable
{{context.run_id}}          - Execution context
```

**Example:**
```
Prompt: Analyze the following ticket: {{input.ticket_text}}
```

### LLM Settings (for Nodes)

Nodes that use AI models show LLM configuration:

- **Provider**: Select LLM provider (Anthropic, OpenAI, Google, Groq)
- **Model**: Choose specific model
- **Temperature**: Control randomness (0.0 = deterministic, 1.0 = creative)
- **Max Tokens**: Limit response length
- **Top P**: Nucleus sampling parameter

---

## Pipeline Status

Pipelines follow a Salesforce Flow-like lifecycle:

| Status | Badge | Description |
|--------|-------|-------------|
| **Draft** | Amber | Pipeline is being developed. Can be edited freely. |
| **Published** | Green | Pipeline has passed testing and is production-ready. |

**Status Badge Location:** The status badge appears next to the pipeline name in the builder header and on pipeline cards in the Pipelines list.

---

## Execution Panel

The right panel handles pipeline testing and execution.

### Run Mode vs Test Mode

Switch between modes using the tabs at the top:

| Mode | Purpose | Suitable For |
|------|---------|--------------|
| **Run** | Execute pipeline with inputs | Production use |
| **Test** | Validate pipeline before publishing | Development |

### Running a Pipeline

1. Switch to **Run** tab
2. Fill in pipeline inputs (based on input schema)
3. Click **Run Pipeline**
4. View results in the output section

### Test & Publish Workflow

To publish a pipeline for production:

1. Switch to **Test** tab
2. Fill in sample inputs
3. Click **Run Test**
4. If test passes:
   - Review the output
   - Click **Publish Pipeline**
5. Pipeline status changes to "Published"

**Publishing Requirements:**
- Pipeline must have at least one stage
- A successful test run is required
- Test run ID is stored with the published version

### Unpublishing

To revert a published pipeline to draft:
1. Click **Unpublish** in the test panel
2. Confirm the action
3. Pipeline returns to draft status

---

## Debug Panel

The debug panel provides deep inspection of pipeline executions.

### Viewing Execution Trace

After running a pipeline, the trace shows:
- Each stage that executed
- Status (completed, failed, skipped)
- Execution time
- Token usage

### Step Inspection

Click on a stage in the trace to expand it:

**Input Section:** Shows the exact input data sent to the stage
**Output Section:** Shows the result returned by the stage
**Error Section:** If failed, shows error details

**Copy Data:** Use the copy buttons to copy input/output JSON for debugging.

### Retry Step

For failed stages:
1. Expand the step details
2. Review the error
3. Make changes to the stage configuration
4. Click the **Retry** icon to re-execute that specific step

---

## Templates

Templates are pre-built pipeline examples you can use as starting points.

### Accessing Templates

1. Click **New Pipeline** on the Pipelines page
2. Select **From Template** tab
3. Browse templates by category
4. Click **Use Template** to create a new pipeline

### Template Categories

| Category | Description |
|----------|-------------|
| **Getting Started** | Basic examples for learning |
| **Content Creation** | Blog posts, review loops, drafting |
| **Salesforce & CRM** | Lead qualification, customer email, call summarization |
| **Data & Integration** | API pipelines, webhook processing |
| **Quality Assurance** | Output validation, iterative refinement |

### Creating Your Own Templates

1. Build and test a pipeline
2. When saving, check **Save as Template**
3. Fill in template metadata:
   - Description
   - Category
   - Difficulty level
   - Use cases

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Delete` / `Backspace` | Delete selected stage |
| `Ctrl/Cmd + S` | Save pipeline |
| `Ctrl/Cmd + Z` | Undo |
| `Ctrl/Cmd + Shift + Z` | Redo |

---

## Dark Mode

Studio supports both light and dark modes:

1. Go to **Settings** page
2. Select **Appearance**
3. Choose: **Light**, **Dark**, or **System** (follows OS preference)

All components support dark mode with appropriate color schemes.

---

## Best Practices

### Pipeline Design

1. **Keep pipelines focused** - One pipeline, one purpose
2. **Use descriptive stage names** - Clear names make debugging easier
3. **Add notes to complex stages** - Document non-obvious configurations
4. **Test with realistic inputs** - Use production-like data for testing

### Performance

1. **Minimize LLM calls** - Each node call costs time and tokens
2. **Use operators for data transformation** - Faster than using LLMs
3. **Set appropriate max_tokens** - Don't request more than needed
4. **Use temperature 0 for deterministic outputs** - Better for testing

### Publishing

1. **Always test before publishing** - Catch errors early
2. **Document input schemas clearly** - Help API consumers
3. **Version your pipelines** - Track changes over time
4. **Monitor published pipelines** - Check for errors in production

---

## Troubleshooting

### Pipeline Won't Save

- Check for validation errors (red indicators)
- Ensure all required fields are filled
- Check browser console for errors

### Test Fails

1. Check the error message in the debug panel
2. Expand the failing stage to see details
3. Verify input mappings are correct
4. Check that upstream stages completed

### Stage Shows "Unknown Component"

- The component package may not be installed
- Go to **Packages** page and verify installation
- Refresh the registry if recently deployed

### Published Pipeline Returns Errors

1. Check the run trace for failure stage
2. Review input data format
3. Verify LLM provider is configured
4. Check API key validity in Settings
