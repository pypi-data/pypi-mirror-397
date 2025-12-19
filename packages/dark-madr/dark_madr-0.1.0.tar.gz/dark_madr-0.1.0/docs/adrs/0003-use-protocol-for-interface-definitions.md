---
title: Use Protocol for Interface Definitions
status: accepted
date: 2025-12-16
authors:
  - m1yag1
tags:
  - architecture
  - typing
---

# 0003. Use Protocol for Interface Definitions

Date: 2025-12-16

## Status

accepted

## Context

Python supports multiple approaches for defining interfaces:

1. **Abstract Base Classes (ABC)** - Traditional approach using `abc.ABC` and
   `@abstractmethod`
2. **Protocol (PEP 544)** - Structural subtyping introduced in Python 3.8
3. **Duck typing** - No explicit interface, rely on runtime behavior

We needed interfaces for `ADRRepository` and `ADRSerializer` to enable
dependency injection and maintain loose coupling between components.

## Decision

We will use `typing.Protocol` for interface definitions:

```python
from typing import Protocol

class ADRRepository(Protocol):
    def save(self, adr: ADR, template: str | None = None) -> None: ...
    def find_by_number(self, number: int) -> ADR | None: ...
    # ...

class ADRSerializer(Protocol):
    def serialize(self, adr: ADR, template: str | None = None) -> str: ...
```

Implementations do not need to explicitly inherit from the Protocol:

```python
class FileSystemADRRepository(ADRRepository):  # Explicit inheritance for clarity
    # Implementation...

class TemplateADRSerializer:  # No inheritance needed, structural typing works
    def serialize(self, adr: ADR, template: str | None = None) -> str:
        # Implementation...
```

## Consequences

### Positive

- **Structural subtyping**: Classes satisfy the interface by having matching
  methods, no inheritance required
- **Better for duck typing**: Works naturally with Python's dynamic nature
- **Static type checking**: mypy validates Protocol conformance at type-check time
- **No runtime overhead**: Protocols are erased at runtime
- **Flexible**: Third-party classes can satisfy Protocols without modification

### Negative

- **Less explicit**: Without inheritance, it's not immediately obvious which
  Protocol a class implements (we chose to use explicit inheritance for clarity)
- **Python 3.8+ only**: Not available in older Python versions
- **Runtime isinstance checks**: Require `@runtime_checkable` decorator
