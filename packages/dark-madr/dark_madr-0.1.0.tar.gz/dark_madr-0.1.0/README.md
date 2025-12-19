# dark-madr

A Python CLI for managing [Architecture Decision Records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

Compatible with [adr-tools](https://github.com/npryce/adr-tools) workflow. Supports Nygard and [MADR](https://adr.github.io/madr/) templates.

For background on ADRs, see the included paper: [Using ADR on GitHub](assets/Using.ADR.GitHub.pdf)

## Installation

```bash
pip install dark-madr
```

For development:

```bash
uv sync
uv pip install -e .
```

## Usage

```bash
# Initialize ADR directory
adr init

# Create a new ADR
adr new "Use PostgreSQL for primary database"

# List all ADRs
adr list

# Show a specific ADR
adr show 1

# Supersede an existing ADR
adr new "Use PostgreSQL 15" --supersedes 1

# Generate table of contents
adr generate toc
```

## Configuration

Configure defaults in `pyproject.toml`:

```toml
[tool.adr]
dir = "docs/decisions"
template = "madr"
default_status = "proposed"
default_authors = ["Architecture Team"]
```

Initialize configuration:

```bash
adr init-config
adr config  # view current settings
```

## Commands

| Command | Description |
|---------|-------------|
| `adr init` | Initialize ADR directory with first ADR |
| `adr new <title>` | Create a new ADR |
| `adr list` | List all ADRs |
| `adr show <number>` | Display an ADR |
| `adr generate toc` | Generate table of contents |
| `adr templates` | List available templates |
| `adr config` | Show current configuration |
| `adr init-config` | Add config section to pyproject.toml |

### Options

```bash
adr new "Title" --template madr    # Use specific template
adr new "Title" --status accepted  # Set initial status
adr new "Title" --supersedes 3     # Supersede ADR-0003
adr --adr-dir ./docs list          # Override ADR directory
```

## Templates

Two built-in templates:

- **nygard** (default) - Michael Nygard's original format
- **madr** - Markdown Any Decision Records format

View template structure:

```bash
adr help-template nygard
adr help-template madr
```

Custom templates can be added to a directory specified by `template_dir` in config.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run mypy src/
uv run ruff check src/
```

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Michael Nygard
- [Lightweight ADRs](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records) - ThoughtWorks Tech Radar (Adopt, Nov 2017)
- [adr-tools](https://github.com/npryce/adr-tools) - Nat Pryce
- [MADR](https://adr.github.io/madr/) - Markdown Any Decision Records

## License

MIT
