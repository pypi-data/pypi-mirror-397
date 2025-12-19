"""Application services for ADR management."""

from __future__ import annotations

from datetime import datetime

from .domain import (
    ADR,
    ADRMetadata,
    ADRNotFoundError,
    ADRRepository,
    ADRStatus,
)


class ADRService:
    """Service for managing ADRs."""

    def __init__(self, repository: ADRRepository) -> None:
        """Initialize service with repository."""
        self.repository = repository

    def create_adr(
        self,
        title: str,
        context: str = "",
        decision: str = "",
        consequences: str = "",
        authors: list[str] | None = None,
        status: ADRStatus = ADRStatus.PROPOSED,
    ) -> ADR:
        """Create a new ADR."""
        number = self.repository.get_next_number()

        metadata = ADRMetadata(
            number=number,
            title=title,
            status=status,
            date=datetime.now(),
            authors=authors or [],
        )

        adr = ADR(
            metadata=metadata,
            context=context,
            decision=decision,
            consequences=consequences,
        )

        self.repository.save(adr)
        return adr

    def get_adr(self, number: int) -> ADR:
        """Get an ADR by number."""
        adr = self.repository.find_by_number(number)
        if not adr:
            raise ADRNotFoundError(number)
        return adr

    def list_adrs(self) -> list[ADR]:
        """List all ADRs."""
        return self.repository.find_all()

    def list_adrs_by_status(self, status: str) -> list[ADR]:
        """List ADRs by status."""
        return self.repository.find_by_status(status)

    def accept_adr(self, number: int) -> ADR:
        """Accept an ADR."""
        adr = self.get_adr(number)
        adr.accept()
        self.repository.save(adr)
        return adr

    def deprecate_adr(self, number: int) -> ADR:
        """Deprecate an ADR."""
        adr = self.get_adr(number)
        adr.deprecate()
        self.repository.save(adr)
        return adr

    def supersede_adr(
        self,
        old_number: int,
        new_title: str,
        context: str = "",
        decision: str = "",
        consequences: str = "",
        authors: list[str] | None = None,
    ) -> tuple[ADR, ADR]:
        """Create a new ADR that supersedes an existing one."""
        # Get the old ADR
        old_adr = self.get_adr(old_number)

        # Create the new ADR
        new_adr = self.create_adr(
            title=new_title,
            context=context or f"This ADR supersedes ADR-{old_number:04d}.",
            decision=decision,
            consequences=consequences,
            authors=authors,
        )

        # Update relationships
        old_adr.supersede(new_adr.metadata.number)
        new_adr.metadata.supersedes = [old_number]

        # Save both ADRs
        self.repository.save(old_adr)
        self.repository.save(new_adr)

        return old_adr, new_adr

    def update_adr(
        self,
        number: int,
        title: str | None = None,
        context: str | None = None,
        decision: str | None = None,
        consequences: str | None = None,
        alternatives: str | None = None,
        authors: list[str] | None = None,
    ) -> ADR:
        """Update an existing ADR."""
        adr = self.get_adr(number)

        # Update fields if provided
        if title is not None:
            adr.metadata.title = title
        if context is not None:
            adr.context = context
        if decision is not None:
            adr.decision = decision
        if consequences is not None:
            adr.consequences = consequences
        if alternatives is not None:
            adr.alternatives = alternatives
        if authors is not None:
            adr.metadata.authors = authors

        self.repository.save(adr)
        return adr

    def delete_adr(self, number: int) -> bool:
        """Delete an ADR."""
        if not self.repository.exists(number):
            raise ADRNotFoundError(number)

        return self.repository.delete(number)

    def get_statistics(self) -> dict[str, int]:
        """Get statistics about ADRs."""
        adrs = self.list_adrs()

        stats = {
            "total": len(adrs),
            "proposed": 0,
            "accepted": 0,
            "deprecated": 0,
            "superseded": 0,
        }

        for adr in adrs:
            stats[adr.metadata.status.value] += 1

        return stats
