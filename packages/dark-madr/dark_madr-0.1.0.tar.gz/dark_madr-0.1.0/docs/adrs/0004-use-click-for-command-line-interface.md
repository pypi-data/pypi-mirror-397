---
title: Use Click for Command Line Interface
status: accepted
date: 2025-12-16
authors:
  - m1yag1
tags:
  - cli
  - tooling
---

# 0004. Use Click for Command Line Interface

Date: 2025-12-16

## Status

accepted

## Context

The ADR tool needs a command-line interface for users to manage architecture
decision records. Python offers several CLI frameworks:

1. **argparse** - Standard library, verbose, limited features
2. **Click** - Decorator-based, composable, rich features
3. **Typer** - Built on Click, uses type hints for arguments
4. **Fire** - Auto-generates CLI from functions/classes

Requirements for the CLI:
- Subcommands (`adr new`, `adr list`, `adr show`, etc.)
- Options with validation (`--status`, `--template`)
- Global options (`--adr-dir`)
- Help text generation
- Testability with `CliRunner`

## Decision

We will use Click for the command-line interface:

```python
import click

@click.group()
@click.option("--adr-dir", type=click.Path(), help="ADR directory")
@click.pass_context
def cli(ctx: click.Context, adr_dir: str | None) -> None:
    ctx.ensure_object(dict)
    ctx.obj["adr_dir"] = adr_dir

@cli.command()
@click.argument("title")
@click.option("--template", default="nygard")
@click.pass_context
def new(ctx: click.Context, title: str, template: str) -> None:
    """Create a new ADR."""
    ...
```

Combined with Rich for enhanced terminal output (tables, colors, formatting).

## Consequences

### Positive

- **Decorator syntax**: Clean, readable command definitions
- **Composable**: Commands can be grouped and nested easily
- **Context passing**: Share state between commands via `@click.pass_context`
- **Built-in testing**: `CliRunner` makes CLI testing straightforward
- **Rich integration**: Works well with Rich for pretty output
- **Widely adopted**: Large community, good documentation
- **Type support**: Good mypy compatibility

### Negative

- **External dependency**: Not in standard library
- **Learning curve**: Decorator patterns can be confusing initially
- **Less type-driven**: Typer would infer types from annotations
