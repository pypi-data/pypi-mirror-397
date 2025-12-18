"""Contains the RichTable class."""
from typing import Any

from rich.box import HEAVY_HEAD
from rich.table import Table

from rich_objects.constants import DEFAULT_ROW_PROPS


class RichTable(Table):
    """Wrapper for the rich.Table to provide some methods for adding complex items."""

    def __init__(
        self,
        *args: Any,
        outer: bool = True,
        row_props: dict[str, Any] = DEFAULT_ROW_PROPS,
        **kwargs: Any,
    ):
        """Initialize the Table with a few defaults."""
        super().__init__(
            # items with "regular" defaults
            highlight=kwargs.pop("highlight", True),
            row_styles=kwargs.pop("row_styles", None),
            expand=kwargs.pop("expand", False),
            caption_justify=kwargs.pop("caption_justify", "left"),
            border_style=kwargs.pop("border_style", None),
            leading=kwargs.pop(
                "leading", 0
            ),  # warning: setting to non-zero disables lines
            # these items take queues from `outer`
            show_header=kwargs.pop("show_header", outer),
            show_edge=kwargs.pop("show_edge", outer),
            box=HEAVY_HEAD if outer else None,
            **kwargs,
        )
        for name in args:
            self.add_column(name, **row_props)


