"""Internationalized constants for controlling appearance."""
from gettext import gettext

# allow for i18n/l8n
ITEMS = gettext("Items")
PROPERTY = gettext("Property")
PROPERTIES = gettext("Properties")
VALUE = gettext("Value")
VALUES = gettext("Values")
UNKNOWN = gettext("Unknown")
FOUND_ITEMS = gettext("Found {} items")
ELLIPSIS = gettext("...")

OBJECT_HEADERS = [PROPERTY, VALUE]

KEY_FIELDS = ["name", "id"]
URL_PREFIXES = ["http://", "https://", "ftp://"]

KEY_MAX_LEN = 35
VALUE_MAX_LEN = 50
URL_MAX_LEN = 100

# this is value used to denote all other properties (not specified in list)
WILDCARD_COLUMN = '*'

DEFAULT_ROW_PROPS = {
    "justify": "left",
    "no_wrap": True,
    "overflow": "ignore",
}
