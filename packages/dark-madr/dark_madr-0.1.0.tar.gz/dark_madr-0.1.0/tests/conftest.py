"""Pytest configuration and fixtures."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from adr import ADRManager, TemplateADRSerializer, TemplateEngine
from adr.domain import ADRParser, FileSystemADRRepository
from adr.services import ADRService


@pytest.fixture  # type: ignore[misc]
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture  # type: ignore[misc]
def template_engine() -> TemplateEngine:
    """Create a template engine for testing."""
    template_dir = Path(__file__).parent.parent / "src" / "adr" / "templates"
    return TemplateEngine(template_dir)


@pytest.fixture  # type: ignore[misc]
def serializer(template_engine: TemplateEngine) -> TemplateADRSerializer:
    """Create a template-based serializer for testing."""
    return TemplateADRSerializer(template_engine)


@pytest.fixture  # type: ignore[misc]
def parser() -> ADRParser:
    """Create an ADR parser for testing."""
    return ADRParser()


@pytest.fixture  # type: ignore[misc]
def manager(temp_dir: Path) -> ADRManager:
    """Create an ADR manager for testing."""
    return ADRManager(temp_dir)


@pytest.fixture  # type: ignore[misc]
def repository(
    temp_dir: Path,
    serializer: TemplateADRSerializer,
    parser: ADRParser,
) -> FileSystemADRRepository:
    """Create a file system repository for testing."""
    return FileSystemADRRepository(temp_dir, serializer=serializer, parser=parser)


@pytest.fixture  # type: ignore[misc]
def service(repository: FileSystemADRRepository) -> ADRService:
    """Create an ADR service for testing."""
    return ADRService(repository)
