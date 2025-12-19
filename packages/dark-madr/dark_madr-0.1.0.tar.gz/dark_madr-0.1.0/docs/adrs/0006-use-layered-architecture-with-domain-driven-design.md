---
title: Use Layered Architecture with Domain-Driven Design
status: accepted
date: 2025-12-16
authors:
  - m1yag1
tags:
  - architecture
  - ddd
---

# 0006. Use Layered Architecture with Domain-Driven Design

Date: 2025-12-16

## Status

accepted

## Context

The application needs a clear structure that separates concerns and allows
independent evolution of different parts. Domain-Driven Design (DDD) provides
patterns for organizing code around the business domain.

## Decision

We will use a layered architecture inspired by DDD:

```
src/adr/
├── domain/           # Domain Layer - Core business logic
│   ├── models.py     # ADR, ADRMetadata, ADRStatus
│   └── repository.py # ADRRepository protocol, ADRParser
├── services.py       # Application Layer - Use cases
├── cli.py            # Interface Layer - CLI commands
├── template_engine.py # Infrastructure - Template rendering
├── config.py         # Infrastructure - Configuration
└── adr_manager.py    # Infrastructure - File operations
```

### Layer Responsibilities

**Domain Layer** (`domain/`)
- Pure business logic with no external dependencies
- Domain entities: `ADR`, `ADRMetadata`
- Value objects: `ADRStatus` enum
- Repository interface: `ADRRepository` protocol
- Domain exceptions: `ADRNotFoundError`, `ADRAlreadyExistsError`

**Application Layer** (`services.py`)
- Orchestrates domain objects to implement use cases
- `ADRService`: create, update, delete, supersede ADRs
- No direct I/O - delegates to repository

**Interface Layer** (`cli.py`)
- Handles user interaction
- Click commands translate user input to service calls
- Formats output using Rich

**Infrastructure Layer** (`template_engine.py`, `config.py`, `adr_manager.py`)
- Technical concerns: file I/O, templating, configuration
- `FileSystemADRRepository`: implements `ADRRepository`
- `TemplateADRSerializer`: implements `ADRSerializer`
- `TemplateEngine`: Jinja2 rendering

### Dependency Rule

Dependencies flow inward - outer layers depend on inner layers:

```
CLI → Services → Domain
 ↓        ↓
Infrastructure
```

The domain layer has no dependencies on other layers.

## Consequences

### Positive

- **Testable domain**: Business logic can be tested without I/O
- **Replaceable infrastructure**: Can swap storage, templates, CLI
- **Clear boundaries**: Each layer has defined responsibilities
- **Domain focus**: Business rules are centralized and visible

### Negative

- **Boilerplate**: More files and indirection than a simple script
- **Mapping overhead**: Data may need transformation between layers
- **Overkill for simple apps**: This structure suits medium+ complexity
