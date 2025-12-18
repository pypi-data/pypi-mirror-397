"""Custom lookups for HashidField.

Provides lookup implementations that handle hashid string to integer
conversion for database queries.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.core.exceptions import EmptyResultSet
from django.db.models import lookups

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class HashidLookup(lookups.Lookup):
    """Base lookup that converts hashid values to integers for queries.

    This lookup handles hashid-to-integer conversion directly, bypassing
    the field's get_prep_value() to enable automatic search_fields support.
    """

    def get_prep_lookup(self) -> Any:
        """Convert the lookup value to an integer for the database.

        Bypasses the field's get_prep_value() and handles conversion directly
        to properly support Django Admin's search_fields with icontains.
        """
        # Don't call super() - handle the conversion ourselves
        return self._convert_value(self.rhs)

    def _convert_value(self, value: Any) -> Any:
        """Convert a single value to its integer representation."""
        logger.debug(
            "Lookup received value: %s (type: %s)", value, type(value).__name__
        )
        if value is None:
            return None

        from hashid_field.hashid import Hashid

        if isinstance(value, Hashid):
            return value.id

        if isinstance(value, int):
            # Check if int lookups are allowed
            from hashid_field.conf import app_settings

            field = self.lhs.output_field
            allow_int = getattr(
                field, "allow_int_lookup", app_settings.allow_int_lookup
            )
            if allow_int:
                return value
            else:
                # Try to treat as a hashid that was decoded
                return value

        if isinstance(value, str):
            # Decode the hashid string
            field = self.lhs.output_field
            if hasattr(field, "decode_id"):
                try:
                    return field.decode_id(value)
                except (ValueError, TypeError):
                    from hashid_field.conf import app_settings

                    if app_settings.lookup_exception:
                        raise
                    # Return an impossible value that will never match any record
                    # Using -1 since database IDs are always positive
                    # This allows OR queries (like Django Admin search) to continue
                    logger.debug("Invalid hashid lookup value '%s' - using impossible value", value)
                    return -1
            return value

        return value


class HashidExact(HashidLookup, lookups.Exact):
    """Exact lookup for HashidField."""

    pass


class HashidIExact(HashidLookup, lookups.Exact):
    """Case-insensitive exact lookup for HashidField.

    Treated as exact lookup since hashids are case-sensitive.
    Enables search_fields to work automatically in Django Admin.
    """

    lookup_name = "iexact"


class HashidContains(HashidLookup, lookups.Exact):
    """Contains lookup for HashidField.

    Treated as exact lookup since hashids must match exactly.
    Enables search_fields to work automatically in Django Admin.
    """

    lookup_name = "contains"


class HashidIContains(HashidLookup, lookups.Exact):
    """Case-insensitive contains lookup for HashidField.

    Treated as exact lookup since hashids must match exactly.
    Enables search_fields to work automatically in Django Admin.
    """

    lookup_name = "icontains"


class HashidIn(HashidLookup, lookups.In):
    """In lookup for HashidField."""

    def get_prep_lookup(self) -> list[Any]:
        """Convert all values in the list to integers."""
        values = self.rhs
        if not hasattr(values, "__iter__") or isinstance(values, str):
            values = [values]
        converted = [self._convert_value(v) for v in values]
        return [v for v in converted if v is not None]


class HashidIsNull(lookups.IsNull):
    """IsNull lookup for HashidField - no conversion needed."""

    pass


class HashidLt(HashidLookup, lookups.LessThan):
    """Less than lookup for HashidField."""

    pass


class HashidLte(HashidLookup, lookups.LessThanOrEqual):
    """Less than or equal lookup for HashidField."""

    pass


class HashidGt(HashidLookup, lookups.GreaterThan):
    """Greater than lookup for HashidField."""

    pass


class HashidGte(HashidLookup, lookups.GreaterThanOrEqual):
    """Greater than or equal lookup for HashidField."""

    pass


def register_lookups(field_class: type) -> None:
    """Register all hashid lookups for a field class.

    Args:
        field_class: The field class to register lookups for
    """
    field_class.register_lookup(HashidExact)
    field_class.register_lookup(HashidIExact)
    field_class.register_lookup(HashidContains)
    field_class.register_lookup(HashidIContains)
    field_class.register_lookup(HashidIn)
    field_class.register_lookup(HashidIsNull)
    field_class.register_lookup(HashidLt)
    field_class.register_lookup(HashidLte)
    field_class.register_lookup(HashidGt)
    field_class.register_lookup(HashidGte)
