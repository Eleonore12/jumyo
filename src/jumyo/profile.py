"""Profiles: separate data folders under ~/.jumyo. The data belongs to the macOS user, not to a Claude account, so every
new session must choose a profile before any data is read (hooks/guard.py enforces it). JUMYO_HOME overrides all of this."""

from __future__ import annotations

import os
from typing import Any

from jumyo.errors import NotFound, ValidationError
from jumyo.files import atomic_write_text
from jumyo.paths import DEFAULT_PROFILE, active_profile, data_root, jumyo_home, profile_dir, validate_id


def _has_data(name: str) -> bool:
    folder = profile_dir(name)
    return folder.is_dir() and any((child / "subject.json").is_file() for child in folder.iterdir() if child.is_dir())


def _names() -> list[str]:
    extra = data_root() / "profiles"
    return [DEFAULT_PROFILE, *sorted(p.name for p in extra.iterdir() if p.is_dir())] if extra.is_dir() else [DEFAULT_PROFILE]


def list_profiles() -> dict[str, Any]:
    """Names and whether each holds data; nothing about what the data says."""
    active = active_profile()
    return {"explicit_home": bool(os.environ.get("JUMYO_HOME")),
            "profiles": [{"name": n, "active": n == active, "has_data": _has_data(n)} for n in _names()]}


def use(name: str, new: bool = False) -> dict[str, Any]:
    if os.environ.get("JUMYO_HOME"):
        raise ValidationError("JUMYO_HOME is set, so profiles do not apply", hint="unset JUMYO_HOME to use profiles")
    validate_id(name, "profile name")
    known = name in _names()
    if new and known and _has_data(name):
        raise ValidationError(f"profile {name!r} already holds data", hint="choose another name")
    if not new and not known:
        raise NotFound(f"profile {name!r} does not exist", code="PROFILE_NOT_FOUND", hint="add --new to create it")
    profile_dir(name).mkdir(parents=True, exist_ok=True)
    atomic_write_text(data_root() / "active_profile", name + "\n")
    return {"profile": name, "path": str(profile_dir(name))}


def home() -> dict[str, str]:
    return {"path": str(jumyo_home())}
