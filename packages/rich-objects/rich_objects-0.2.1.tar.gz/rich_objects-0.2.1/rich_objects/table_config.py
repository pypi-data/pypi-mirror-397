"""Contains TableConfig class which controlls the table outputs."""
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from rich_objects.constants import DEFAULT_ROW_PROPS
from rich_objects.constants import FOUND_ITEMS
from rich_objects.constants import ITEMS
from rich_objects.constants import KEY_FIELDS
from rich_objects.constants import KEY_MAX_LEN
from rich_objects.constants import PROPERTIES
from rich_objects.constants import PROPERTY
from rich_objects.constants import UNKNOWN
from rich_objects.constants import URL_MAX_LEN
from rich_objects.constants import URL_PREFIXES
from rich_objects.constants import VALUE
from rich_objects.constants import VALUE_MAX_LEN
from rich_objects.constants import VALUES


@dataclass
class TableConfig:
    """Configuration for customizing the table outputs.

    The defaults provide a standard look and feel, but can be overridden to all customization.
    """

    items_label: str = ITEMS
    property_label: str = PROPERTY
    properties_label: str = PROPERTIES
    value_label: str = VALUE
    values_label: str = VALUES
    unknown_label: str = UNKNOWN
    items_caption: str = FOUND_ITEMS
    url_prefixes: list[str] = field(default_factory=lambda: URL_PREFIXES)
    url_max_len: int = URL_MAX_LEN
    key_fields: list[str] = field(default_factory=lambda: KEY_FIELDS)
    key_max_len: int = KEY_MAX_LEN
    value_max_len: int = VALUE_MAX_LEN
    row_properties: dict[str, Any] = field(default_factory=lambda: DEFAULT_ROW_PROPS)
