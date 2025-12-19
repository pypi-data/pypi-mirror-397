"""Core ADR management functionality."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from .config import find_project_root, load_config
from .template_engine import TemplateEngine, get_default_context, open_in_editor


class ADRManager:
    """Manages Architecture Decision Records."""

    def __init__(self, adr_dir: Path, template_dir: Path | None = None) -> None:
        """Initialize ADR manager."""
        self.adr_dir = Path(adr_dir)
        self.adr_dir.mkdir(parents=True, exist_ok=True)

        # Use built-in templates if no custom template dir provided
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_engine = TemplateEngine(template_dir)

        # Load configuration for defaults
        project_root = find_project_root(self.adr_dir)
        self.config = load_config(project_root)

        self.default_template = self.config.template
        self.default_status = self.config.default_status
        self.default_authors = self.config.default_authors

    def init(self) -> Path:
        """Initialize ADR directory with first ADR."""
        if self.list_adrs():
            raise ValueError("ADR directory already initialized")

        # Create the first ADR about using ADRs
        first_adr_path = self.new_adr(
            title="Record architecture decisions",
            template="nygard",  # Always use nygard for the first ADR
            status="accepted",  # First ADR is always accepted
            open_editor=False,
        )

        # Fill in the first ADR content
        content = self._get_initial_adr_content()
        first_adr_path.write_text(content, encoding="utf-8")

        return first_adr_path

    def new_adr(
        self,
        title: str,
        template: str | None = None,
        status: str | None = None,
        authors: list[str] | None = None,
        open_editor: bool = True,
    ) -> Path:
        """Create a new ADR from template."""
        template_name = template or self.default_template
        effective_status = status or self.default_status
        effective_authors = authors or self.default_authors

        if not self.template_engine.template_exists(template_name):
            available = ", ".join(self.template_engine.list_templates())
            raise ValueError(
                f"Template '{template_name}' not found. Available: {available}"
            )

        number = self._get_next_number()
        filename = self._generate_filename(number, title)
        file_path = self.adr_dir / filename

        context = get_default_context(
            number, title, effective_status, effective_authors
        )
        content = self.template_engine.render_template(f"{template_name}.md", context)

        file_path.write_text(content, encoding="utf-8")

        if open_editor:
            open_in_editor(file_path)

        return file_path

    def list_adrs(self) -> list[tuple[int, str, Path]]:
        """List all ADRs as (number, title, path) tuples."""
        adrs = []

        for file_path in sorted(self.adr_dir.glob("*.md")):
            number, title = self._parse_filename(file_path.name)
            if number is not None:
                adrs.append((number, title, file_path))

        return sorted(adrs, key=lambda x: x[0])

    def get_adr_path(self, number: int) -> Path | None:
        """Get path to ADR by number."""
        for adr_number, _, path in self.list_adrs():
            if adr_number == number:
                return path
        return None

    def supersede_adr(
        self,
        old_number: int,
        new_title: str,
        template: str | None = None,
    ) -> tuple[Path, Path]:
        """Create a new ADR that supersedes an existing one."""
        old_path = self.get_adr_path(old_number)
        if not old_path:
            raise ValueError(f"ADR {old_number} not found")

        # Create new ADR
        new_path = self.new_adr(
            title=new_title,
            template=template,
            status=self.default_status,
            open_editor=False,
        )

        # Update old ADR status
        self._update_adr_status(
            old_path, f"superseded by {self._get_next_number() - 1:04d}"
        )

        # Add supersession note to new ADR
        self._add_supersession_note(new_path, old_number)

        return old_path, new_path

    def generate_toc(self) -> str:
        """Generate a table of contents for all ADRs."""
        adrs = self.list_adrs()

        if not adrs:
            return "No ADRs found.\n"

        lines = ["# Architecture Decision Records\n"]

        for number, title, path in adrs:
            status = self._extract_status(path)
            relative_path = path.relative_to(self.adr_dir)
            lines.append(f"* [ADR-{number:04d}]({relative_path}) - {title} - {status}")

        return "\n".join(lines) + "\n"

    def _get_next_number(self) -> int:
        """Get the next ADR number."""
        adrs = self.list_adrs()
        if not adrs:
            return 1
        return max(adr[0] for adr in adrs) + 1

    def _generate_filename(self, number: int, title: str) -> str:
        """Generate filename for ADR."""
        # Convert title to lowercase, replace spaces/special chars with hyphens
        safe_title = re.sub(r"[^a-zA-Z0-9\s-]", "", title.lower())
        safe_title = re.sub(r"\s+", "-", safe_title).strip("-")

        return f"{number:04d}-{safe_title}.md"

    def _parse_filename(self, filename: str) -> tuple[int | None, str]:
        """Parse ADR number and title from filename."""
        match = re.match(r"^(\d{4})-(.+)\.md$", filename)
        if match:
            number = int(match.group(1))
            title = match.group(2).replace("-", " ").title()
            return number, title
        return None, filename

    def _extract_status(self, file_path: Path) -> str:
        """Extract status from ADR file."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Look for status in different formats
            status_patterns = [
                r"## Status\s*\n\s*([^\n]+)",  # Nygard format
                r"\* Status:\s*([^\n]+)",  # MADR format
                r"Status:\s*([^\n]+)",  # Simple format
            ]

            for pattern in status_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            return "unknown"
        except Exception:
            return "unknown"

    def _update_adr_status(self, file_path: Path, new_status: str) -> None:
        """Update the status of an ADR."""
        content = file_path.read_text(encoding="utf-8")

        # Update status in different formats
        status_patterns = [
            (r"(## Status\s*\n\s*)([^\n]+)", f"\\g<1>{new_status}"),
            (r"(\* Status:\s*)([^\n]+)", f"\\g<1>{new_status}"),
            (r"(Status:\s*)([^\n]+)", f"\\g<1>{new_status}"),
        ]

        for pattern, replacement in status_patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                return

    def _add_supersession_note(self, file_path: Path, old_number: int) -> None:
        """Add a note about superseding another ADR."""
        content = file_path.read_text(encoding="utf-8")

        supersession_note = (
            f"\nThis ADR supersedes [ADR-{old_number:04d}]({old_number:04d}-*.md).\n"
        )

        # Add after the title or status section
        if "## Context" in content:
            content = content.replace("## Context", f"{supersession_note}\n## Context")
        elif "## Status" in content:
            content = content.replace("## Status", f"{supersession_note}\n## Status")
        else:
            # Add at the end
            content += supersession_note

        file_path.write_text(content, encoding="utf-8")

    def _get_initial_adr_content(self) -> str:
        """Get content for the initial ADR about using ADRs."""
        return """# 0001. Record architecture decisions

Date: {date}

## Status

Accepted

## Context

We need to record the architectural decisions made on this project.

## Decision

We will use Architecture Decision Records, as described by Michael Nygard in this article: http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions

## Consequences

See Michael Nygard's article, linked above. For a lightweight ADR toolset, see Nat Pryce's adr-tools at https://github.com/npryce/adr-tools.
""".format(date=datetime.now().strftime("%Y-%m-%d"))
