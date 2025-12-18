# Tutorial 1: Getting Started with FlowMason

**Duration:** 15 minutes

In this tutorial, you'll install FlowMason and create your first project using VSCode.

## Prerequisites

- **Python** 3.11 or higher
- **Visual Studio Code** 1.85.0 or later
- Basic familiarity with Python

## Step 1: Install FlowMason CLI

Open a terminal and install FlowMason from PyPI:

```bash
pip install flowmason
```

Verify the installation:

```bash
fm --version
# Should show: FlowMason CLI v1.0.0
```

> **Tip:** If `fm` command is not found, see [Troubleshooting](#troubleshooting) at the end.

## Step 2: Install the VSCode Extension

### Option A: From VS Code Marketplace (Recommended)

1. Open VSCode
2. Go to **Extensions** (`Ctrl+Shift+X` / `Cmd+Shift+X`)
3. Search for "**FlowMason**"
4. Click **Install**

### Option B: From VSIX File

```bash
code --install-extension flowmason-0.10.0.vsix
```

After installation, you'll see:
- **FlowMason icon** in the Activity Bar (left sidebar)
- **FlowMason status** in the status bar at the bottom

## Step 3: Create a New Project

Use the VSCode Command Palette to create a new project:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "**FlowMason: New Project**"
3. Press Enter

Follow the prompts:

| Prompt | Example Input |
|--------|---------------|
| Project name | `my-first-pipeline` |
| Description | `My first FlowMason project` |
| Author | `Your Name` |
| Include examples? | `Yes` |
| Location | Select a parent folder |

Click "**Open Project**" when prompted.

## Step 4: Explore the Project Structure

Your new project has this structure:

```
my-first-pipeline/
├── components/
│   ├── __init__.py
│   ├── example_node.py       # AI-powered component
│   └── example_operator.py   # Deterministic component
├── pipelines/
│   └── main.pipeline.json    # Your first pipeline
├── flowmason.json            # Project manifest
├── requirements.txt          # Dependencies
├── .gitignore
└── README.md
```

### Key Files

**`flowmason.json`** - Project configuration:
```json
{
  "name": "my-first-pipeline",
  "version": "1.0.0",
  "main": "pipelines/main.pipeline.json",
  "components": {
    "include": ["components/**/*.py"]
  },
  "providers": {
    "default": "anthropic",
    "anthropic": {
      "model": "claude-sonnet-4-20250514"
    }
  }
}
```

**`components/example_node.py`** - An AI node:
```python
@node(name="my-first-pipeline-processor", category="custom")
class MyFirstPipelineNode:
    class Input(NodeInput):
        text: str

    class Output(NodeOutput):
        result: str

    async def execute(self, input: Input, context) -> Output:
        # Uses LLM to process text
        ...
```

**`pipelines/main.pipeline.json`** - Your pipeline definition (open to see visual editor)

## Step 5: Start FlowMason Studio

Studio is the backend that executes pipelines.

### Using VSCode (Recommended)

1. Press `Ctrl+Shift+P` / `Cmd+Shift+P`
2. Type "**FlowMason: Start Studio**"
3. Press Enter

You'll see a notification: "FlowMason Studio started on port 8999"

The status bar will show: **FlowMason: Connected** ✓

### Using CLI

```bash
fm studio start
```

Check status:
```bash
fm studio status
```

## Step 6: Open the Visual Pipeline Editor

1. Click on `pipelines/main.pipeline.json` in the Explorer
2. The file opens in the JSON editor
3. Click "**Open DAG View**" in the editor toolbar (or `Ctrl+Shift+P` → "FlowMason: Open DAG View")

You'll see a visual representation of your pipeline stages.

## Step 7: Run Your First Pipeline

### Using VSCode (Recommended)

1. With `main.pipeline.json` open
2. Press `F5` to run the pipeline
3. Enter input when prompted:
   ```json
   {"text": "Hello, FlowMason!"}
   ```
4. View output in the Debug Console

### Using CLI

```bash
fm run pipelines/main.pipeline.json --input '{"text": "Hello, FlowMason!"}'
```

## Step 8: Explore VSCode Features

### FlowMason Panel (Activity Bar)

Click the FlowMason icon in the Activity Bar to see:

```
FLOWMASON
├── COMPONENTS
│   ├── Nodes
│   │   ├── generator
│   │   ├── critic
│   │   └── my-first-pipeline-processor
│   ├── Operators
│   │   ├── http-request
│   │   ├── json-transform
│   │   └── ...
│   └── Control Flow
│       ├── conditional
│       ├── foreach
│       └── ...
├── PIPELINES
│   └── main.pipeline.json
└── RUNS
    └── (execution history)
```

### Code Intelligence

Open `components/example_node.py` and notice:
- **Syntax highlighting** for decorators
- **Hover documentation** - Hover over `@node` to see docs
- **IntelliSense** - Autocomplete for imports and decorators
- **CodeLens** - "Run" and "Preview" buttons above components

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run Pipeline | `F5` |
| Set Breakpoint | `F9` |
| Step Over | `F10` |
| Command Palette | `Ctrl+Shift+P` / `Cmd+Shift+P` |

## Step 9: Configure LLM Provider (Optional)

For AI nodes to call real LLMs, set your API key:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

Or add to your shell profile (`~/.bashrc`, `~/.zshrc`).

## Step 10: Stop Studio

When done:

1. Press `Ctrl+Shift+P` / `Cmd+Shift+P`
2. Type "**FlowMason: Stop Studio**"

Or via CLI:
```bash
fm studio stop
```

## What You've Learned

- ✅ Installed FlowMason CLI (`pip install flowmason`)
- ✅ Installed VSCode extension
- ✅ Created a project using "FlowMason: New Project"
- ✅ Started FlowMason Studio
- ✅ Ran your first pipeline
- ✅ Explored the visual pipeline editor

## VSCode Commands Reference

| Command | Description |
|---------|-------------|
| FlowMason: New Project | Create a new project with structure |
| FlowMason: Start Studio | Start the backend server |
| FlowMason: Stop Studio | Stop the backend server |
| FlowMason: New Node | Create a new AI node |
| FlowMason: New Operator | Create a new operator |
| FlowMason: Open DAG View | Open visual pipeline editor |
| FlowMason: Refresh Registry | Refresh component list |

## Next Steps

Continue to [Tutorial 2: Building Your First Pipeline](02-building-first-pipeline.md) to create a multi-stage AI pipeline.

---

## Troubleshooting

### "fm: command not found"

Your Python scripts directory isn't in PATH:

```bash
# Option 1: Find and add to PATH
export PATH="$PATH:$(python -m site --user-base)/bin"

# Option 2: Use virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install flowmason
fm --version
```

### Studio fails to start

Check if port 8999 is in use:
```bash
lsof -i :8999
# Kill the process or use different port:
fm studio start --port 9000
```

### Extension not showing

1. Reload VSCode: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Check extension is enabled in Extensions panel
3. Ensure you have a folder open (not just a file)

### No components in sidebar

1. Ensure Studio is running (check status bar)
2. `Ctrl+Shift+P` → "FlowMason: Refresh Registry"
3. Check Output panel: View → Output → FlowMason
