"""Generate receipt PDFs from JSON or spreadsheet data."""

from .generator import (
    ConfigError,
    generate_receipts,
    generate_receipts_from_config,
    load_config,
    receipt_total,
)

__all__ = [
    "ConfigError",
    "generate_receipts",
    "generate_receipts_from_config",
    "load_config",
    "receipt_total",
]
