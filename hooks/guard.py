#!/usr/bin/env python3
"""PreToolUse guard: enforces in code what the roster says. Standard library only.

- an agent may run only the `jumyo` commands of its roster row;
- a specialist the user did not choose cannot be started;
- only the three record owners may open the inbox;
- nobody writes to an event log directly;
- a new session reads no data until a profile is chosen for it.

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
LOG_FILE = r"[^\s;|&]*events\.jsonl"
LOG_WRITE = re.compile(rf"(?<![0-9&])>>?\s*[\"']?{LOG_FILE}"  # a redirect into the log; 2>&1 and reads are fine
                       rf"|\b(?:rm|mv|truncate|tee|dd)\b[^;|&\n]*events\.jsonl"
                       rf"|\bsed\s+-i[^;|&\n]*events\.jsonl|\bperl\s+-\S*i[^;|&\n]*events\.jsonl"
                       rf"|\bcp\b[^;|&\n]*events\.jsonl[\"']?\s*(?:$|[;|&\n])")
HEREDOC = re.compile(r"(?P<head><<-?\s*['\"]?(?P<tag>\w+)['\"]?[^\n]*\n).*?\n\s*(?P=tag)[ \t]*(?=\n|$)", re.S)
FEEDS_SHELL = re.compile(r"\b(?:ba|z|da)?sh\b[^\n]*$")
QUOTED = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'", re.S)


def without_text(command: str) -> str:
    """The command with what is only text removed: heredoc bodies (unless fed to a shell) and quoted strings."""

    def body(match: re.Match[str]) -> str:
        return match.group(0) if FEEDS_SHELL.search(command[:match.start()]) else match.group("head")

    return QUOTED.sub('""', HEREDOC.sub(body, command))


OPEN_COMMANDS = {"doctor", "profile list", "profile use"}
DATA_MENTION = re.compile(r"\.jumyo(?!/\.venv)(?![\w-])")
PROFILE_USE = re.compile(r"\bprofile\s+use\b[^;|&\n]*?--name[=\s]+[\"']?([a-z0-9][a-z0-9_-]*)")
NO_PROFILE = ("no profile is chosen for this session, and this computer's jumyo data is shared by every Claude account on it. "
              "Run `jumyo profile list`, ask the user which profile to use, then `jumyo profile use --name <name>`.")


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": f"jūmyō guard: {reason}"}}))
    sys.exit(0)


def roster() -> dict[str, dict]:
    return {a["role"]: a for a in json.loads((ROOT / "roster.json").read_text(encoding="utf-8"))["agents"]}


def data_root() -> Path:
    return Path.home() / ".jumyo"


def active_profile() -> str:
    try:
        return (data_root() / "active_profile").read_text(encoding="utf-8").strip() or "default"
    except OSError:
        return "default"


def home_dir() -> Path:
    explicit = os.environ.get("JUMYO_HOME")
    if explicit:
        return Path(explicit)
    name = active_profile()
    return data_root() if name == "default" else data_root() / "profiles" / name


def session_marker(event: dict) -> Path | None:
    """Where this session's choice is kept; None when the gate does not apply (explicit JUMYO_HOME, no session id)."""
    session = str(event.get("session_id") or "")
    if os.environ.get("JUMYO_HOME") or not re.fullmatch(r"[\w-]{1,128}", session):
        return None
    return data_root() / "sessions" / session


def require_profile(marker: Path) -> None:
    try:
        picked = marker.read_text(encoding="utf-8").strip()
    except OSError:
        deny(NO_PROFILE)
    if picked != active_profile():
        deny(f"the active profile changed to {active_profile()!r} since this session chose {picked!r}. Ask the user which to use, "
             "then `jumyo profile use --name <name>`.")


def chosen() -> set[str]:
    home = home_dir()
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


def check_bash(event: dict, command: str, role: str, agents: dict[str, dict]) -> None:
    if LOG_WRITE.search(command):
        deny("the event log is append-only; corrections go through `jumyo retract`.")
    if role != "orchestrator":
        if DIRECT.search(command):
            deny("run the toolbelt only through the `jumyo` command.")
        if "/inbox/" in command and role not in INBOX_OWNERS:
            deny("only Data Processor, Device Technician and Nutritionist open inbox files.")
    allowed = set(agents[role]["commands"])
    invoked = CMD.findall(without_text(command))
    for first, second in invoked:
        if first not in allowed and f"{first} {second}".strip() not in allowed:
            deny(f"`jumyo {first} {second}`".replace(" `", "`") + f" is not allowed for {agents[role]['alias']}. Ask jūmyō to hand it to the owner.")
    marker = session_marker(event)
    if marker is None:
        return
    names = [f"{first} {second}".strip() for first, second in invoked]
    use = PROFILE_USE.search(command) if "profile use" in names else None
    if use and role == "orchestrator":
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(use.group(1), encoding="utf-8")
        return
    if DATA_MENTION.search(command) or any(n not in OPEN_COMMANDS and n.split()[0] not in OPEN_COMMANDS for n in names):
        require_profile(marker)


def check_file(event: dict, tool: str, tool_input: dict, role: str) -> None:
    path = str(tool_input.get("file_path") or "")
    marker = session_marker(event)
    root = str(data_root())
    if marker and (path == root or path.startswith(root + "/")) and not path.startswith(root + "/.venv"):
        require_profile(marker)
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
        check_bash(event, str(tool_input.get("command") or ""), role, agents)
    elif tool in ("Read", "Write", "Edit"):
        check_file(event, tool, tool_input, role)


if __name__ == "__main__":
    main()
