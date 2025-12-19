---
title: Support YAML Frontmatter and Documentation System Plugins
status: proposed
date: 2025-12-17
authors:
  - m1yag1
tags:
  - architecture
  - documentation
  - sphinx
---

# 0007. Support YAML Frontmatter and Documentation System Plugins

Date: 2025-12-17

## Status

proposed

## Context

Current ADR parsing relies on regex patterns to extract metadata from markdown
headers and sections. This approach has limitations:

1. **Fragile parsing**: Status, date, and other metadata must be in specific
   formats and locations within the document
2. **Limited metadata**: Only basic fields (status, date) are supported
3. **No documentation integration**: ADRs cannot be easily consumed by
   documentation systems like Sphinx or MkDocs
4. **No hierarchical relationships**: Cannot express parent/child ADRs or
   component groupings

Inspiration from [tnh-scholar](https://github.com/aaronksolomon/tnh-scholar)
shows a more sophisticated approach using:
- YAML frontmatter for structured metadata
- Component-based ADR prefixes (e.g., `adr-at01` for AI Text processing)
- Decimal sub-ADRs for related decisions (e.g., `adr-at03.1`)
- Integration with MkDocs for published documentation

## Decision

We will enhance the ADR tool in three phases:

### Phase 1: YAML Frontmatter Support

Add optional YAML frontmatter to ADR templates and parsing:

```yaml
---
title: "Use PostgreSQL for Primary Database"
status: accepted
date: 2025-01-15
authors:
  - Architecture Team
tags:
  - database
  - infrastructure
supersedes: 3
related:
  - 5
  - 12
---
```

**Implementation:**
- Extend `ADRMetadata` model with new optional fields
- Update `ADRParser` to detect and parse frontmatter (fall back to current
  parsing for backwards compatibility)
- Update `TemplateADRSerializer` to optionally emit frontmatter
- Add `--frontmatter` flag to `adr new` command
- Add `frontmatter = true` config option

### Phase 2: Documentation System Plugin Protocol

Create an abstraction layer for documentation system integration:

```python
class DocumentationAdapter(Protocol):
    """Protocol for documentation system plugins."""

    def generate_index(self, adrs: list[ADR]) -> str:
        """Generate an index/TOC for all ADRs."""
        ...

    def generate_nav_entry(self, adr: ADR) -> dict[str, Any]:
        """Generate navigation structure entry for an ADR."""
        ...

    def render_status_badge(self, status: ADRStatus) -> str:
        """Render a status indicator in the target format."""
        ...

    def render_cross_reference(self, adr_number: int) -> str:
        """Render a cross-reference to another ADR."""
        ...
```

**Sphinx Integration (Primary):**
- Sphinx extension: `adr.sphinx`
- Directive: `.. adr:: 0001` to embed ADR content
- Role: `:adr:`0001`` for cross-references
- Auto-generate RST index from ADR directory
- Status badges using Sphinx substitutions

**MkDocs Integration (Secondary):**
- MkDocs plugin: `adr.mkdocs`
- Auto-generate `nav` entries in `mkdocs.yml`
- Status badges using Material for MkDocs admonitions

### Phase 3: Enhanced Organization (Future)

Optional features for larger projects:

**Component Prefixes:**
```bash
adr new "Text Processing Pipeline" --prefix tp
# Creates: 0008-tp-text-processing-pipeline.md
```

**Sub-ADRs:**
```bash
adr new "Migration Plan" --parent 8
# Creates: 0008.1-migration-plan.md
```

**Frontmatter for sub-ADRs:**
```yaml
---
type: implementation-guide
parent_adr: 0008-tp-text-processing-pipeline.md
---
```

## Consequences

### Positive

- **Robust parsing**: YAML frontmatter is unambiguous and well-supported
- **Rich metadata**: Tags, relationships, custom fields without format changes
- **Documentation integration**: ADRs become first-class documentation
- **Sphinx-native**: Primary support for Python project documentation tool
- **Backwards compatible**: Existing ADRs continue to work
- **Extensible**: Plugin protocol allows community contributions

### Negative

- **Complexity**: More code to maintain (frontmatter parsing, plugins)
- **Dependencies**: May need optional dependencies for Sphinx/MkDocs
- **Migration effort**: Existing ADRs need updates to use frontmatter
- **Learning curve**: Users need to understand frontmatter syntax

### Neutral

- **Template changes**: New templates needed for frontmatter format
- **Config options**: More configuration surface area

## Alternatives Considered

1. **TOML frontmatter**: Less common in markdown ecosystem, YAML is standard
2. **Separate metadata files**: More files to manage, breaks locality
3. **Custom comment syntax**: Non-standard, tooling wouldn't recognize it
4. **MkDocs-first**: Sphinx more common in Python projects

## Open Questions

1. Should frontmatter be required for new ADRs or remain optional?
2. How should we handle ADRs that mix frontmatter and inline metadata?
3. Should the Sphinx extension be a separate package (`adr-sphinx`)?
4. What's the migration path for existing ADRs?

## Implementation Plan

1. **Phase 1** (Core):
   - Add frontmatter parsing to `ADRParser`
   - Extend `ADRMetadata` with new fields
   - Add frontmatter template variant
   - Update CLI with `--frontmatter` flag
   - Add config option

2. **Phase 2** (Sphinx):
   - Create `DocumentationAdapter` protocol
   - Implement `SphinxDocumentationAdapter`
   - Create Sphinx extension with directive and role
   - Document usage in README

3. **Phase 3** (Optional):
   - Component prefix support
   - Sub-ADR support
   - MkDocs adapter (community contribution welcome)
