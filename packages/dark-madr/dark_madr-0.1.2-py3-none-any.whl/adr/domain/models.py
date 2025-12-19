"""Domain models for Architecture Decision Records."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ADRStatus(str, Enum):
    """Status of an Architecture Decision Record."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class ADRMetadata(BaseModel):
    """Metadata for an ADR."""

    id: UUID = Field(default_factory=uuid4)
    number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    status: ADRStatus = ADRStatus.PROPOSED
    date: datetime = Field(default_factory=datetime.now)
    authors: list[str] = Field(default_factory=list)
    supersedes: list[int] | None = None
    superseded_by: int | None = None

    @field_validator("title")
    @classmethod
    def title_must_be_meaningful(cls, v: str) -> str:
        """Ensure title is meaningful."""
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip()


class ADR(BaseModel):
    """Architecture Decision Record."""

    metadata: ADRMetadata
    context: str = Field(description="The architectural context and problem")
    decision: str = Field(description="The architectural decision made")
    consequences: str = Field(description="Consequences of the decision")
    alternatives: str | None = Field(
        default=None, description="Alternative solutions considered"
    )

    def __str__(self) -> str:
        """String representation of the ADR."""
        return f"ADR-{self.metadata.number:04d}: {self.metadata.title}"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"ADR(number={self.metadata.number}, "
            f"title='{self.metadata.title}', "
            f"status={self.metadata.status.value})"
        )

    @property
    def filename(self) -> str:
        """Generate filename for this ADR."""
        safe_title = "".join(
            c if c.isalnum() or c in "-_" else "-" for c in self.metadata.title.lower()
        )
        # Collapse multiple hyphens and strip leading/trailing hyphens
        safe_title = re.sub(r"-+", "-", safe_title).strip("-")
        return f"{self.metadata.number:04d}-{safe_title}.md"

    @property
    def is_active(self) -> bool:
        """Check if this ADR is currently active."""
        return self.metadata.status in {ADRStatus.PROPOSED, ADRStatus.ACCEPTED}

    def supersede(self, superseding_adr_number: int) -> None:
        """Mark this ADR as superseded by another."""
        self.metadata.status = ADRStatus.SUPERSEDED
        self.metadata.superseded_by = superseding_adr_number

    def accept(self) -> None:
        """Accept this ADR."""
        self.metadata.status = ADRStatus.ACCEPTED

    def deprecate(self) -> None:
        """Deprecate this ADR."""
        self.metadata.status = ADRStatus.DEPRECATED
