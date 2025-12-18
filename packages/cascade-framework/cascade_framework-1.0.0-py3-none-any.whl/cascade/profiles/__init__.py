"""
Profile-based validation support for Cascade.

Profiles provide contextual rule selection without affecting
type checking or coercion behavior.
"""

from cascade.profiles.context import use_profile, current_profile
from cascade.profiles.manager import Profile, ProfileRegistry

__all__ = [
    "use_profile",
    "current_profile",
    "Profile",
    "ProfileRegistry",
]
