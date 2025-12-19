"""Tests for configuration management."""

from pathlib import Path

from adr.config import ADRConfig, find_project_root, get_effective_adr_dir, load_config


class TestADRConfig:
    """Test ADRConfig data class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ADRConfig()

        assert config.adr_dir == "doc/adr"
        assert config.template == "nygard"
        assert config.template_dir is None
        assert config.default_status == "proposed"
        assert config.default_authors == []

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = ADRConfig(
            adr_dir="docs/decisions",
            template="madr",
            default_status="draft",
            default_authors=["Alice", "Bob"],
        )

        assert config.adr_dir == "docs/decisions"
        assert config.template == "madr"
        assert config.default_status == "draft"
        assert config.default_authors == ["Alice", "Bob"]


class TestConfigLoading:
    """Test configuration loading from pyproject.toml."""

    def test_load_config_no_file(self, temp_dir: Path) -> None:
        """Test loading config when no pyproject.toml exists."""
        config = load_config(temp_dir)

        # Should return defaults
        assert config.adr_dir == "doc/adr"
        assert config.template == "nygard"

    def test_load_config_no_adr_section(self, temp_dir: Path) -> None:
        """Test loading config when pyproject.toml has no [tool.adr] section."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("""
[project]
name = "test-project"
version = "1.0.0"
""")

        config = load_config(temp_dir)

        # Should return defaults
        assert config.adr_dir == "doc/adr"
        assert config.template == "nygard"

    def test_load_config_with_adr_section(self, temp_dir: Path) -> None:
        """Test loading config with [tool.adr] section."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("""
[project]
name = "test-project"
version = "1.0.0"

[tool.adr]
dir = "docs/decisions"
template = "madr"
default_status = "draft"
default_authors = ["Team Architecture", "John Doe"]
template_dir = "custom_templates"
""")

        config = load_config(temp_dir)

        assert config.adr_dir == "docs/decisions"
        assert config.template == "madr"
        assert config.default_status == "draft"
        assert config.default_authors == ["Team Architecture", "John Doe"]
        assert config.template_dir == "custom_templates"

    def test_load_config_partial_section(self, temp_dir: Path) -> None:
        """Test loading config with partial [tool.adr] section."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("""
[tool.adr]
template = "madr"
default_authors = ["Alice"]
""")

        config = load_config(temp_dir)

        # Should use config values where available, defaults elsewhere
        assert config.adr_dir == "doc/adr"  # default
        assert config.template == "madr"  # from config
        assert config.default_status == "proposed"  # default
        assert config.default_authors == ["Alice"]  # from config

    def test_load_config_invalid_toml(self, temp_dir: Path) -> None:
        """Test loading config with invalid TOML."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml content [")

        config = load_config(temp_dir)

        # Should fall back to defaults on error
        assert config.adr_dir == "doc/adr"
        assert config.template == "nygard"


class TestProjectRootFinding:
    """Test finding project root directory."""

    def test_find_project_root_current_dir(self, temp_dir: Path) -> None:
        """Test finding project root in current directory."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        root = find_project_root(temp_dir)

        # Use resolve() to handle macOS /var -> /private/var symlinks
        assert root is not None
        assert root.resolve() == temp_dir.resolve()

    def test_find_project_root_parent_dir(self, temp_dir: Path) -> None:
        """Test finding project root in parent directory."""
        # Create nested structure
        subdir = temp_dir / "src" / "myproject"
        subdir.mkdir(parents=True)

        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        root = find_project_root(subdir)

        # Use resolve() to handle macOS /var -> /private/var symlinks
        assert root is not None
        assert root.resolve() == temp_dir.resolve()

    def test_find_project_root_not_found(self, temp_dir: Path) -> None:
        """Test when no project root is found."""
        subdir = temp_dir / "some" / "deep" / "path"
        subdir.mkdir(parents=True)

        root = find_project_root(subdir)

        assert root is None


class TestEffectivePaths:
    """Test effective path calculation."""

    def test_get_effective_adr_dir_absolute_path(self, temp_dir: Path) -> None:
        """Test effective ADR directory with absolute path."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text(f"""
[tool.adr]
dir = "{temp_dir / "custom" / "adrs"}"
""")

        effective_dir = get_effective_adr_dir(temp_dir)

        assert effective_dir == temp_dir / "custom" / "adrs"

    def test_get_effective_adr_dir_relative_path(self, temp_dir: Path) -> None:
        """Test effective ADR directory with relative path."""
        pyproject_path = temp_dir / "pyproject.toml"
        pyproject_path.write_text("""
[tool.adr]
dir = "docs/decisions"
""")

        effective_dir = get_effective_adr_dir(temp_dir)

        assert effective_dir == temp_dir / "docs" / "decisions"

    def test_get_effective_adr_dir_no_config(self, temp_dir: Path) -> None:
        """Test effective ADR directory with no configuration."""
        effective_dir = get_effective_adr_dir(temp_dir)

        # When project_dir is provided, returns default path relative to it
        assert effective_dir == temp_dir / "doc" / "adr"
