# VSCode Extension MCP Integration

The FlowMason VSCode extension includes AI-assisted pipeline creation via MCP (Model Context Protocol) integration. This allows developers to describe what they want in natural language and have the extension generate pipeline configurations automatically.

## Features

### Create Pipeline with AI
Use natural language to describe your pipeline, and let AI generate the complete configuration.

**Command:** `FlowMason: Create Pipeline with AI` (Cmd+Shift+P)

**Workflow:**
1. Describe what you want (e.g., "Summarize articles and filter by sentiment")
2. Review suggested stages
3. Select which stages to include
4. Choose to accept or customize the generated configuration
5. Name your pipeline and save

### Get Pipeline Suggestions
Get AI-powered suggestions for building a pipeline without committing to creation.

**Command:** `FlowMason: Get Pipeline Suggestions`

**Usage:**
1. Describe your task
2. View suggested components and their purposes
3. See example pipeline structure in the output panel
4. Optionally proceed to create the pipeline

### Generate Stage with AI
Generate a single stage configuration for any component type.

**Command:** `FlowMason: Generate Stage with AI`

**Workflow:**
1. Select component type (generator, filter, json_transform, etc.)
2. Describe what the stage should do
3. Specify input source (pipeline input or previous stage output)
4. Review generated configuration in editor

### Validate Pipeline
Validate the currently open pipeline file for errors and warnings.

**Command:** `FlowMason: Validate Pipeline`

Available in the editor title bar for `.pipeline.json` files.

### Add AI-Generated Stage
Add an AI-generated stage to the currently open pipeline.

**Command:** `FlowMason: Add AI-Generated Stage`

**Workflow:**
1. Open a `.pipeline.json` file
2. Select component type
3. Describe stage purpose
4. Select input source from existing stages
5. Stage is automatically added to the pipeline

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Create Pipeline with AI | Cmd+Shift+P → "FlowMason: Create Pipeline with AI" |
| Validate Pipeline | Cmd+Shift+P → "FlowMason: Validate Pipeline" |

## Editor Title Bar Actions

When editing a `.pipeline.json` file, additional buttons appear in the editor title bar:

- **Add AI-Generated Stage** - Generate and add a new stage
- **Validate Pipeline** - Check for errors and warnings

## How It Works

The extension uses the MCP service to communicate with FlowMason Studio or provides local fallback functionality:

### With FlowMason Studio Running
- Fetches available components from the registry
- Validates against actual component schemas
- Accesses pipeline templates and examples

### Local Mode (Studio Not Running)
- Uses built-in component knowledge
- Generates reasonable default configurations
- Validates basic pipeline structure

## Configuration

The MCP integration uses the existing FlowMason settings:

```json
{
  "flowmason.studioUrl": "http://localhost:8999"
}
```

## Example Usage

### Creating a Content Processing Pipeline

1. Open Command Palette (Cmd+Shift+P)
2. Type "FlowMason: Create Pipeline with AI"
3. Enter description: "Fetch RSS feed, summarize each article, and filter by topic relevance"
4. Review suggested stages:
   - `http_request` - Fetch RSS feed
   - `loop` - Iterate over articles
   - `generator` - Summarize content
   - `filter` - Filter by relevance
5. Select all stages and accept
6. Name pipeline "rss-summarizer"
7. Pipeline is created and opened in editor

### Adding a Stage to Existing Pipeline

1. Open your `.pipeline.json` file
2. Click "Add AI-Generated Stage" in editor title bar
3. Select `filter` component
4. Describe: "filter out articles older than 7 days"
5. Select input source: `stages.fetch.output`
6. Stage is added with appropriate configuration

## Troubleshooting

### "Failed to get suggestions"
- Check if FlowMason Studio is running
- Verify `flowmason.studioUrl` setting is correct
- The extension will fall back to local mode automatically

### Generated Configuration Needs Adjustment
- Use "Customize" option to edit generated stages
- Generated prompts and configurations are starting points
- Adjust parameters based on your specific needs

### Validation Errors
- Run "FlowMason: Validate Pipeline" to see detailed errors
- Check the FlowMason output panel for full error messages
- Common issues: missing required fields, invalid stage IDs

## Best Practices

1. **Be Specific**: More detailed descriptions yield better suggestions
2. **Review Before Saving**: Always review generated configurations
3. **Use Validation**: Validate before running pipelines
4. **Iterate**: Use "Add AI-Generated Stage" to build incrementally
5. **Customize**: Treat generated config as a starting point

## API Integration

The extension exposes MCP functionality through the following internal service:

```typescript
interface MCPService {
  suggestPipeline(taskDescription: string): Promise<PipelineSuggestion>
  generateStage(stageType: string, purpose: string, inputSource: string): Promise<GeneratedStage>
  validatePipeline(pipelineJson: string): Promise<ValidationResult>
  createPipeline(name: string, description: string, stages: GeneratedStage[]): Promise<string>
}
```

This service can be used by other extension features or extensions that depend on FlowMason.
