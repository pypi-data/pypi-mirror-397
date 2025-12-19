---
title: Use Dependency Injection for ADR Serialization
status: accepted
date: 2025-12-16
authors:
  - m1yag1
tags:
  - architecture
  - solid
---

# 0002. Use Dependency Injection for ADR Serialization

Date: 2025-12-16

## Status

accepted

## Context

The ADR domain model (`ADR` class) originally contained methods for serializing
itself to markdown (`to_markdown()`, `_to_madr_format()`, `_to_simple_format()`)
and deserializing from markdown (`from_markdown()`). This violated several SOLID
principles:

- **Single Responsibility Principle (SRP)**: The model handled both domain logic
  and serialization concerns
- **Open/Closed Principle (OCP)**: Adding new output formats required modifying
  the model class
- **Dependency Inversion Principle (DIP)**: The repository was tightly coupled
  to the model's serialization methods

Additionally, the project already had Jinja2 templates for rendering ADRs, but
the model contained duplicate hardcoded serialization logic.

## Decision

We will use dependency injection to separate serialization from the domain model:

1. **Create `ADRSerializer` protocol** - Defines the interface for serialization
2. **Create `TemplateADRSerializer`** - Implementation using Jinja2 templates
3. **Create `ADRParser`** - Handles parsing markdown back to ADR objects
4. **Inject dependencies into `FileSystemADRRepository`** - Repository receives
   serializer and parser via constructor

The domain model (`ADR`) now contains only:
- Domain properties (metadata, context, decision, consequences, alternatives)
- Domain behaviors (accept, deprecate, supersede)
- Computed properties (filename, is_active)

## Consequences

### Positive

- **Clean domain model**: 100% test coverage, focused on business logic
- **Single responsibility**: Each class has one reason to change
- **Open for extension**: New formats can be added via new serializer implementations
- **Testability**: Components can be tested in isolation with mocks
- **Template reuse**: Serialization uses the same Jinja2 templates as the CLI
- **Reduced code duplication**: Removed ~160 lines of hardcoded serialization

### Negative

- **More classes**: Introduces `ADRSerializer`, `TemplateADRSerializer`, `ADRParser`
- **Constructor complexity**: Repository now requires a serializer parameter
- **Indirection**: Serialization path is less obvious when reading the code
