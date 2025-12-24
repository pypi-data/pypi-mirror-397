"""Implementation for displaying data in a user-friendly fashion."""
from typing import Any
from typing import Optional

import yaml
from rich.console import Console
from rich.markup import escape

from rich_objects.console import console_factory
from rich_objects.constants import ELLIPSIS
from rich_objects.constants import PROPERTIES
from rich_objects.constants import WILDCARD_COLUMN
from rich_objects.enums import OutputFormat
from rich_objects.enums import OutputStyle
from rich_objects.rich_table import RichTable
from rich_objects.table_config import TableConfig

# NOTE: the key field of dictionaries are expected to be be `str`, `int`, `float`, but use
#       `Any` readability.


def headerize(s: str) -> str:
    """Create a table header from the provided string."""
    if s == WILDCARD_COLUMN:
        return PROPERTIES
    return s[0].upper() + s[1:]


def _truncate(s: str, max_length: int) -> str:
    """Truncate the provided string to a maximum of max_length (including elipsis)."""
    if len(s) < max_length:
        return s
    return s[: max_length - 3] + ELLIPSIS


def _get_name_key(item: dict[Any, Any], key_fields: list[str]) -> Optional[str]:
    """Attempt to find an identifying value."""
    for k in key_fields:
        key = str(k)
        if key in item:
            return key

    return None


def _get_other_key(item: dict[Any, Any], name_key: str) -> Optional[str]:
    """Find the "other" key (if there's just one value)."""
    keys = set(item.keys())
    keys.remove(name_key)
    if len(keys) != 1:
        return None

    return keys.pop()


def _is_url(s: str, url_prefixes: list[str]) -> bool:
    """Rudimentary check for somethingt starting with URL prefix."""
    return any(s.startswith(p) for p in url_prefixes)


def _safe(v: Any) -> str:
    """Convert 'v' to a string that is properly escaped."""
    return escape(str(v))


def _create_list_table(
    items: list[dict[Any, Any]], outer: bool, config: TableConfig
) -> RichTable:
    """Create a table from a list of dictionary items.

    If an identifying "name key" is found (in the first entry), the table will have 2 columns: name, Properties
    If no identifying "name key" is found, the table will be a single column table with the properties.

    NOTE: nesting is done as needed
    """
    caption = config.items_caption.format(len(items)) if outer else None
    name_key = _get_name_key(items[0], config.key_fields)
    if not name_key:
        # without identifiers just create table with one "Values" column
        table = RichTable(
            config.values_label,
            outer=outer,
            show_lines=True,
            caption=caption,
            row_props=config.row_properties,
        )
        for item in items:
            table.add_row(_table_cell_value(item, config))
        return table

    # if there's just one property besides the key, use that as the label
    name_label = headerize(name_key)
    other_key = _get_other_key(items[0], name_key)
    if other_key:
        other_name = headerize(other_key)
        fields = [name_label, other_name]
        table = RichTable(
            *fields,
            outer=outer,
            show_lines=True,
            caption=caption,
            row_props=config.row_properties,
        )
        for item in items:
            # id may be an int, so convert to string before truncating
            name = _safe(item.pop(name_key, config.unknown_label))
            body = _table_cell_value(item.get(other_key), config)
            table.add_row(_truncate(name, config.key_max_len), body)
        return table

    # create a table with identifier in left column, and rest of data in right column
    fields = [name_label, config.properties_label]
    table = RichTable(
        *fields,
        outer=outer,
        show_lines=True,
        caption=caption,
        row_props=config.row_properties,
    )
    for item in items:
        # id may be an int, so convert to string before truncating
        name = _safe(item.pop(name_key, config.unknown_label))
        body = _table_cell_value(item, config)
        table.add_row(_truncate(name, config.key_max_len), body)

    return table


def _create_object_table(
    obj: dict[Any, Any], outer: bool, config: TableConfig
) -> RichTable:
    """Create a table of a dictionary object.

    NOTE: nesting is done in the right column as needed.
    """
    headers = [config.property_label, config.value_label]
    table = RichTable(
        *headers, outer=outer, show_lines=False, row_props=config.row_properties
    )
    for k, v in obj.items():
        name = _safe(k)
        table.add_row(_truncate(name, config.key_max_len), _table_cell_value(v, config))

    return table


def _table_cell_value(obj: Any, config: TableConfig) -> Any:
    """Create the "inner" value for a table cell.

    Depending on the input value type, the cell may look different. If a dict, or list[dict],
    an inner table is created. Otherwise, the object is converted to a printable value.
    """
    value: Any = None
    if isinstance(obj, dict):
        value = _create_object_table(obj, outer=False, config=config)
    elif isinstance(obj, list) and obj:
        if isinstance(obj[0], dict):
            value = _create_list_table(obj, outer=False, config=config)
        else:
            values = [str(x) for x in obj]
            s = _safe(", ".join(values))
            value = _truncate(s, config.value_max_len)
    else:
        s = _safe(obj)
        max_len = (
            config.url_max_len
            if _is_url(s, config.url_prefixes)
            else config.value_max_len
        )
        value = _truncate(s, max_len)

    return value


def _create_list_columns_table(items: list[dict[str, Any]], columns: list[str], config: TableConfig) -> RichTable:
    """Create a table with the provided columns."""
    headers = [headerize(c) for c in columns]
    table = RichTable(
        *headers, outer=True, show_lines=True, row_props=config.row_properties
    )
    for item in items:
        values = []
        for c in columns:
            if c == WILDCARD_COLUMN:
                sub_value = {k: v for k, v in item.items() if k not in columns}
                values.append(_table_cell_value(sub_value, config))
                continue
            values.append(_table_cell_value(item.get(c), config))
        table.add_row(*values)

    return table


def rich_table_factory(
    obj: Any,
    config: Optional[TableConfig] = None,
    columns: Optional[list[str]] = None,
) -> RichTable:
    """Create a RichTable (alias for rich.table.Table) from the object."""
    config = config or TableConfig()
    if isinstance(obj, dict):
        return _create_object_table(obj, outer=True, config=config)

    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        if columns:
            return _create_list_columns_table(obj, columns=columns, config=config)

        return _create_list_table(obj, outer=True, config=config)

    # this is a list of "simple" properties
    if (
        isinstance(obj, list)
        and obj
        and all(
            item is None or isinstance(item, (str, float, bool, int)) for item in obj
        )
    ):
        caption = config.items_caption.format(len(obj))
        table = RichTable(
            config.items_label,
            outer=True,
            show_lines=True,
            caption=caption,
            row_props=config.row_properties,
        )
        for item in obj:
            table.add_row(_table_cell_value(item, config))
        return table

    raise ValueError(f"Unable to create table for type {type(obj).__name__}")


def display(
    obj: Any,
    fmt: OutputFormat,
    style: OutputStyle,
    indent: int = 2,
    columns: Optional[list[str]] = None,
    console: Optional[Console] = None,
    config: Optional[TableConfig] = None,
) -> None:
    """Display the data provided in obj, according to the formating arguments."""
    no_color = style != OutputStyle.ALL
    highlight = style != OutputStyle.NONE
    console = console or console_factory(no_color=no_color, highlight=highlight)

    if isinstance(obj, str):
        console.print(_safe(obj))
        return

    if fmt == OutputFormat.JSON:
        console.print_json(data=obj, indent=indent, highlight=highlight)
        return

    if fmt == OutputFormat.YAML:
        console.print(_safe(yaml.dump(obj, indent=indent)))
        return

    if not obj:
        console.print("Nothing found")
        return

    table = rich_table_factory(obj, columns=columns, config=config)
    console.print(table)
    return
