"""ADR - Architecture Decision Records management tool."""

__version__ = "0.1.0"
__author__ = "m1yag1"
__email__ = "730430+m1yag1@users.noreply.github.com"

from .adr_manager import ADRManager
from .config import ADRConfig, load_config
from .template_engine import ADRSerializer, TemplateADRSerializer, TemplateEngine

__all__ = [
    "ADRConfig",
    "ADRManager",
    "ADRSerializer",
    "TemplateADRSerializer",
    "TemplateEngine",
    "load_config",
]
