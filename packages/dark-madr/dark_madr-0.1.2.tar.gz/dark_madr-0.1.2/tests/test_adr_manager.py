"""Tests for ADR manager."""

from pathlib import Path

import pytest

from adr.adr_manager import ADRManager


class TestADRManager:
    """Test ADRManager."""

    def test_init_creates_first_adr(self, temp_dir: Path) -> None:
        """Test that init creates the first ADR."""
        manager = ADRManager(temp_dir)

        first_adr = manager.init()

        assert first_adr.exists()
        assert first_adr.name == "0001-record-architecture-decisions.md"

        content = first_adr.read_text()
        assert "Record architecture decisions" in content
        assert "Michael Nygard" in content

    def test_init_fails_if_already_initialized(self, temp_dir: Path) -> None:
        """Test that init fails if directory already has ADRs."""
        manager = ADRManager(temp_dir)
        manager.init()

        with pytest.raises(ValueError, match="already initialized"):
            manager.init()

    def test_new_adr_creates_file(self, temp_dir: Path) -> None:
        """Test creating a new ADR."""
        manager = ADRManager(temp_dir)

        adr_path = manager.new_adr("Use PostgreSQL", open_editor=False)

        assert adr_path.exists()
        assert adr_path.name == "0001-use-postgresql.md"

        content = adr_path.read_text()
        assert "Use PostgreSQL" in content
        assert "## Status" in content
        assert "## Context" in content
        assert "## Decision" in content
        assert "## Consequences" in content

    def test_new_adr_with_madr_template(self, temp_dir: Path) -> None:
        """Test creating ADR with MADR template."""
        manager = ADRManager(temp_dir)

        adr_path = manager.new_adr("Use Redis", template="madr", open_editor=False)

        content = adr_path.read_text()
        assert "# Use Redis" in content
        assert "* Status: proposed" in content
        assert "## Context and Problem Statement" in content
        assert "## Considered Alternatives" in content

    def test_list_adrs(self, temp_dir: Path) -> None:
        """Test listing ADRs."""
        manager = ADRManager(temp_dir)

        # Initially empty
        assert manager.list_adrs() == []

        # Create some ADRs
        manager.new_adr("First Decision", open_editor=False)
        manager.new_adr("Second Decision", open_editor=False)

        adrs = manager.list_adrs()
        assert len(adrs) == 2
        assert adrs[0][1] == "First Decision"
        assert adrs[1][1] == "Second Decision"

    def test_get_adr_path(self, temp_dir: Path) -> None:
        """Test getting ADR path by number."""
        manager = ADRManager(temp_dir)

        adr_path = manager.new_adr("Test Decision", open_editor=False)

        found_path = manager.get_adr_path(1)
        assert found_path == adr_path

        not_found = manager.get_adr_path(999)
        assert not_found is None

    def test_supersede_adr(self, temp_dir: Path) -> None:
        """Test superseding an ADR."""
        manager = ADRManager(temp_dir)

        # Create original ADR
        manager.new_adr("Use MySQL", open_editor=False)

        # Supersede it
        old_path, new_path = manager.supersede_adr(1, "Use PostgreSQL")

        # Check that old ADR is marked as superseded
        old_content = old_path.read_text()
        assert "superseded by 0002" in old_content

        # Check that new ADR mentions supersession
        new_content = new_path.read_text()
        assert "supersedes" in new_content or "ADR-0001" in new_content

    def test_generate_toc(self, temp_dir: Path) -> None:
        """Test generating table of contents."""
        manager = ADRManager(temp_dir)

        manager.new_adr("First Decision", open_editor=False)
        manager.new_adr("Second Decision", open_editor=False)

        toc = manager.generate_toc()

        assert "# Architecture Decision Records" in toc
        assert "ADR-0001" in toc
        assert "ADR-0002" in toc
        assert "First Decision" in toc
        assert "Second Decision" in toc

    def test_invalid_template_raises_error(self, temp_dir: Path) -> None:
        """Test that invalid template raises error."""
        manager = ADRManager(temp_dir)

        with pytest.raises(ValueError, match="Template 'invalid' not found"):
            manager.new_adr("Test", template="invalid", open_editor=False)
