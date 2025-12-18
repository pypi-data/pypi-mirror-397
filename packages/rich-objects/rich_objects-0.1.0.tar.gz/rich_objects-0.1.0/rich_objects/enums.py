"""Simple enum definitions."""
from enum import Enum


class OutputFormat(str, Enum):
    """Output text format for received data."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"


class OutputStyle(str, Enum):
    """Text style options for none, bold-only, or bold-and-color."""

    NONE = "none"
    BOLD = "bold"
    ALL = "all"


