# FlowMason Tutorials

Step-by-step guides to help you master FlowMason.

## Tutorial Path

Follow these tutorials in order for the best learning experience:

| # | Tutorial | Duration | What You'll Learn |
|---|----------|----------|-------------------|
| 1 | [Getting Started](./01-getting-started.md) | 15 min | Install extension, set up project |
| 2 | [Building Your First Pipeline](./02-building-first-pipeline.md) | 30 min | Create a 3-stage AI pipeline |
| 3 | [Debugging Pipelines](./03-debugging-pipelines.md) | 25 min | Breakpoints, stepping, prompt editing |
| 4 | [Testing Pipelines](./04-testing-pipelines.md) | 25 min | Write tests, use mocks, coverage |
| 5 | [Working with Components](./05-working-with-components.md) | 35 min | Create custom nodes and operators |

**Total Time:** ~2.5 hours

## Prerequisites

Before starting:
- VSCode 1.85.0 or later
- Python 3.11 or later
- Basic understanding of JSON and Python

## Quick Start

If you're in a hurry:

1. **Install** (5 min)
   ```bash
   code --install-extension flowmason-0.10.0.vsix
   pip install flowmason flowmason-studio flowmason-lab
   ```

2. **Create Project** (2 min)
   ```bash
   mkdir my-project && cd my-project
   fm init
   fm studio start
   code .
   ```

3. **Run a Pipeline** (1 min)
   - Open any `.pipeline.json` file
   - Press `F5` to run

## Tutorial Summaries

### Tutorial 1: Getting Started

Learn how to:
- Install the FlowMason VSCode extension
- Set up Python dependencies
- Initialize a FlowMason project
- Start the Studio backend
- Navigate the VSCode interface

### Tutorial 2: Building Your First Pipeline

Learn how to:
- Create pipeline files (`.pipeline.json`)
- Add stages using the visual editor
- Configure component inputs
- Use template expressions (`{{input.field}}`)
- Run pipelines from VSCode

### Tutorial 3: Debugging Pipelines

Learn how to:
- Set breakpoints on stages
- Step through execution (F10, F11)
- Inspect variables and outputs
- Use the Prompt Editor for AI stages
- Handle errors and exceptions

### Tutorial 4: Testing Pipelines

Learn how to:
- Create test files (`.test.json`)
- Write assertions for outputs
- Mock external services and LLMs
- Run tests from Test Explorer
- Generate coverage reports

### Tutorial 5: Working with Components

Learn how to:
- Create custom AI nodes (`@node`)
- Create custom operators (`@operator`)
- Use built-in control flow components
- Register components in your project
- Package components for distribution

## Additional Resources

- [Reference Documentation](../04-core-framework/decorators/node.md)
- [Concepts Guide](../03-concepts/pipelines.md)
- [Studio API Reference](../06-studio/overview.md)
- [VSCode Extension Guide](../07-vscode-extension/overview.md)

## Getting Help

- Check the [Troubleshooting](../07-vscode-extension/overview.md#troubleshooting) section
- View FlowMason output: `View > Output > FlowMason`
- Run diagnostics: `fm validate pipelines/`

## Feedback

Found an issue or have suggestions? Open an issue on GitHub.
