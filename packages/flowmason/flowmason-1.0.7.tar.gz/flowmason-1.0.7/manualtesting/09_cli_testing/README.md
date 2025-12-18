# Project 09: CLI Testing

Test FlowMason command-line interface.

## Purpose
Test all CLI commands:
- Basic commands (help, version, init, studio)
- Pipeline commands (run, validate, list, show)
- Package commands
- Configuration

## Time Required
~45 minutes

## Prerequisites
- FlowMason CLI installed
- Pipelines from earlier tests

## Commands Overview

### Basic
```bash
flowmason --help
flowmason --version
flowmason init
flowmason studio
```

### Pipeline Operations
```bash
flowmason run <pipeline>
flowmason run <pipeline> --input '{"key": "value"}'
flowmason run <pipeline> --input-file input.json
flowmason validate <pipeline>
flowmason list
flowmason show <pipeline>
```

### Packages
```bash
flowmason package install <pkg>
flowmason package list
flowmason package uninstall <pkg>
```

### Configuration
```bash
flowmason config set <key> <value>
flowmason config get <key>
flowmason config list
```
