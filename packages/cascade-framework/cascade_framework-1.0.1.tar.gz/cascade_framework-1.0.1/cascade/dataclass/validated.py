"""
Validated dataclass support for Cascade.

This module provides an explicit execution policy for field validation.

Execution order (fixed for v1):
1. Type validation
2. Field rules (in declared order)

Validation is never implicit.
"""

from dataclasses import dataclass, fields
from typing import Any, Type, TypeVar

from cascade.core.types import validate_type
from cascade.core.errors import ValidationError


T = TypeVar("T")


def validated_dataclass(cls: Type[T]) -> Type[T]:
    """
    Decorate a class as a validated dataclass.

    The resulting dataclass provides explicit validation methods:
    - validate()
    - validate_field(name)
    - is_valid()

    No validation occurs automatically on initialization or assignment.
    """
    cls = dataclass(cls)

    def validate(self) -> None:
        for f in fields(self):
            _validate_field(self, f.name)

    def validate_field(self, name: str) -> None:
        if not hasattr(self, name):
            raise AttributeError(f"Field '{name}' does not exist.")

        _validate_field(self, name)

    def is_valid(self) -> bool:
        try:
            self.validate()
            return True
        except ValidationError:
            return False

    cls.validate = validate
    cls.validate_field = validate_field
    cls.is_valid = is_valid

    return cls


def _validate_field(instance: Any, name: str) -> None:
    value = getattr(instance, name)
    annotation = instance.__annotations__.get(name)

    if annotation is not None:
        validate_type(value, annotation)

    field_info = next(f for f in fields(instance) if f.name == name)
    rules = field_info.metadata.get("cascade_rules", [])

    for rule in rules:
        if not callable(rule) or not hasattr(rule, "name"):
            raise TypeError(
                "Field rules must be callable and expose a 'name' attribute."
            )

        rule(value)
