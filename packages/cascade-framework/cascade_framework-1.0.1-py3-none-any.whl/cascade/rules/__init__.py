"""
Validation rules for Cascade.

Rules are optional constraints applied after successful type validation.
They are explicit, composable, and never executed implicitly.
"""

from cascade.rules.base import Rule
from cascade.rules.common import (
    Min,
    Max,
    Length,
    Pattern,
)

__all__ = [
    "Rule",
    "Min",
    "Max",
    "Length",
    "Pattern",
]
