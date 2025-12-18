"""
Common built-in validation rules for Cascade.

These rules cover basic and widely applicable constraints.
"""

import re
from typing import Any

from cascade.rules.base import Rule


class Min(Rule):
    """Ensure a numeric value is greater than or equal to a minimum."""

    name = "min"

    def __init__(self, minimum: Any):
        self.minimum = minimum

    def check(self, value: Any) -> None:
        if value < self.minimum:
            self.fail(
                value,
                f"Value {value!r} is less than minimum {self.minimum!r}.",
            )


class Max(Rule):
    """Ensure a numeric value is less than or equal to a maximum."""

    name = "max"

    def __init__(self, maximum: Any):
        self.maximum = maximum

    def check(self, value: Any) -> None:
        if value > self.maximum:
            self.fail(
                value,
                f"Value {value!r} exceeds maximum {self.maximum!r}.",
            )


class Length(Rule):
    """Ensure a value satisfies length constraints."""

    name = "length"

    def __init__(self, *, min: int | None = None, max: int | None = None):
        self.min = min
        self.max = max

    def check(self, value: Any) -> None:
        size = len(value)

        if self.min is not None and size < self.min:
            self.fail(value, f"Length {size} is less than minimum {self.min}.")

        if self.max is not None and size > self.max:
            self.fail(value, f"Length {size} exceeds maximum {self.max}.")


class Pattern(Rule):
    """Ensure a string value matches a regular expression."""

    name = "pattern"

    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def check(self, value: Any) -> None:
        if not isinstance(value, str):
            self.fail(
                value,
                "Pattern rule can only be applied to string values.",
            )

        if not self.pattern.search(value):
            self.fail(
                value,
                f"Value {value!r} does not match required pattern.",
            )
