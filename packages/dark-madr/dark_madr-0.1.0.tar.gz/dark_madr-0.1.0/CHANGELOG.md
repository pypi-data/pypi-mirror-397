# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of ADR (Architecture Decision Records) management tool
- CLI commands: `init`, `new`, `list`, `show`, `generate toc`, `templates`, `help-template`, `config`, `init-config`
- Support for multiple templates: Nygard (classic) and MADR formats
- Configuration via `pyproject.toml` `[tool.adr]` section
- Domain model with Pydantic for ADR metadata validation
- File-based repository for ADR storage
- Rich terminal output with syntax highlighting
- Template engine using Jinja2
- Supersession support for ADR lifecycle management
- Table of contents generation

### Changed
- N/A

### Fixed
- N/A

## [0.1.0] - 2024-01-01

### Added
- Initial project structure
- Basic ADR management functionality
- CLI interface with Click
- Template system with Jinja2
- Rich console output
- Configuration management
- Test suite with pytest
