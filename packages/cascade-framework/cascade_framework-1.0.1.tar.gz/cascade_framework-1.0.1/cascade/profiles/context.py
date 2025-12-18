"""
Profile context management.

This module provides a lightweight context mechanism
for activating a validation profile.
"""

from contextvars import ContextVar
from contextlib import contextmanager
from typing import Iterator, Optional


_current_profile: ContextVar[Optional[str]] = ContextVar(
    "cascade_current_profile",
    default=None,
)


def current_profile() -> Optional[str]:
    """
    Return the name of the currently active profile, if any.
    """
    return _current_profile.get()


@contextmanager
def use_profile(name: str) -> Iterator[None]:
    """
    Activate a profile within a controlled context.

    Profiles are context-local and safe for concurrent and async usage.
    """
    token = _current_profile.set(name)
    try:
        yield
    finally:
        _current_profile.reset(token)
