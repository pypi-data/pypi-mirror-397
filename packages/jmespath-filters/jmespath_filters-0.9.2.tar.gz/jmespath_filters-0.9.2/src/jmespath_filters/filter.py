"""Main package."""

from __future__ import annotations

import typing

from jmespath_filters.common import Expression

from .schema import schema


if typing.TYPE_CHECKING:
    from .types import Payload, Rules


class Filter:
    """Jmespath composite expressions filter."""

    def __init__(self, rules: Rules) -> None:
        self._expression = Expression(rules)

    @classmethod
    def from_json(cls, rules: Rules) -> Filter:
        """Create a Filter from a json."""
        try:
            from jsonschema import validate  # noqa: PLC0415

            validate(rules, schema=schema)
            return Filter(rules)
        except ImportError:
            raise RuntimeError("Missing jsonschema dependency") from None

    def match(self, data: Payload) -> bool:
        """Match the filter expression against data."""
        return self._expression.match(data)
