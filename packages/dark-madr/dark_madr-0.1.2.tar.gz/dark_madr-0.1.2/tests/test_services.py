"""Tests for ADR services."""

import pytest

from adr.domain import ADRNotFoundError, ADRStatus
from adr.services import ADRService


class TestADRService:
    """Test ADRService."""

    def test_create_adr(self, service: ADRService) -> None:
        """Test creating an ADR."""
        adr = service.create_adr(
            title="Test Decision",
            context="We need to test something",
            decision="We decided to use pytest",
            consequences="Better test coverage",
            authors=["Test Author"],
        )

        assert adr.metadata.number == 1
        assert adr.metadata.title == "Test Decision"
        assert adr.context == "We need to test something"
        assert adr.metadata.authors == ["Test Author"]
        assert adr.metadata.status == ADRStatus.PROPOSED

    def test_get_adr(self, service: ADRService) -> None:
        """Test getting an ADR."""
        # Create an ADR first
        created_adr = service.create_adr(
            title="Test Decision",
            context="context",
            decision="decision",
            consequences="consequences",
        )

        # Get it back
        retrieved_adr = service.get_adr(created_adr.metadata.number)

        assert retrieved_adr.metadata.title == "Test Decision"
        assert retrieved_adr.context == "context"

    def test_get_nonexistent_adr(self, service: ADRService) -> None:
        """Test getting a nonexistent ADR raises error."""
        with pytest.raises(ADRNotFoundError):
            service.get_adr(999)

    def test_list_adrs(self, service: ADRService) -> None:
        """Test listing ADRs."""
        # Initially empty
        assert service.list_adrs() == []

        # Create some ADRs
        service.create_adr(
            title="First ADR", context="c", decision="d", consequences="cons"
        )
        service.create_adr(
            title="Second ADR", context="c", decision="d", consequences="cons"
        )

        adrs = service.list_adrs()
        assert len(adrs) == 2
        assert adrs[0].metadata.title == "First ADR"
        assert adrs[1].metadata.title == "Second ADR"

    def test_accept_adr(self, service: ADRService) -> None:
        """Test accepting an ADR."""
        adr = service.create_adr(
            title="Test", context="c", decision="d", consequences="cons"
        )

        accepted_adr = service.accept_adr(adr.metadata.number)

        assert accepted_adr.metadata.status == ADRStatus.ACCEPTED

    def test_deprecate_adr(self, service: ADRService) -> None:
        """Test deprecating an ADR."""
        adr = service.create_adr(
            title="Test", context="c", decision="d", consequences="cons"
        )

        deprecated_adr = service.deprecate_adr(adr.metadata.number)

        assert deprecated_adr.metadata.status == ADRStatus.DEPRECATED

    def test_supersede_adr(self, service: ADRService) -> None:
        """Test superseding an ADR."""
        old_adr = service.create_adr(
            title="Old Decision", context="c", decision="d", consequences="cons"
        )

        old_updated, new_adr = service.supersede_adr(
            old_number=old_adr.metadata.number,
            new_title="New Decision",
            context="Updated context",
            decision="Updated decision",
            consequences="Updated consequences",
        )

        # Check old ADR is superseded
        assert old_updated.metadata.status == ADRStatus.SUPERSEDED
        assert old_updated.metadata.superseded_by == new_adr.metadata.number

        # Check new ADR supersedes old one
        assert new_adr.metadata.supersedes == [old_adr.metadata.number]
        assert new_adr.metadata.title == "New Decision"

    def test_update_adr(self, service: ADRService) -> None:
        """Test updating an ADR."""
        adr = service.create_adr(
            title="Original", context="c", decision="d", consequences="cons"
        )

        updated_adr = service.update_adr(
            number=adr.metadata.number,
            title="Updated Title",
            context="Updated context",
        )

        assert updated_adr.metadata.title == "Updated Title"
        assert updated_adr.context == "Updated context"
        assert updated_adr.decision == "d"  # Unchanged

    def test_get_statistics(self, service: ADRService) -> None:
        """Test getting ADR statistics."""
        # Create ADRs with different statuses
        adr1 = service.create_adr(
            title="ADR 1", context="c", decision="d", consequences="cons"
        )
        adr2 = service.create_adr(
            title="ADR 2", context="c", decision="d", consequences="cons"
        )
        service.create_adr(
            title="ADR 3", context="c", decision="d", consequences="cons"
        )

        service.accept_adr(adr1.metadata.number)
        service.deprecate_adr(adr2.metadata.number)
        # Third ADR remains proposed

        stats = service.get_statistics()

        assert stats["total"] == 3
        assert stats["proposed"] == 1
        assert stats["accepted"] == 1
        assert stats["deprecated"] == 1
        assert stats["superseded"] == 0
