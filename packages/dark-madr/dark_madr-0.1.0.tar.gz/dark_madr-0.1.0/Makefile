# Makefile for ADR project

.PHONY: help install install-dev test lint format type-check clean build publish dev test-cli

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install the package"
	@echo "  install-dev - Install with development dependencies"
	@echo "  test        - Run tests"
	@echo "  test-cli    - Test CLI installation"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  type-check  - Run type checking"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the package"
	@echo "  dev         - Setup development environment"
	@echo "  all         - Run all quality checks"

# Install the package
install:
	uv sync
	uv pip install -e .

# Install with development dependencies
install-dev:
	uv sync --all-extras

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=src/adr --cov-report=term-missing --cov-report=html

# Test CLI installation
test-cli: install
	@echo "Testing CLI installation..."
	uv run adr --help
	@echo "CLI is working!"

# Run linting
lint:
	uv run ruff check src/ tests/

# Format code
format:
	uv run ruff format src/ tests/

# Run type checking
type-check:
	uv run mypy src/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build the package
build: clean
	uv build

# Setup development environment
dev: install-dev
	pre-commit install
	@echo "Development environment setup complete!"

# Run all quality checks
all: lint type-check test
	@echo "All quality checks passed!"

# Quick development cycle
check: format lint type-check test
	@echo "Quick check complete!"
