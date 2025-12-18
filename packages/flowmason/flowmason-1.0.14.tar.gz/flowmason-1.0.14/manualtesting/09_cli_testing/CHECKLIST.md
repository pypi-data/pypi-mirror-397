# CLI Testing Checklist

## 9.1 Basic Commands

- [ ] `flowmason --help` - Shows help text
- [ ] `flowmason --version` - Shows version number
- [ ] `flowmason init` - Initialize project creates config
- [ ] `flowmason studio` - Starts Studio server

---

## 9.2 Pipeline Commands

### Run
- [ ] `flowmason run <pipeline>` - Execute pipeline
- [ ] `flowmason run <pipeline> --input <json>` - With inline JSON
- [ ] `flowmason run <pipeline> --input-file <file>` - From file

### Other
- [ ] `flowmason validate <pipeline>` - Validate pipeline
- [ ] `flowmason list` - List pipelines
- [ ] `flowmason show <pipeline>` - Show details

---

## 9.3 Package Commands

- [ ] `flowmason package install <pkg>` - Install package
- [ ] `flowmason package list` - List installed packages
- [ ] `flowmason package uninstall <pkg>` - Uninstall package

---

## 9.4 Configuration

- [ ] `flowmason config set <key> <value>` - Set config value
- [ ] `flowmason config get <key>` - Get config value
- [ ] `flowmason config list` - List all config
- [ ] Provider API key configuration via CLI
- [ ] Default provider setting via CLI

---

## 9.5 Error Handling

- [ ] Invalid pipeline file: Clear error message
- [ ] Missing input: Appropriate error
- [ ] Provider not configured: Helpful error
- [ ] Network error: Graceful handling

---

## Summary

| Area | Tests | Passed |
|------|-------|--------|
| Basic | 4 | ___ |
| Pipeline | 6 | ___ |
| Package | 3 | ___ |
| Config | 5 | ___ |
| Errors | 4 | ___ |
| **Total** | **22** | ___ |
