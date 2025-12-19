"""Tests for ADR repository."""

from pathlib import Path
from typing import TYPE_CHECKING

from adr.domain import ADR, ADRMetadata, ADRStatus

if TYPE_CHECKING:
    from adr.domain import FileSystemADRRepository


class TestFileSystemADRRepository:
    """Test FileSystemADRRepository."""

    def test_save_new_adr(self, repository: "FileSystemADRRepository") -> None:
        metadata = ADRMetadata(number=1, title="Test Decision")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )

        repository.save(adr)

        assert repository.exists(1)

    def test_save_update_existing(self, repository: "FileSystemADRRepository") -> None:
        metadata = ADRMetadata(number=1, title="Test Decision")
        adr = ADR(
            metadata=metadata,
            context="context",
            decision="decision",
            consequences="consequences",
        )

        repository.save(adr)

        # Update the same ADR (same filename)
        adr.context = "updated context"
        repository.save(adr)

        retrieved = repository.find_by_number(1)
        assert retrieved is not None
        assert retrieved.context == "updated context"

    def test_find_by_number_not_found(
        self, repository: "FileSystemADRRepository"
    ) -> None:
        result = repository.find_by_number(999)

        assert result is None

    def test_find_all_empty(self, repository: "FileSystemADRRepository") -> None:
        result = repository.find_all()

        assert result == []

    def test_find_all_skips_invalid_filenames(
        self, repository: "FileSystemADRRepository", temp_dir: Path
    ) -> None:
        # Create valid ADR
        metadata = ADRMetadata(number=1, title="Valid")
        adr = ADR(
            metadata=metadata,
            context="c",
            decision="d",
            consequences="cons",
        )
        repository.save(adr)

        # Create invalid file that matches glob but has invalid number
        invalid_file = temp_dir / "abcd-invalid.md"
        invalid_file.write_text("# Invalid")

        result = repository.find_all()

        assert len(result) == 1
        assert result[0].metadata.title == "Valid"

    def test_find_by_status(self, repository: "FileSystemADRRepository") -> None:
        # Create ADRs with different statuses
        for i, status in enumerate(
            [ADRStatus.PROPOSED, ADRStatus.ACCEPTED, ADRStatus.PROPOSED], 1
        ):
            metadata = ADRMetadata(number=i, title=f"ADR {i}", status=status)
            adr = ADR(
                metadata=metadata,
                context="c",
                decision="d",
                consequences="cons",
            )
            repository.save(adr)

        proposed = repository.find_by_status("proposed")
        accepted = repository.find_by_status("accepted")

        assert len(proposed) == 2
        assert len(accepted) == 1

    def test_delete_existing(self, repository: "FileSystemADRRepository") -> None:
        metadata = ADRMetadata(number=1, title="To Delete")
        adr = ADR(
            metadata=metadata,
            context="c",
            decision="d",
            consequences="cons",
        )
        repository.save(adr)

        result = repository.delete(1)

        assert result is True
        assert not repository.exists(1)

    def test_delete_nonexistent(self, repository: "FileSystemADRRepository") -> None:
        result = repository.delete(999)

        assert result is False

    def test_get_next_number_empty(self, repository: "FileSystemADRRepository") -> None:
        assert repository.get_next_number() == 1

    def test_get_next_number_with_existing(
        self, repository: "FileSystemADRRepository"
    ) -> None:
        metadata = ADRMetadata(number=5, title="Test")
        adr = ADR(
            metadata=metadata,
            context="c",
            decision="d",
            consequences="cons",
        )
        repository.save(adr)

        assert repository.get_next_number() == 6

    def test_exists(self, repository: "FileSystemADRRepository") -> None:
        metadata = ADRMetadata(number=1, title="Test")
        adr = ADR(
            metadata=metadata,
            context="c",
            decision="d",
            consequences="cons",
        )
        repository.save(adr)

        assert repository.exists(1) is True
        assert repository.exists(999) is False
