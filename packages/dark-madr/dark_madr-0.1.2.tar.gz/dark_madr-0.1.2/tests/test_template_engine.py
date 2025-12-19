"""Tests for template engine."""

from adr import ADRManager
from adr.template_engine import get_default_context


class TestTemplateEngine:
    """Test TemplateEngine."""

    def test_get_default_context(self) -> None:
        """Test getting default context."""
        context = get_default_context(5, "Test Decision", "accepted")

        assert context["number"] == "0005"
        assert context["title"] == "Test Decision"
        assert context["status"] == "accepted"
        assert "date" in context
        assert context["authors"] == []

    def test_list_templates(self, manager: ADRManager) -> None:
        """Test listing available templates."""
        templates = manager.template_engine.list_templates()

        assert "nygard" in templates
        assert "madr" in templates

    def test_template_exists(self, manager: ADRManager) -> None:
        """Test checking if template exists."""
        assert manager.template_engine.template_exists("nygard")
        assert manager.template_engine.template_exists("madr")
        assert not manager.template_engine.template_exists("nonexistent")

    def test_render_nygard_template(self, manager: ADRManager) -> None:
        """Test rendering Nygard template."""
        context = get_default_context(1, "Test Decision")

        content = manager.template_engine.render_template("nygard.md", context)

        assert "# 0001. Test Decision" in content
        assert "## Status" in content
        assert "## Context" in content
        assert "## Decision" in content
        assert "## Consequences" in content

    def test_render_madr_template(self, manager: ADRManager) -> None:
        """Test rendering MADR template."""
        context = get_default_context(2, "Another Decision")

        content = manager.template_engine.render_template("madr.md", context)

        assert "# Another Decision" in content
        assert "* Status: proposed" in content
        assert "## Context and Problem Statement" in content
        assert "## Considered Alternatives" in content
