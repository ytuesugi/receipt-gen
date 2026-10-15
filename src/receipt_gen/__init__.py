"""Generate receipt PDFs from local JSON configuration."""

from .generator import ConfigError, generate_receipts, load_config

__all__ = ["ConfigError", "generate_receipts", "load_config"]
