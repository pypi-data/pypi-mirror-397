"""Configuration management for ADR tool."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ADR_DIR = "doc/adr"
DEFAULT_TEMPLATE = "nygard"


@dataclass
class ADRConfig:
    """Configuration for ADR tool."""

    adr_dir: str = DEFAULT_ADR_DIR
    template: str = DEFAULT_TEMPLATE
    template_dir: str | None = None
    default_status: str = "proposed"
    default_authors: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.default_authors is None:
            self.default_authors = []


def find_project_root(start_path: Path) -> Path | None:
    """Find the project root by looking for pyproject.toml."""
    current = Path(start_path).resolve()

    # Walk up the directory tree
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent

    return None


def load_config(project_dir: Path | None = None) -> ADRConfig:
    """Load ADR configuration from pyproject.toml."""
    if project_dir is None:
        project_dir = find_project_root(Path.cwd())

    if not project_dir:
        return ADRConfig()

    pyproject_path = project_dir / "pyproject.toml"
    if not pyproject_path.exists():
        return ADRConfig()

    try:
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        adr_config = data.get("tool", {}).get("adr", {})

        return ADRConfig(
            adr_dir=adr_config.get("dir", DEFAULT_ADR_DIR),
            template=adr_config.get("template", DEFAULT_TEMPLATE),
            template_dir=adr_config.get("template_dir"),
            default_status=adr_config.get("default_status", "proposed"),
            default_authors=adr_config.get("default_authors", []),
        )

    except Exception:
        # If there's any error loading config, fall back to defaults
        return ADRConfig()


def get_effective_adr_dir(project_dir: Path | None = None) -> Path:
    """Get the effective ADR directory based on configuration."""
    if project_dir is None:
        project_dir = find_project_root(Path.cwd())

    config = load_config(project_dir)

    if project_dir and not Path(config.adr_dir).is_absolute():
        return project_dir / config.adr_dir
    else:
        return Path(config.adr_dir)


def get_effective_template_dir(project_dir: Path | None = None) -> Path | None:
    """Get the effective template directory based on configuration."""
    config = load_config(project_dir)

    if not config.template_dir:
        return None

    template_dir = Path(config.template_dir)

    if project_dir and not template_dir.is_absolute():
        return project_dir / template_dir
    else:
        return template_dir


def save_config_example(project_dir: Path) -> None:
    """Save an example configuration to pyproject.toml."""
    pyproject_path = project_dir / "pyproject.toml"

    example_config = """
# ADR tool configuration
[tool.adr]
# Directory for ADR files (relative to project root)
dir = "docs/decisions"

# Default template to use
template = "madr"

# Optional: Custom template directory
# template_dir = "custom_templates"

# Default status for new ADRs
default_status = "proposed"

# Default authors for new ADRs
default_authors = ["Team Architecture"]
"""

    if pyproject_path.exists():
        content = pyproject_path.read_text()
        if "[tool.adr]" not in content:
            # Append to existing file
            with pyproject_path.open("a") as f:
                f.write(example_config)
    else:
        # Create new pyproject.toml
        pyproject_path.write_text(example_config.strip())
