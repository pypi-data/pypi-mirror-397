# Test Project for Sindri

This is a test project designed to test all Sindri functionality.

## Features

This project includes:

- Python application with main module
- Unit tests with pytest
- Code quality tools (ruff, mypy)
- Docker support (Dockerfile, docker-compose.yml)
- Git repository
- Version management
- All Sindri command groups configured

## Usage

After installing Sindri (`pip install sindri-dev`), you can use it in this project:

```bash
# Initialize Sindri (if not already done)
sindri init

# List all available commands
sindri list

# Run tests
sindri run test

# Run setup
sindri run setup
```

## Testing Sindri Features

The project is configured to test all Sindri command groups:

- **General Group**: Setup, Install
- **Quality Group**: Test, Coverage, Lint, Validate
- **Application Group**: Start, Stop, Restart, Build
- **Docker Group**: Build, Push, Build+Push, Up, Down, Restart
- **Compose Group**: Up, Down, Build, Restart
- **Git Group**: Commit, Push
- **Version Group**: Show, Bump, Tag
- **PyPI Group**: Validate, Push
- **Custom Commands**: With dependencies, env vars, timeouts

## Project Structure

```
test_project/
├── test_project/              # Main application code
├── tests/                      # Test files
├── Dockerfile                  # Test project Docker image
├── docker-compose.yml          # Test project Docker Compose
├── pyproject.toml              # Python project configuration
├── sindri.toml                 # Sindri configuration
└── README.md                   # This file
```
