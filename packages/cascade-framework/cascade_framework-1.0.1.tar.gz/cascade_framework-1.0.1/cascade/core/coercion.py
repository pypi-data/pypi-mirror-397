"""
Explicit coercion utilities for Cascade Core.

This module provides a minimal and explicit coercion mechanism.
Coercion is always opt-in and never triggered automatically by type checking.

Design goals:
- Explicit API, no implicit behavior
- Deterministic outcome
- No dependency on rules, profiles, or validation logic
"""

from typing import Any, Callable, Dict, Optional, Type

from cascade.core.errors import CoercionError


Coercer = Callable[[Any], Any]


class CoercionRegistry:
    """
    Passive registry for coercion functions.

    This registry maps a target type to a coercion callable.
    Coercers must either return a value of the target type
    or raise an exception on failure.
    """

    def __init__(self) -> None:
        self._coercers: Dict[Type[Any], Coercer] = {}

    def register(self, target_type: Type[Any], coercer: Coercer) -> None:
        """
        Register a coercion function for a specific target type.
        """
        if not callable(coercer):
            raise TypeError("Coercer must be a callable.")

        self._coercers[target_type] = coercer

    def unregister(self, target_type: Type[Any]) -> None:
        """
        Remove a registered coercer for a given type.

        This operation is idempotent.
        """
        self._coercers.pop(target_type, None)

    def get(self, target_type: Type[Any]) -> Optional[Coercer]:
        """
        Retrieve a coercer for the given target type, if available.
        """
        return self._coercers.get(target_type)

    def clear(self) -> None:
        """
        Remove all registered coercers.

        Intended for test isolation only.
        """
        self._coercers.clear()


# Global coercion registry used by Cascade Core.
_registry = CoercionRegistry()


def register_coercer(target_type: Type[Any], coercer: Coercer) -> None:
    """
    Register a coercer for a target type.

    This does not validate or execute the coercer.
    """
    _registry.register(target_type, coercer)


def unregister_coercer(target_type: Type[Any]) -> None:
    """
    Unregister a coercer for a target type.
    """
    _registry.unregister(target_type)


def can_coerce(value: Any, target_type: Type[Any]) -> bool:
    """
    Check whether a value can be coerced to the target type.

    This function does not perform coercion. It only checks whether
    a coercer is registered for the target type.
    """
    return _registry.get(target_type) is not None


def coerce(value: Any, target_type: Type[Any]) -> Any:
    """
    Explicitly coerce a value to the target type.

    Parameters
    ----------
    value:
        The value to be coerced.
    target_type:
        The desired target type.

    Returns
    -------
    Any
        The coerced value.

    Raises
    ------
    CoercionError
        If no coercer is registered or coercion fails.
    """
    coercer = _registry.get(target_type)
    if coercer is None:
        raise CoercionError(
            value=value,
            target_type=target_type,
            message=f"No coercer registered for target type {target_type!r}.",
        )

    try:
        result = coercer(value)
    except Exception as exc:
        raise CoercionError(
            value=value,
            target_type=target_type,
            message=str(exc),
        ) from exc

    if not isinstance(result, target_type):
        raise CoercionError(
            value=value,
            target_type=target_type,
            message=(
                f"Coercer returned value {result!r} "
                f"which is not of type {target_type!r}."
            ),
        )

    return result


def clear_coercers() -> None:
    """
    Clear all registered coercers.

    Intended for test isolation only.
    """
    _registry.clear()
