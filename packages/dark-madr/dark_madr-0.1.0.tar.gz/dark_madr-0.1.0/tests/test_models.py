"""Tests for ADR domain models."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from adr.domain import ADR, ADRMetadata, ADRStatus

if TYPE_CHECKING:
    from adr import TemplateADRSerializer


class TestADRMetadata:
    """Test ADRMetadata model."""

    def test_create_basic_metadata(self) -> None:
        """Test creating basic metadata."""
        metadata = ADRMetadata(
            number=1,
            title="Test ADR",
        )

        assert metadata.number == 1
        assert metadata.title == "Test ADR"
        assert metadata.status == ADRStatus.PROPOSED
        assert isinstance(metadata.id, UUID)
        assert isinstance(metadata.date, datetime)

    def test_title_validation(self) -> None:
        """Test title validation."""
        with pytest.raises(ValueError, match="Title must be at least 3 characters"):
            ADRMetadata(number=1, title="Hi")

    def test_title_strip_whitespace(self) -> None:
        """Test title whitespace is stripped."""
        metadata = ADRMetadata(number=1, title="  Test ADR  ")
        assert metadata.title == "Test ADR"


class TestADR:
    """Test ADR model."""

    def test_create_basic_adr(self) -> None:
        """Test creating a basic ADR."""
        metadata = ADRMetadata(number=1, title="Test Decision")
        adr = ADR(
            metadata=metadata,
            context="We need to decide something",
            decision="We decided to do X",
            consequences="This will result in Y",
        )

        assert adr.metadata.number == 1
        assert adr.context == "We need to decide something"
        assert adr.decision == "We decided to do X"
        assert adr.consequences == "This will result in Y"

    def test_filename_generation(self) -> None:
        """Test filename generation."""
        metadata = ADRMetadata(number=5, title="Use PostgreSQL Database")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )

        assert adr.filename == "0005-use-postgresql-database.md"

    def test_filename_with_special_chars(self) -> None:
        """Test filename generation with special characters."""
        metadata = ADRMetadata(number=1, title="Use React/TypeScript & Docker!")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )

        assert adr.filename == "0001-use-react-typescript-docker.md"

    def test_is_active(self) -> None:
        """Test is_active property."""
        metadata = ADRMetadata(number=1, title="Test")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )

        # Proposed ADRs are active
        assert adr.is_active is True

        # Accepted ADRs are active
        adr.accept()
        assert adr.is_active is True

        # Deprecated ADRs are not active
        adr.deprecate()
        assert adr.is_active is False

    def test_is_active_superseded(self) -> None:
        """Test that superseded ADRs are not active."""
        metadata = ADRMetadata(number=1, title="Test")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )
        adr.supersede(2)
        assert adr.is_active is False

    def test_accept_status(self) -> None:
        """Test accept method changes status."""
        metadata = ADRMetadata(number=1, title="Test")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )
        adr.accept()
        assert adr.metadata.status == ADRStatus.ACCEPTED

    def test_deprecate_status(self) -> None:
        """Test deprecate method changes status."""
        metadata = ADRMetadata(number=1, title="Test")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )
        adr.deprecate()
        assert adr.metadata.status == ADRStatus.DEPRECATED

    def test_supersede_status(self) -> None:
        """Test supersede method changes status and sets superseded_by."""
        metadata = ADRMetadata(number=1, title="Test")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )
        adr.supersede(5)
        assert adr.metadata.status == ADRStatus.SUPERSEDED
        assert adr.metadata.superseded_by == 5

    def test_to_markdown_madr_format(self, serializer: "TemplateADRSerializer") -> None:
        """Test markdown generation in MADR format using serializer."""
        metadata = ADRMetadata(
            number=1,
            title="Use PostgreSQL",
            authors=["John Doe", "Jane Smith"],
        )
        adr = ADR(
            metadata=metadata,
            context="We need a reliable database",
            decision="We will use PostgreSQL",
            consequences="Better data consistency",
            alternatives="We considered MySQL and MongoDB",
        )

        markdown = serializer.serialize(adr, "madr")

        assert "# Use PostgreSQL" in markdown
        assert "* Status: proposed" in markdown
        assert "* Authors: John Doe, Jane Smith" in markdown
        assert "## Context and Problem Statement" in markdown
        assert "We need a reliable database" in markdown
        assert "## Decision" in markdown
        assert "We will use PostgreSQL" in markdown
        assert "## Consequences" in markdown
        assert "Better data consistency" in markdown
        assert "## Considered Alternatives" in markdown
        assert "We considered MySQL and MongoDB" in markdown

    def test_string_representations(self) -> None:
        """Test string representations."""
        metadata = ADRMetadata(number=5, title="Test Decision")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )

        assert str(adr) == "ADR-0005: Test Decision"
        assert "ADR(number=5" in repr(adr)
        assert "title='Test Decision'" in repr(adr)
        assert "status=proposed" in repr(adr)
