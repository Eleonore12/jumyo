"""The team: `roster.json` (the single source for names, tiers, commands) and the specialists this user chose
(<JUMYO_HOME>/team.json). The plugin's guard hook reads the same two files, so an unchosen specialist cannot run."""

from __future__ import annotations

import json
from typing import Any

from jumyo.errors import ValidationError
from jumyo.files import atomic_write_json
from jumyo.paths import REPO_ROOT, jumyo_home

SPECIALIST = "specialist"


def roster() -> list[dict[str, Any]]:
    return json.loads((REPO_ROOT / "roster.json").read_text(encoding="utf-8"))["agents"]


def chosen() -> list[str]:
    path = jumyo_home() / "team.json"
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("specialists", [])


def show() -> dict[str, Any]:
    on = set(chosen())
    agents = [{"role": a["role"], "name": a["name"], "tier": a["tier"], "description": a["description"],
               "on_team": a["tier"] != SPECIALIST or a["role"] in on} for a in roster()]
    return {"configured": (jumyo_home() / "team.json").is_file(), "agents": agents}


def set_specialists(specialists: str) -> dict[str, Any]:
    known = {a["role"] for a in roster() if a["tier"] == SPECIALIST}
    picked = [] if specialists.strip() == "none" else [s.strip() for s in specialists.split(",") if s.strip()]
    unknown = sorted(set(picked) - known)
    if unknown:
        raise ValidationError(f"not a specialist: {', '.join(unknown)}", hint=f"choose among: {', '.join(sorted(known))}")
    jumyo_home().mkdir(parents=True, exist_ok=True)
    atomic_write_json(jumyo_home() / "team.json", {"specialists": sorted(set(picked))})
    return show()
