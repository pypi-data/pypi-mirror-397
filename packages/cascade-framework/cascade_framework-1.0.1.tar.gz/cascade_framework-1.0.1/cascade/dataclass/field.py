"""
Field helpers for Cascade validated dataclasses.

This module only stores metadata.
No validation logic is executed here.
"""

from dataclasses import field as dc_field, MISSING
from typing import Any, Iterable, Optional


def field(
    *,
    rules: Optional[Iterable[Any]] = None,
    default: Any = MISSING,
    default_factory: Any = MISSING,
):
    """
    Define a dataclass field with optional validation rules.

    Parameters
    ----------
    rules:
        Iterable of callable rules.
        Each rule must expose a 'name' attribute.
    default:
        Default field value.
    default_factory:
        Factory for default value.
    """
    metadata = {}

    if rules is not None:
        metadata["cascade_rules"] = list(rules)

    kwargs = {"metadata": metadata}

    if default is not MISSING:
        kwargs["default"] = default

    if default_factory is not MISSING:
        kwargs["default_factory"] = default_factory

    return dc_field(**kwargs)
