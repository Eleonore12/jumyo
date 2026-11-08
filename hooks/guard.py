#!/usr/bin/env python3
"""PreToolUse guard: enforces in code what the roster says. Standard library only.

- an agent may run only the `jumyo` commands of its roster row;
- a specialist the user did not choose cannot be started;
- only the three record owners may open the inbox;
- nobody writes to an event log directly.

Guard rails, not a sandbox: a malformed input falls through to the normal permission flow."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "jumyo"
INBOX_OWNERS = {"processor", "wearables", "nutritionist"}
CMD = re.compile(r"(?:^|[;&|(]\s*|\n\s*)(?:[A-Za-z_]+=\S+\s+)*(?:\S*/)?jumyo\s+([a-z][a-z-]*)(?:\s+([a-z][a-z-]*))?")
DIRECT = re.compile(r"-m\s+jumyo\b|import\s+jumyo\b")
LOG_WRITE = re.compile(r"events\.jsonl.*(?:>|\btee\b)|(?:>|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i|\btruncate\b|\bperl\s+-|\btee\b).*events\.jsonl")


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": f"jūmyō guard: {reason}"}}))
    sys.exit(0)


def roster() -> dict[str, dict]:
    return {a["role"]: a for a in json.loads((ROOT / "roster.json").read_text(encoding="utf-8"))["agents"]}


def chosen() -> set[str]:
    home = Path(os.environ.get("JUMYO_HOME") or Path.home() / ".jumyo")
    try:
        return set(json.loads((home / "team.json").read_text(encoding="utf-8")).get("specialists", []))
    except (OSError, ValueError):
        return set()


def role_of(event: dict, agents: dict[str, dict]) -> str:
    last = str(event.get("agent_type") or "").split(":")[-1]
    return last if last in agents else "orchestrator"


def check_agent(tool_input: dict, agents: dict[str, dict]) -> None:
    kind = str(tool_input.get("subagent_type") or "")
    if not kind.startswith(f"{PLUGIN}:"):
        return
    role = kind.split(":", 1)[1]
    agent = agents.get(role)
    if agent is None or role == "orchestrator":
        deny(f"{role} is not a worker on the roster.")
    if agent["tier"] == "specialist" and role not in chosen():
        deny(f"{agent['name']} is not on this user's team. Offer to add it (jumyo team set); do not stand in for it.")


def check_bash(command: str, role: str, agents: dict[str, dict]) -> None:
    if LOG_WRITE.search(command):
        deny("the event log is append-only; corrections go through `jumyo retract`.")
    if role != "orchestrator":
        if DIRECT.search(command):
            deny("run the toolbelt only through the `jumyo` command.")
        if "/inbox/" in command and role not in INBOX_OWNERS:
            deny("only Data Processor, Device Technician and Nutritionist open inbox files.")
    allowed = set(agents[role]["commands"])
    for first, second in CMD.findall(command):
        if first not in allowed and f"{first} {second}".strip() not in allowed:
            deny(f"`jumyo {first} {second}`".replace(" `", "`") + f" is not allowed for {agents[role]['alias']}. Ask jūmyō to hand it to the owner.")


def check_file(tool: str, tool_input: dict, role: str) -> None:
    path = str(tool_input.get("file_path") or "")
    if tool in ("Write", "Edit") and path.endswith("events.jsonl"):
        deny("the event log is append-only; corrections go through `jumyo retract`.")
    if role != "orchestrator" and "/inbox/" in path and role not in INBOX_OWNERS and tool == "Read":
        deny("only Data Processor, Device Technician and Nutritionist open inbox files.")


def main() -> None:
    try:
        event = json.load(sys.stdin)
        agents = roster()
    except (OSError, ValueError):
        return
    tool, tool_input = event.get("tool_name"), event.get("tool_input") or {}
    role = role_of(event, agents)
    if tool in ("Agent", "Task"):
        check_agent(tool_input, agents)
    elif tool == "Bash":
        check_bash(str(tool_input.get("command") or ""), role, agents)
    elif tool in ("Read", "Write", "Edit"):
        check_file(tool, tool_input, role)


if __name__ == "__main__":
    main()
