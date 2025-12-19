# Quick Start Guide - Testing Sindri

This guide shows you how to quickly test Sindri functionality.

## Prerequisites

- Python 3.11+
- Sindri installed: `pip install sindri-dev`

## Quick Start

### Initialize Sindri

```bash
# Navigate to test project
cd test_project

# Initialize Sindri configuration
sindri init

# This creates .sindri/sindri.toml with detected command groups
```

### Use Sindri

```bash
# List all available commands
sindri list

# Run tests
sindri run test

# Run setup
sindri run setup

# Run quality checks
sindri run lint
sindri run validate

# Run application commands
sindri run start
sindri run build
```

## Testing Different Features

### Test Command Groups

```bash
# Quality commands
sindri run test
sindri run cov
sindri run lint
sindri run validate

# Application commands
sindri run start
sindri run stop
sindri run build

# Docker commands
sindri run docker-build
sindri run docker-up

# Git commands
sindri run git-commit
sindri run git-push

# Version commands
sindri run version-show
sindri run version-bump

# PyPI commands
sindri run pypi-validate
sindri run pypi-push
```

### Test Custom Commands

```bash
# Simple command
sindri run test-custom-echo

# Command with dependencies
sindri run test-custom-chain

# Command with environment variables
sindri run test-custom-env
```

## Interactive Mode

Open the interactive TUI:

```bash
sindri
```

This opens an interactive menu where you can:
- Search for commands
- View command details
- Execute commands
- See command output in real-time
