---
title: Apply SOLID Principles to Architecture
status: accepted
date: 2025-12-16
authors:
  - m1yag1
tags:
  - architecture
  - solid
---

# 0005. Apply SOLID Principles to Architecture

Date: 2025-12-16

## Status

accepted

## Context

As the codebase grows, we need consistent design principles to ensure
maintainability, testability, and extensibility. SOLID principles provide
a well-established framework for object-oriented design:

- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

## Decision

We will apply SOLID principles throughout the codebase:

### Single Responsibility Principle (SRP)

Each class has one reason to change:

| Class | Responsibility |
|-------|----------------|
| `ADR` | Domain entity with business rules |
| `ADRMetadata` | ADR metadata validation |
| `ADRParser` | Parse markdown to ADR objects |
| `TemplateADRSerializer` | Serialize ADR to markdown |
| `FileSystemADRRepository` | Persist/retrieve ADRs from filesystem |
| `ADRService` | Orchestrate ADR operations |
| `TemplateEngine` | Render Jinja2 templates |

### Open/Closed Principle (OCP)

Open for extension, closed for modification:

- New output formats: Add new `ADRSerializer` implementations
- New storage backends: Add new `ADRRepository` implementations
- New templates: Add `.md` files to templates directory

### Liskov Substitution Principle (LSP)

Subtypes are substitutable for their base types:

- `FileSystemADRRepository` can replace any `ADRRepository`
- `TemplateADRSerializer` can replace any `ADRSerializer`

### Interface Segregation Principle (ISP)

Clients depend only on interfaces they use:

- `ADRRepository` defines only persistence methods
- `ADRSerializer` defines only serialization methods
- No "god interfaces" with unrelated methods

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions:

```python
class FileSystemADRRepository(ADRRepository):
    def __init__(
        self,
        base_path: Path,
        serializer: ADRSerializer,  # Depends on abstraction
        parser: ADRParser | None = None,
    ) -> None:
        ...
```

## Consequences

### Positive

- **Testability**: Components can be tested in isolation with mocks
- **Maintainability**: Changes are localized to specific classes
- **Extensibility**: New features don't require modifying existing code
- **Readability**: Each class has a clear, focused purpose
- **Flexibility**: Easy to swap implementations (e.g., different storage)

### Negative

- **More files**: More classes means more files to navigate
- **Indirection**: Call chains can be harder to follow
- **Overhead**: Small projects may not benefit from this structure
- **Learning curve**: Developers need to understand the patterns
