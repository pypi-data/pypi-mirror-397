"""Template engine for ADR generation."""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from .domain import ADR


class ADRSerializer(Protocol):
    """Protocol for serializing ADR objects to string format."""

    def serialize(self, adr: ADR, template: str | None = None) -> str:
        """Serialize an ADR to string format."""
        ...


class TemplateADRSerializer:
    """Serializes ADR objects using Jinja2 templates."""

    def __init__(self, template_engine: TemplateEngine) -> None:
        """Initialize serializer with template engine."""
        self.template_engine = template_engine

    def serialize(self, adr: ADR, template: str | None = None) -> str:
        """Serialize an ADR to markdown using templates."""
        template_name = template or "madr"

        # Build context from ADR object
        context = self._build_context(adr)

        # Check if we have a template for this format
        if self.template_engine.template_exists(template_name):
            return self.template_engine.render_adr_template(
                f"{template_name}.md", context
            )

        # Fallback to simple format if template not found
        return self._render_simple_format(adr)

    def _build_context(self, adr: ADR) -> dict[str, Any]:
        """Build template context from ADR object."""
        supersedes_list = []
        if adr.metadata.supersedes:
            supersedes_list = [f"ADR-{n:04d}" for n in adr.metadata.supersedes]

        superseded_by = None
        if adr.metadata.superseded_by:
            superseded_by = f"ADR-{adr.metadata.superseded_by:04d}"

        return {
            "number": f"{adr.metadata.number:04d}",
            "title": adr.metadata.title,
            "status": adr.metadata.status.value,
            "date": adr.metadata.date.strftime("%Y-%m-%d"),
            "authors": adr.metadata.authors,
            "supersedes": supersedes_list,
            "superseded_by": superseded_by,
            "context": adr.context,
            "decision": adr.decision,
            "consequences": adr.consequences,
            "alternatives": adr.alternatives,
        }

    def _render_simple_format(self, adr: ADR) -> str:
        """Render ADR in simple format (fallback)."""
        return f"""# ADR-{adr.metadata.number:04d}: {adr.metadata.title}

**Status:** {adr.metadata.status.value}
**Date:** {adr.metadata.date.strftime("%Y-%m-%d")}

## Context

{adr.context}

## Decision

{adr.decision}

## Consequences

{adr.consequences}
"""


class TemplateEngine:
    """Template engine for rendering ADR templates."""

    def __init__(self, template_dir: Path) -> None:
        """Initialize template engine with template directory."""
        self.template_dir = template_dir
        # Autoescape disabled: we generate markdown, not HTML
        self.env = Environment(  # nosec B701
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context."""
        template = self.env.get_template(template_name)
        result: str = template.render(**context)
        return result

    def render_adr_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with full ADR content.

        This method renders a template with actual content, not just
        placeholder comments. It uses the same templates but fills in
        the content sections.
        """
        template = self.env.get_template(template_name)
        rendered = template.render(**context)

        # If content fields are provided, we need to fill them in
        # The templates have HTML comments as placeholders
        if context.get("context"):
            # Replace context placeholder
            rendered = self._fill_section(
                rendered, "## Context and Problem Statement", context["context"]
            )
            rendered = self._fill_section(rendered, "## Context", context["context"])

        if context.get("decision"):
            rendered = self._fill_section(rendered, "## Decision", context["decision"])

        if context.get("consequences"):
            rendered = self._fill_section(
                rendered, "## Consequences", context["consequences"]
            )

        if context.get("alternatives"):
            rendered = self._fill_section(
                rendered, "## Considered Alternatives", context["alternatives"]
            )

        result: str = rendered
        return result

    def _fill_section(self, content: str, section_header: str, text: str) -> str:
        """Fill in a section's content after its header."""
        # Pattern to match section header followed by optional content until next section or end
        pattern = rf"({re.escape(section_header)}\n)(\n?)(<!--.*?-->)?"

        def replacement(match: re.Match[str]) -> str:
            return f"{match.group(1)}\n{text}\n"

        return re.sub(pattern, replacement, content, flags=re.DOTALL)

    def list_templates(self) -> list[str]:
        """List available templates."""
        templates = []
        for file_path in self.template_dir.glob("*.md"):
            templates.append(file_path.stem)
        return sorted(templates)

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists."""
        template_path = self.template_dir / f"{template_name}.md"
        return template_path.exists()


def open_in_editor(file_path: Path) -> None:
    """Open a file in the user's preferred editor."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")

    if editor:
        try:
            subprocess.run([editor, str(file_path)], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Could not open {file_path} with {editor}")
    else:
        print(f"ADR created: {file_path}")
        print("Set EDITOR environment variable to auto-open files")


def get_default_context(
    number: int, title: str, status: str = "proposed", authors: list[str] | None = None
) -> dict[str, Any]:
    """Get default context for template rendering."""
    return {
        "number": f"{number:04d}",
        "title": title,
        "status": status,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "authors": authors or [],
        "supersedes": [],
        "superseded_by": None,
    }
