"""Command-line interface for ADR management."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .adr_manager import ADRManager
from .config import (
    find_project_root,
    get_effective_adr_dir,
    get_effective_template_dir,
    load_config,
    save_config_example,
)

console = Console()


@click.group()
@click.option(
    "--adr-dir",
    help="Directory for ADR files (overrides config)",
    type=click.Path(path_type=Path),
)
@click.option(
    "--template-dir",
    help="Directory for custom templates (overrides config)",
    type=click.Path(path_type=Path),
)
@click.pass_context
def cli(ctx: click.Context, adr_dir: Path | None, template_dir: Path | None) -> None:
    """Architecture Decision Records tool.

    Configuration is loaded from pyproject.toml [tool.adr] section.
    Command line options override configuration values.
    """
    ctx.ensure_object(dict)

    # Find project root and load configuration
    project_root = find_project_root(Path.cwd())
    config = load_config(project_root)

    # Use command line overrides or fall back to config
    effective_adr_dir = adr_dir or get_effective_adr_dir(project_root)
    effective_template_dir = template_dir or get_effective_template_dir(project_root)

    ctx.obj["manager"] = ADRManager(effective_adr_dir, effective_template_dir)
    ctx.obj["config"] = config
    ctx.obj["project_root"] = project_root


@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize the ADR directory."""
    manager: ADRManager = ctx.obj["manager"]

    try:
        first_adr = manager.init()
        console.print(f"Initialized ADR directory: {manager.adr_dir}", style="green")
        console.print(f"Created first ADR: {first_adr.name}")

    except ValueError as e:
        console.print(f"Error: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("title")
@click.option(
    "--template",
    "-t",
    help="Template to use (overrides config default)",
)
@click.option(
    "--supersedes",
    "-s",
    type=int,
    help="Number of ADR this supersedes",
)
@click.option(
    "--status",
    help="Status for the new ADR (overrides config default)",
)
@click.pass_context
def new(
    ctx: click.Context,
    title: str,
    template: str | None,
    supersedes: int | None,
    status: str | None,
) -> None:
    """Create a new ADR using configured defaults.

    Template and status can be overridden with --template and --status flags.
    Configure defaults in pyproject.toml [tool.adr] section.
    """
    manager: ADRManager = ctx.obj["manager"]
    config = ctx.obj["config"]

    # Use command line overrides or fall back to config
    effective_template = template or config.template
    effective_status = status or config.default_status

    try:
        if supersedes:
            old_path, new_path = manager.supersede_adr(
                supersedes, title, effective_template
            )
            console.print(
                f"Created {new_path.name} superseding {old_path.name}", style="green"
            )
        else:
            new_path = manager.new_adr(title, effective_template, effective_status)
            console.print(f"Created {new_path.name}", style="green")

    except Exception as e:
        console.print(f"Error: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List all ADRs."""
    manager: ADRManager = ctx.obj["manager"]

    adrs = manager.list_adrs()

    if not adrs:
        console.print("No ADRs found. Run 'adr init' to get started.", style="yellow")
        return

    table = Table(title="Architecture Decision Records")
    table.add_column("Number", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Status", style="magenta")
    table.add_column("File", style="dim")

    for number, title, path in adrs:
        status = manager._extract_status(path)
        table.add_row(
            f"ADR-{number:04d}",
            title,
            status,
            path.name,
        )

    console.print(table)


@cli.command()
@click.argument("number", type=int)
@click.pass_context
def show(ctx: click.Context, number: int) -> None:
    """Show the content of an ADR."""
    manager: ADRManager = ctx.obj["manager"]

    adr_path = manager.get_adr_path(number)
    if not adr_path:
        console.print(f"ADR {number} not found", style="red")
        sys.exit(1)

    try:
        content = adr_path.read_text(encoding="utf-8")
        console.print(f"\n[bold cyan]File: {adr_path.name}[/bold cyan]\n")
        console.print(content)

    except Exception as e:
        console.print(f"Error reading ADR: {e}", style="red")
        sys.exit(1)


@cli.command("generate")
@click.argument("what", type=click.Choice(["toc"]))
@click.pass_context
def generate_cmd(ctx: click.Context, what: str) -> None:
    """Generate various outputs."""
    manager: ADRManager = ctx.obj["manager"]

    if what == "toc":
        toc = manager.generate_toc()
        console.print(toc)


@cli.command()
@click.pass_context
def templates(ctx: click.Context) -> None:
    """List available templates."""
    manager: ADRManager = ctx.obj["manager"]
    config = ctx.obj["config"]

    available_templates = manager.template_engine.list_templates()

    console.print("\n[bold]Available Templates:[/bold]")
    for template in available_templates:
        marker = " (default)" if template == config.template else ""
        console.print(f"  - {template}{marker}")

    console.print(f"\nDefault from config: [cyan]{config.template}[/cyan]")
    console.print(
        f'Override with: [cyan]adr new "My Decision" --template {available_templates[0] if available_templates else "custom"}[/cyan]'
    )


@cli.command()
@click.argument("template_name")
@click.pass_context
def help_template(ctx: click.Context, template_name: str) -> None:
    """Show template content."""
    manager: ADRManager = ctx.obj["manager"]

    if not manager.template_engine.template_exists(template_name):
        available = ", ".join(manager.template_engine.list_templates())
        console.print(f"Template '{template_name}' not found", style="red")
        console.print(f"Available templates: {available}")
        sys.exit(1)

    try:
        template_path = manager.template_engine.template_dir / f"{template_name}.md"
        content = template_path.read_text(encoding="utf-8")

        console.print(f"\n[bold cyan]Template: {template_name}[/bold cyan]\n")
        console.print(content)

    except Exception as e:
        console.print(f"Error reading template: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Show current configuration."""
    manager: ADRManager = ctx.obj["manager"]
    config = ctx.obj["config"]
    project_root = ctx.obj["project_root"]

    console.print("\n[bold]ADR Configuration:[/bold]")

    # Project info
    if project_root:
        console.print(f"  Project Root: {project_root.absolute()}")
        pyproject_path = project_root / "pyproject.toml"
        has_config = (
            pyproject_path.exists() and "[tool.adr]" in pyproject_path.read_text()
        )
        console.print(f"  Has Config: {'Yes' if has_config else 'No (using defaults)'}")
    else:
        console.print("  Project Root: [dim]Not found (using current directory)[/dim]")

    # Current settings
    console.print("\n[bold]Current Settings:[/bold]")
    console.print(f"  ADR Directory: {manager.adr_dir.absolute()}")
    console.print(
        f"  Template Directory: {manager.template_engine.template_dir.absolute()}"
    )
    console.print(f"  Default Template: {config.template}")
    console.print(f"  Default Status: {config.default_status}")
    console.print(f"  Default Authors: {config.default_authors or 'None'}")

    # ADR stats
    adr_count = len(manager.list_adrs())
    console.print("\n[bold]Statistics:[/bold]")
    console.print(f"  Total ADRs: {adr_count}")


@cli.command("init-config")
@click.pass_context
def init_config(ctx: click.Context) -> None:
    """Initialize ADR configuration in pyproject.toml."""
    project_root = ctx.obj["project_root"]

    if not project_root:
        console.print(
            "No pyproject.toml found in current directory or parents", style="red"
        )
        console.print("Run this command from a Python project directory.")
        sys.exit(1)

    try:
        save_config_example(project_root)
        console.print(
            f"Added ADR configuration to {project_root / 'pyproject.toml'}",
            style="green",
        )
        console.print("\nEdit the [tool.adr] section to customize settings:")
        console.print("  - dir: Directory for ADR files")
        console.print("  - template: Default template (nygard, madr)")
        console.print("  - default_status: Default status for new ADRs")
        console.print("  - default_authors: Default authors list")

    except Exception as e:
        console.print(f"Error creating config: {e}", style="red")
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
