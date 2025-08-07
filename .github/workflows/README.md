# GitHub Actions Workflows

This directory contains the CI/CD workflows for the Node Finder project.

## Workflows

### 🔧 `pre-commit.yml`

- **Triggers**: Push/PR to main/develop branches
- **Purpose**: Runs pre-commit hooks for code quality
- **Includes**: Ruff linting, formatting, Django upgrades, security checks

### 🧪 `ci.yml`

- **Triggers**: Push/PR to main/develop branches
- **Purpose**: Complete CI pipeline with tests and Docker builds
- **Includes**: Pre-commit, tests with PostgreSQL/Redis, Docker builds, coverage

### ⚡ `pull-request.yml`

- **Triggers**: Pull request events
- **Purpose**: Fast feedback for PRs with essential checks
- **Includes**: Changed-files pre-commit, security scanning, quick tests

## Dependencies

### 📦 `dependabot.yml`

- **Purpose**: Automated dependency updates
- **Monitors**: Python packages, Docker images, GitHub Actions
- **Schedule**: Weekly updates with automatic PR creation

## Usage

These workflows run automatically on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly dependency scans

## Local Development

To run the same checks locally:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run all checks
pre-commit run --all-files

# Run tests
make test

# Security scan
pip install bandit safety
safety check
bandit -r . -x "./venv/*,./env/*,**/migrations/*"
```

## Status Badges

Add these to your README for status visibility:

```markdown
[![CI](https://github.com/yourusername/nodeFinder/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/nodeFinder/actions/workflows/ci.yml)
[![Pre-commit](https://github.com/yourusername/nodeFinder/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/yourusername/nodeFinder/actions/workflows/pre-commit.yml)
```
