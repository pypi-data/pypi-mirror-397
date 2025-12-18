"""Jmespath_filters types."""

import typing

Rules = "str | dict[str, Expression] | Expression | list[Expression]"
Payload = dict[str, typing.Any] | str | None
