"""
Public API surface for Cascade.

This module defines the stable and supported entry points of the framework.
Anything not exported here is considered internal and may change without notice.

Design principles:
- Explicit over implicit
- Small and stable API
- No convenience magic
"""

# Core type validation
from cascade.core.types import validate_type

# Type registry
from cascade.core.registry import (
    register_type,
    unregister_type,
)

# Explicit coercion utilities
from cascade.core.coercion import (
    register_coercer,
    unregister_coercer,
    can_coerce,
    coerce,
)

# Error hierarchy
from cascade.core.errors import (
    CascadeError,
    ValidationError,
    TypeValidationError,
    RuleValidationError,
    CoercionError,
)

# Dataclass execution policy
from cascade.dataclass import (
    validated_dataclass,
    field,
)

__all__ = [
    # Core validation
    "validate_type",

    # Type registry
    "register_type",
    "unregister_type",

    # Coercion
    "register_coercer",
    "unregister_coercer",
    "can_coerce",
    "coerce",

    # Errors
    "CascadeError",
    "ValidationError",
    "TypeValidationError",
    "RuleValidationError",
    "CoercionError",

    # Dataclass utilities
    "validated_dataclass",
    "field",
]
