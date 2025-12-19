"""Repository interfaces for ADR domain."""

from __future__ import annotations

import contextlib
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from .models import ADR, ADRMetadata, ADRStatus

if TYPE_CHECKING:
    from adr.template_engine import ADRSerializer


class ADRRepository(Protocol):
    """Repository interface for managing ADRs."""

    def save(self, adr: ADR, template: str | None = None) -> None:
        """Save an ADR to the repository."""
        ...

    def find_by_number(self, number: int) -> ADR | None:
        """Find an ADR by its number."""
        ...

    def find_all(self) -> list[ADR]:
        """Find all ADRs in the repository."""
        ...

    def find_by_status(self, status: str) -> list[ADR]:
        """Find ADRs by status."""
        ...

    def get_next_number(self) -> int:
        """Get the next available ADR number."""
        ...

    def delete(self, number: int) -> bool:
        """Delete an ADR by number. Returns True if deleted, False if not found."""
        ...

    def exists(self, number: int) -> bool:
        """Check if an ADR with the given number exists."""
        ...


class ADRParser:
    """Parses markdown content into ADR objects."""

    def parse(self, content: str, number: int) -> ADR:
        """Parse markdown content into an ADR object."""
        lines = content.strip().split("\n")

        # Parse title from first heading
        title = "Untitled"
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                # Remove ADR number prefix if present
                title = re.sub(r"^(\d{4}\.\s*|ADR-\d{4}:\s*)", "", title)
                break

        # Parse status
        status = ADRStatus.PROPOSED
        status_match = re.search(
            r"(?:\*\s*Status:\s*|\*\*Status:\*\*\s*)(\w+)", content, re.IGNORECASE
        )
        if status_match:
            status_str = status_match.group(1).lower()
            status_map = {
                "proposed": ADRStatus.PROPOSED,
                "accepted": ADRStatus.ACCEPTED,
                "deprecated": ADRStatus.DEPRECATED,
                "superseded": ADRStatus.SUPERSEDED,
            }
            status = status_map.get(status_str, ADRStatus.PROPOSED)

        # Parse date
        date = datetime.now()
        date_match = re.search(
            r"(?:\*\s*Date:\s*|\*\*Date:\*\*\s*|Date:\s*)(\d{4}-\d{2}-\d{2})", content
        )
        if date_match:
            with contextlib.suppress(ValueError):
                date = datetime.strptime(date_match.group(1), "%Y-%m-%d")

        # Parse authors
        authors: list[str] = []
        authors_match = re.search(r"\*\s*Authors?:\s*(.+?)(?:\n|\*)", content)
        if authors_match:
            authors = [a.strip() for a in authors_match.group(1).split(",")]

        # Parse sections using regex
        def extract_section(pattern: str, default: str = "") -> str:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                section_content = match.group(1).strip()
                # Remove HTML comments
                section_content = re.sub(
                    r"<!--.*?-->", "", section_content, flags=re.DOTALL
                )
                return section_content.strip()
            return default

        context = extract_section(
            r"##\s*(?:Context and Problem Statement|Context)\s*\n(.*?)(?=\n##|\Z)"
        )
        decision = extract_section(r"##\s*Decision\s*\n(.*?)(?=\n##|\Z)")
        consequences = extract_section(r"##\s*Consequences\s*\n(.*?)(?=\n##|\Z)")
        alternatives = extract_section(
            r"##\s*(?:Considered Alternatives|Alternatives)\s*\n(.*?)(?=\n##|\Z)"
        )

        metadata = ADRMetadata(
            number=number,
            title=title,
            status=status,
            date=date,
            authors=authors,
        )

        return ADR(
            metadata=metadata,
            context=context,
            decision=decision,
            consequences=consequences,
            alternatives=alternatives if alternatives else None,
        )


class ADRRepositoryError(Exception):
    """Base exception for repository operations."""

    pass


class ADRNotFoundError(ADRRepositoryError):
    """Raised when an ADR is not found."""

    def __init__(self, number: int) -> None:
        self.number = number
        super().__init__(f"ADR with number {number} not found")


class ADRAlreadyExistsError(ADRRepositoryError):
    """Raised when trying to create an ADR that already exists."""

    def __init__(self, number: int) -> None:
        self.number = number
        super().__init__(f"ADR with number {number} already exists")


class FileSystemADRRepository(ADRRepository):
    """File system implementation of ADR repository."""

    def __init__(
        self,
        base_path: Path,
        serializer: ADRSerializer,
        parser: ADRParser | None = None,
    ) -> None:
        """Initialize repository with base path and serializer/parser.

        :param base_path: Path to the ADR directory
        :param serializer: Serializer for converting ADR to markdown
        :param parser: Optional parser for converting markdown to ADR
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._serializer = serializer
        self._parser = parser or ADRParser()

    def save(self, adr: ADR, template: str | None = None) -> None:
        """Save an ADR to the file system."""
        file_path = self.base_path / adr.filename

        # Check if file already exists and this is a new ADR
        if file_path.exists() and not self._is_update(adr):
            raise ADRAlreadyExistsError(adr.metadata.number)

        content = self._serializer.serialize(adr, template)

        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)

    def find_by_number(self, number: int) -> ADR | None:
        """Find an ADR by its number."""
        # Look for files matching the pattern NNNN-*.md
        pattern = f"{number:04d}-*.md"
        matching_files = list(self.base_path.glob(pattern))

        if not matching_files:
            return None

        # Take the first match (there should only be one)
        file_path = matching_files[0]

        try:
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()
                return self._parser.parse(content, number)
        except FileNotFoundError:
            return None

    def find_all(self) -> list[ADR]:
        """Find all ADRs in the repository."""
        adrs = []

        # Find all .md files that match ADR pattern
        for file_path in sorted(self.base_path.glob("????-*.md")):
            try:
                # Extract number from filename
                number_str = file_path.stem[:4]
                if number_str.isdigit():
                    number = int(number_str)
                    adr = self.find_by_number(number)
                    if adr:
                        adrs.append(adr)
            except (ValueError, IndexError):
                continue  # Skip invalid filenames

        return adrs

    def find_by_status(self, status: str) -> list[ADR]:
        """Find ADRs by status."""
        return [adr for adr in self.find_all() if adr.metadata.status.value == status]

    def get_next_number(self) -> int:
        """Get the next available ADR number."""
        existing_numbers = {
            int(f.stem[:4])
            for f in self.base_path.glob("????-*.md")
            if f.stem[:4].isdigit()
        }

        if not existing_numbers:
            return 1

        return max(existing_numbers) + 1

    def delete(self, number: int) -> bool:
        """Delete an ADR by number."""
        pattern = f"{number:04d}-*.md"
        matching_files = list(self.base_path.glob(pattern))

        if not matching_files:
            return False

        for file_path in matching_files:
            file_path.unlink()

        return True

    def exists(self, number: int) -> bool:
        """Check if an ADR with the given number exists."""
        pattern = f"{number:04d}-*.md"
        return bool(list(self.base_path.glob(pattern)))

    def _is_update(self, adr: ADR) -> bool:
        """Check if this is an update to an existing ADR."""
        return self.exists(adr.metadata.number)
