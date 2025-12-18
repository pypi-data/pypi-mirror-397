# Cascade

[![Upload Python Package](https://github.com/XGCascade/cascade/actions/workflows/python-publish.yml/badge.svg?branch=main&event=check_run)](https://github.com/XGCascade/cascade/actions/workflows/python-publish.yml)

Cascade is a lightweight, explicit runtime validation framework for Python.

It is designed for developers who want **predictable validation**, **minimal magic**, and a **clean separation of concerns**.
Cascade intentionally avoids model-centric abstractions and implicit behavior.

If you prefer clarity over convenience magic, Cascade is built for you.

---

## Core Principles

Cascade is built around a few non-negotiable principles:

- **Explicit over implicit** – nothing runs unless you call it
- **Type validation is separate from rules**
- **No silent coercion**
- **Context-aware validation without global state**
- **Python semantics first**

Cascade is **not** a Pydantic replacement.
It solves a different problem with a smaller and more controlled scope.

---

## Installation

```bash
pip install --pre cascade
```

Cascade requires **Python 3.10+**.

---

## Basic Type Validation

```python
from cascade import validate_type

validate_type(10, int)          # passes
validate_type("10", int)        # raises TypeValidationError
```

Type validation is strict by default.
No coercion happens unless you explicitly request it.

---

## Typing Support

Cascade supports common typing constructs from `typing`:

```python
from typing import Optional, List, Dict
from cascade import validate_type

validate_type(None, Optional[int])
validate_type([1, 2, 3], List[int])
validate_type({"a": 1}, Dict[str, int])
```

Errors are explicit and deterministic.

---

## Custom Type Validation

You can register validators for custom types.

```python
from cascade import register_type, validate_type
from cascade.core.errors import TypeValidationError

class UserId(int):
    pass

def validate_user_id(value):
    if not isinstance(value, UserId):
        raise TypeValidationError(value=value, expected_type=UserId)

register_type(UserId, validate_user_id)

validate_type(UserId(1), UserId)   # passes
validate_type(1, UserId)           # raises TypeValidationError
```

Custom validators are explicit and easy to audit.

---

## Explicit Coercion

Cascade never performs implicit coercion.

If coercion is needed, it must be requested directly.

```python
from cascade import register_coercer, coerce

register_coercer(int, int)

value = coerce("123", int)
```

If coercion fails or no coercer is registered, a `CoercionError` is raised.

---

## Validation Rules

Rules are optional constraints applied **after** type validation.

```python
from cascade import validate_type
from cascade.rules import Min, Max

value = 10

validate_type(value, int)

for rule in (Min(5), Max(20)):
    rule(value)
```

Rules are simple callables.
They are never executed automatically.

---

## Profile-Based Validation (Contextual Rules)

Profiles allow validation rules to change based on execution context.
This is a core differentiator of Cascade.

```python
from cascade import validate_type
from cascade.rules import Min
from cascade.profiles import Profile, ProfileRegistry, use_profile

profiles = ProfileRegistry()

create = Profile("create")
create.add_rules("age", [Min(18)])

update = Profile("update")
update.add_rules("age", [Min(0)])

profiles.register(create)
profiles.register(update)

value = 15
validate_type(value, int)

with use_profile("create"):
    for rule in profiles.resolve_rules("age"):
        rule(value)   # fails

with use_profile("update"):
    for rule in profiles.resolve_rules("age"):
        rule(value)   # passes
```

Profiles are:
- Context-local
- Safe for async and concurrency
- Fully explicit

---

## Validated Dataclasses (Thin Sugar)

Cascade provides a **minimal dataclass helper**.
There is no validation on init or assignment unless explicitly called.

```python
from cascade import validated_dataclass, field
from cascade.rules import Min

@validated_dataclass
class User:
    id: int
    age: int = field(rules=[Min(18)])

user = User(id=1, age=20)
user.validate()      # passes

user.age = 10
user.validate()      # raises RuleValidationError
```

Dataclasses are plain Python dataclasses with explicit validation methods.

---

## What Cascade Is Not

Cascade does not try to be:

- A data modeling framework
- An ORM
- A serializer
- A request/response parser
- A schema generator

If you need those features, other tools may be a better fit.

---

## When to Use Cascade

Cascade is a good fit if you want:

- Runtime validation without model overhead
- Strict and predictable behavior
- Contextual validation logic
- Minimal framework intrusion

Cascade is intentionally small.
That is a feature, not a limitation.

---

## Stability

Cascade v1.0.0 is the first stable release.

Core APIs are considered frozen for the v1 series.
Breaking changes will only occur in major versions.

---

## License

MIT License
