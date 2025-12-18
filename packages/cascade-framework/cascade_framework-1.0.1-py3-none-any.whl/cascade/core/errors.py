"""
Core error definitions for Cascade.

This module defines the foundational error hierarchy used by Cascade Core.
Errors defined here must remain completely standalone and must not depend
on higher-level features such as rules, profiles, dataclasses, or JIT layers.

Design goals:
- Explicit error types over generic exceptions
- Predictable structure for tooling and tests
- Zero upward dependencies
"""

from typing import Any, Optional


class CascadeError(Exception):
    """
    Base exception for all Cascade-related errors.

    This class exists mainly for catch-all purposes and should not be raised
    directly in normal validation flows.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class ValidationError(CascadeError):
    """
    Base class for all validation-related errors.

    This error represents a failure where a value does not satisfy
    an expected constraint or contract.
    """

    def __init__(
        self,
        message: str,
        *,
        value: Any = None,
        expected: Any = None,
    ):
        super().__init__(message)
        self.value = value
        self.expected = expected


class TypeValidationError(ValidationError):
    """
    Raised when a value does not match the expected type.

    This error is strictly about type compatibility, not about
    additional constraints or business rules.
    """

    def __init__(
        self,
        *,
        value: Any,
        expected_type: Any,
        message: Optional[str] = None,
    ):
        if message is None:
            message = (
                f"Expected value of type {expected_type!r}, "
                f"but received value {value!r} of type {type(value)!r}."
            )

        super().__init__(
            message,
            value=value,
            expected=expected_type,
        )


class RuleValidationError(ValidationError):
    """
    Raised when a value fails a validation rule.

    Rules are higher-level constraints applied after type checking.
    This error intentionally does not depend on any rule implementation.
    """

    def __init__(
        self,
        *,
        value: Any,
        rule_name: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Validation rule '{rule_name}' failed for value {value!r}."

        super().__init__(
            message,
            value=value,
            expected=rule_name,
        )

        self.rule_name = rule_name


class CoercionError(CascadeError):
    """
    Raised when an explicit coercion attempt fails.

    Coercion errors are not validation errors by default, as coercion
    is an explicit and opt-in operation in Cascade.
    """

    def __init__(
        self,
        *,
        value: Any,
        target_type: Any,
        message: Optional[str] = None,
    ):
        if message is None:
            message = (
                f"Failed to coerce value {value!r} "
                f"to target type {target_type!r}."
            )

        super().__init__(message)
        self.value = value
        self.target_type = target_type
