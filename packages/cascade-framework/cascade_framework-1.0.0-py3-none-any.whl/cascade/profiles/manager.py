"""
Profile registry and rule resolution logic.

This module defines how profiles map to rule sets.
It does not execute rules and does not perform validation.
"""

from typing import Dict, Iterable, List

from cascade.rules.base import Rule
from cascade.profiles.context import current_profile


class Profile:
    """
    Definition of a validation profile.

    A profile maps a field or logical key to a list of rules.
    """

    def __init__(self, name: str):
        self.name = name
        self._rules: Dict[str, List[Rule]] = {}

    def add_rules(self, key: str, rules: Iterable[Rule]) -> None:
        """
        Associate rules with a logical key under this profile.
        """
        self._rules[key] = list(rules)

    def get_rules(self, key: str) -> List[Rule]:
        """
        Retrieve rules for a given key in this profile.
        """
        return self._rules.get(key, [])


class ProfileRegistry:
    """
    Registry for validation profiles.

    This registry is intentionally explicit and not global-magic-driven.
    """

    def __init__(self):
        self._profiles: Dict[str, Profile] = {}

    def register(self, profile: Profile) -> None:
        """
        Register a profile definition.
        """
        self._profiles[profile.name] = profile

    def get(self, name: str) -> Profile | None:
        """
        Retrieve a profile by name.
        """
        return self._profiles.get(name)

    def resolve_rules(self, key: str) -> List[Rule]:
        """
        Resolve rules for the given key based on the active profile.

        If no profile is active or the profile is unknown,
        an empty rule list is returned.
        """
        name = current_profile()
        if name is None:
            return []

        profile = self._profiles.get(name)
        if profile is None:
            return []

        return profile.get_rules(key)
