"""
Global type registry for Cascade Core.

This registry is process-global by design.
Context-local or request-local registries are explicitly out of scope for v1.
"""

from typing import Any, Callable, Dict, Optional, Type


Validator = Callable[[Any], None]


class TypeRegistry:
    def __init__(self) -> None:
        self._validators: Dict[Type[Any], Validator] = {}

    def register(self, target_type: Type[Any], validator: Validator) -> None:
        if not callable(validator):
            raise TypeError("Validator must be callable.")

        self._validators[target_type] = validator

    def unregister(self, target_type: Type[Any]) -> None:
        self._validators.pop(target_type, None)

    def get(self, target_type: Type[Any]) -> Optional[Validator]:
        return self._validators.get(target_type)

    def clear(self) -> None:
        self._validators.clear()


_registry = TypeRegistry()


def register_type(target_type: Type[Any], validator: Validator) -> None:
    _registry.register(target_type, validator)


def unregister_type(target_type: Type[Any]) -> None:
    _registry.unregister(target_type)


def get_registered_validator(target_type: Type[Any]) -> Optional[Validator]:
    return _registry.get(target_type)


def clear_registry() -> None:
    """
    Clear the global registry.

    Intended strictly for test isolation.
    """
    _registry.clear()
