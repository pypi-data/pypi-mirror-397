"""
Core type checking logic for Cascade.

This module provides deterministic runtime type validation based on
Python's type system and typing constructs.

Design constraints:
- Always strict
- No coercion
- No rule execution
- No context awareness
"""

from typing import Any, get_args, get_origin, Union

from cascade.core.errors import TypeValidationError
from cascade.core.registry import get_registered_validator


def validate_type(value: Any, expected_type: Any) -> bool:
    """
    Validate a value against an expected type.

    This function is strictly deterministic:
    - No coercion is performed
    - No implicit behavior exists
    - Validation either passes or raises TypeValidationError

    Parameters
    ----------
    value:
        The value to be validated.
    expected_type:
        The expected Python type or typing construct.

    Returns
    -------
    bool
        True if validation succeeds.

    Raises
    ------
    TypeValidationError
        If the value does not satisfy the expected type.
    """
    _check_type(value, expected_type)
    return True


def _check_type(value: Any, expected_type: Any) -> None:
    """
    Internal dispatcher for type checking.
    """
    if expected_type is Any:
        return

    validator = get_registered_validator(expected_type)
    if validator is not None:
        _check_custom_type(value, expected_type, validator)
        return

    origin = get_origin(expected_type)

    if origin is None:
        _check_builtin_type(value, expected_type)
        return

    if origin is Union:
        _check_union_type(value, expected_type)
        return

    _check_generic_type(value, expected_type, origin)


def _check_builtin_type(value: Any, expected_type: Any) -> None:
    if not isinstance(value, expected_type):
        raise TypeValidationError(
            value=value,
            expected_type=expected_type,
        )


def _check_union_type(value: Any, expected_type: Any) -> None:
    for option in get_args(expected_type):
        try:
            _check_type(value, option)
            return
        except TypeValidationError:
            continue

    raise TypeValidationError(
        value=value,
        expected_type=expected_type,
    )


def _check_generic_type(value: Any, expected_type: Any, origin: Any) -> None:
    if not isinstance(value, origin):
        raise TypeValidationError(
            value=value,
            expected_type=expected_type,
        )

    args = get_args(expected_type)
    if not args:
        return

    if origin in (list, tuple, set, frozenset):
        _check_iterable_items(value, args[0])
        return

    if origin is dict:
        _check_mapping_items(value, args)
        return

    # Unsupported generics fall back to container-only validation.


def _check_iterable_items(iterable: Any, item_type: Any) -> None:
    for item in iterable:
        _check_type(item, item_type)


def _check_mapping_items(mapping: Any, args: tuple) -> None:
    if len(args) != 2:
        return

    key_type, value_type = args
    for key, value in mapping.items():
        _check_type(key, key_type)
        _check_type(value, value_type)


def _check_custom_type(value: Any, expected_type: Any, validator) -> None:
    try:
        validator(value)
    except TypeValidationError:
        raise
    except Exception as exc:
        raise TypeValidationError(
            value=value,
            expected_type=expected_type,
            message=str(exc),
        ) from exc
