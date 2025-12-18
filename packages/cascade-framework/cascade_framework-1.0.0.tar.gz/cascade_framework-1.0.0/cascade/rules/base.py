"""
Base rule definition for Cascade.

A rule is defined as:
- A callable accepting a single value
- Raising RuleValidationError on failure
- Exposing a public 'name' attribute

This class is a reference implementation, not a hard requirement.
"""

from typing import Any

from cascade.core.errors import RuleValidationError


class Rule:
    """
    Reference base class for validation rules.

    Subclasses must implement the check() method.
    """

    name: str = "rule"

    def __call__(self, value: Any) -> None:
        self.check(value)

    def check(self, value: Any) -> None:
        """
        Validate a value.

        Must raise RuleValidationError on failure.
        """
        raise NotImplementedError(
            "Rule.check() must be implemented by subclasses."
        )

    def fail(self, value: Any, message: str) -> None:
        """
        Raise a standardized rule validation error.
        """
        raise RuleValidationError(
            value=value,
            rule_name=self.name,
            message=message,
        )
