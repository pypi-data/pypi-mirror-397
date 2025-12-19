"""Tests for CLI commands."""

import os
from pathlib import Path

from click.testing import CliRunner

from adr.cli import cli


class TestCLIInit:
    """Test the init command."""

    def test_init_creates_first_adr(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "init"])

            assert result.exit_code == 0
            assert "Initialized ADR directory" in result.output
            assert "Created first ADR" in result.output

            # Check file was created
            adr_files = list(temp_dir.glob("*.md"))
            assert len(adr_files) == 1
            assert "0001" in adr_files[0].name

    def test_init_fails_if_already_initialized(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # First init
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "init"])

            # Second init should fail
            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "init"])

            assert result.exit_code == 1
            assert "Error" in result.output


class TestCLINew:
    """Test the new command."""

    def test_new_creates_adr(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["--adr-dir", str(temp_dir), "new", "Use PostgreSQL"]
            )

            assert result.exit_code == 0
            assert "Created" in result.output
            assert "use-postgresql" in result.output

    def test_new_with_template(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                ["--adr-dir", str(temp_dir), "new", "Use Redis", "--template", "madr"],
            )

            assert result.exit_code == 0
            assert "Created" in result.output

            # Check MADR format
            adr_file = list(temp_dir.glob("*.md"))[0]
            content = adr_file.read_text()
            assert "* Status:" in content
            assert "## Context and Problem Statement" in content

    def test_new_with_status(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "--adr-dir",
                    str(temp_dir),
                    "new",
                    "Important Decision",
                    "--status",
                    "accepted",
                ],
            )

            assert result.exit_code == 0

            adr_file = list(temp_dir.glob("*.md"))[0]
            content = adr_file.read_text()
            assert "accepted" in content.lower()

    def test_new_with_invalid_template(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "--adr-dir",
                    str(temp_dir),
                    "new",
                    "Test",
                    "--template",
                    "nonexistent",
                ],
            )

            assert result.exit_code == 1
            assert "Error" in result.output

    def test_new_supersedes(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create first ADR
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "new", "Use MySQL"])

            # Create superseding ADR
            result = runner.invoke(
                cli,
                [
                    "--adr-dir",
                    str(temp_dir),
                    "new",
                    "Use PostgreSQL",
                    "--supersedes",
                    "1",
                ],
            )

            assert result.exit_code == 0
            assert "superseding" in result.output

    def test_new_supersedes_nonexistent(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "--adr-dir",
                    str(temp_dir),
                    "new",
                    "Test",
                    "--supersedes",
                    "999",
                ],
            )

            assert result.exit_code == 1
            assert "Error" in result.output


class TestCLIList:
    """Test the list command."""

    def test_list_empty(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "list"])

            assert result.exit_code == 0
            assert "No ADRs found" in result.output

    def test_list_with_adrs(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "new", "First Decision"])
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "new", "Second Decision"])

            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "list"])

            assert result.exit_code == 0
            assert "ADR-0001" in result.output
            assert "ADR-0002" in result.output
            assert "First Decision" in result.output
            assert "Second Decision" in result.output


class TestCLIShow:
    """Test the show command."""

    def test_show_existing_adr(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "new", "Test Decision"])

            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "show", "1"])

            assert result.exit_code == 0
            assert "Test Decision" in result.output

    def test_show_nonexistent_adr(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "show", "999"])

            assert result.exit_code == 1
            assert "not found" in result.output


class TestCLIGenerate:
    """Test the generate command."""

    def test_generate_toc(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "new", "First"])
            runner.invoke(cli, ["--adr-dir", str(temp_dir), "new", "Second"])

            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "generate", "toc"])

            assert result.exit_code == 0
            assert "Architecture Decision Records" in result.output
            assert "ADR-0001" in result.output
            assert "ADR-0002" in result.output


class TestCLITemplates:
    """Test the templates command."""

    def test_templates_list(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "templates"])

            assert result.exit_code == 0
            assert "Available Templates" in result.output
            assert "nygard" in result.output
            assert "madr" in result.output


class TestCLIHelpTemplate:
    """Test the help-template command."""

    def test_help_template_existing(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["--adr-dir", str(temp_dir), "help-template", "nygard"]
            )

            assert result.exit_code == 0
            assert "## Status" in result.output
            assert "## Context" in result.output

    def test_help_template_nonexistent(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["--adr-dir", str(temp_dir), "help-template", "nonexistent"]
            )

            assert result.exit_code == 1
            assert "not found" in result.output


class TestCLIConfig:
    """Test the config command."""

    def test_config_shows_settings(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["--adr-dir", str(temp_dir), "config"])

            assert result.exit_code == 0
            assert "ADR Configuration" in result.output
            assert "ADR Directory" in result.output
            assert "Default Template" in result.output


class TestCLIInitConfig:
    """Test the init-config command."""

    def test_init_config_no_pyproject(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Change to temp dir where there's no pyproject.toml
            os.chdir(temp_dir)
            result = runner.invoke(cli, ["init-config"])

            assert result.exit_code == 1
            assert "No pyproject.toml found" in result.output

    def test_init_config_with_pyproject(self, temp_dir: Path) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create pyproject.toml
            pyproject = temp_dir / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"')

            os.chdir(temp_dir)
            result = runner.invoke(cli, ["init-config"])

            assert result.exit_code == 0
            assert "Added ADR configuration" in result.output

            # Check config was added
            content = pyproject.read_text()
            assert "[tool.adr]" in content
