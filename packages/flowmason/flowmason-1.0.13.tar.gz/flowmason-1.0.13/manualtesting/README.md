# FlowMason Manual Testing Suite

Comprehensive manual testing suite covering all FlowMason functionality: Core engine, Studio web UI, VSCode extension, and CLI.

## Overview

| Project | Description | Time | Test Cases |
|---------|-------------|------|------------|
| [01_smoke_test](./01_smoke_test/) | Quick validation everything works | 15 min | 9 |
| [02_control_flow_mastery](./02_control_flow_mastery/) | All 6 control flow types | 2 hrs | 60 |
| [03_llm_providers_deep](./03_llm_providers_deep/) | All 4 providers with all capabilities | 1.5 hrs | 50 |
| [04_data_operators](./04_data_operators/) | All operators and transformations | 1 hr | 42 |
| [05_error_resilience](./05_error_resilience/) | Errors, retries, timeouts, cancellation | 1.5 hrs | 48 |
| [06_studio_ui](./06_studio_ui/) | Web UI comprehensive testing | 2 hrs | 55 |
| [07_studio_api](./07_studio_api/) | API endpoints exhaustive testing | 2 hrs | 38 |
| [08_vscode_extension](./08_vscode_extension/) | VSCode debugging and integration | 1 hr | 20 |
| [09_cli_testing](./09_cli_testing/) | Command-line interface testing | 45 min | 18 |
| [10_templates_and_ai](./10_templates_and_ai/) | Templates, AI generation, copilot | 1 hr | 21 |
| [11_advanced_patterns](./11_advanced_patterns/) | Complex real-world scenarios | 1.5 hrs | 23 |
| [12_stress_and_performance](./12_stress_and_performance/) | Load testing, large batches, limits | 1.5 hrs | 26 |
| **TOTAL** | | **~16 hours** | **~410** |

## Prerequisites

### Required
- Python 3.11+
- Node.js 18+
- FlowMason installed and configured
- API keys for all 4 providers:
  - Anthropic (Claude)
  - OpenAI (GPT-4)
  - Google (Gemini)
  - Groq (Llama)

### Setup

1. **Start FlowMason Studio:**
   ```bash
   flowmason studio start
   ```
   Studio runs at `http://localhost:8999` (both API and web UI)

2. **Configure Providers:**
   - Open Studio → Settings
   - Add API keys for all 4 providers
   - Test each provider connection

3. **Install VSCode Extension (for Project 08):**
   ```bash
   code --install-extension vscode-extension/flowmason-0.9.5.vsix
   ```

## How to Use This Suite

### Full Testing (Recommended Order)
Run projects in order 01-12 for comprehensive coverage:

1. Start with **01_smoke_test** to verify everything is working
2. If smoke test passes, continue with remaining projects
3. Track progress using CHECKLIST.md in each project
4. Document issues in NOTES.md

### Focused Testing
Cherry-pick specific projects based on what you need to test:

- **Core functionality:** Projects 01, 02, 04, 05
- **LLM integrations:** Project 03
- **UI/UX:** Projects 06, 10
- **API testing:** Project 07
- **IDE integration:** Projects 08, 09
- **Edge cases & limits:** Projects 11, 12

## Project Structure

Each project contains:
```
XX_project_name/
├── README.md              # Purpose, what's tested, setup, expected outcomes
├── pipelines/             # JSON pipeline definitions to test
├── inputs/                # Sample input data for each pipeline
├── expected/              # Expected outputs (for manual validation)
├── CHECKLIST.md           # Checkbox list of all test cases
└── NOTES.md               # Your notes, issues found, observations
```

## Running Pipelines

### Via Studio UI
1. Open Studio at http://localhost:8999
2. Import pipeline JSON from project's `pipelines/` folder
3. Use input from project's `inputs/` folder
4. Execute and compare output to `expected/`

### Via CLI
```bash
flowmason run manualtesting/01_smoke_test/pipelines/hello_world.json \
  --input-file manualtesting/01_smoke_test/inputs/hello_input.json
```

### Via API
```bash
curl -X POST http://localhost:8999/api/v1/debug/run \
  -H "Content-Type: application/json" \
  -d @manualtesting/01_smoke_test/pipelines/hello_world.json
```

## Tracking Progress

### Using Checklists
Each project has a `CHECKLIST.md` with test cases as checkboxes:
```markdown
- [x] Test case completed ✓
- [ ] Test case pending
```

Edit the file as you complete tests.

### Recording Issues
Use `NOTES.md` in each project to document:
- Bugs found
- Unexpected behavior
- Performance observations
- Suggested improvements

### Example Notes Entry
```markdown
## Issue: Router doesn't handle null values
**Date:** 2024-12-15
**Severity:** Medium
**Steps to reproduce:**
1. Run router_default.json with null routing value
2. Expected: Routes to default branch
3. Actual: Throws NullPointerException

**Workaround:** Use empty string instead of null
```

## Test Coverage Matrix

| Area | Projects |
|------|----------|
| Nodes (AI) | 01, 02, 03, 10, 11 |
| Operators | 04, 11 |
| Control Flow | 02, 11 |
| Error Handling | 05, 11 |
| Providers | 03 |
| Studio UI | 01, 06, 10 |
| Studio API | 07 |
| VSCode | 08 |
| CLI | 09 |
| Performance | 12 |

## Tips

1. **Start Fresh:** Clear database before full test run
   ```bash
   rm .flowmason/flowmason.db
   ```

2. **Monitor Logs:** Keep logs open during testing
   - Studio: Settings → Logs page
   - CLI: `flowmason studio --log-level DEBUG`

3. **Check Token Usage:** Verify costs don't spike unexpectedly
   - Monitor in Operations dashboard
   - Provider billing dashboards

4. **Take Screenshots:** For UI bugs, capture screenshots in NOTES.md

5. **Test Edge Cases:** Don't just test happy paths
   - Empty inputs
   - Very large inputs
   - Special characters
   - Concurrent operations

## Contributing

When adding new test cases:
1. Add pipeline JSON to appropriate project's `pipelines/`
2. Add matching input to `inputs/`
3. Add expected output to `expected/`
4. Update CHECKLIST.md with new test cases
5. Update this README if adding new projects

## Support

- FlowMason Docs: See `/fmdocs/` folder
- Report Issues: Document in NOTES.md, escalate to dev team
