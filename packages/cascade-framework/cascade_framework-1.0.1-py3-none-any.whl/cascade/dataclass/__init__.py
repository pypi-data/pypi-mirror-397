"""
Thin dataclass utilities for Cascade.

This package provides minimal sugar on top of Cascade Core.
It intentionally avoids magic behavior and implicit validation.
"""

from cascade.dataclass.field import field
from cascade.dataclass.validated import validated_dataclass

__all__ = [
    "field",
    "validated_dataclass",
]
