"""The plugin's promises: the roster, the same laws everywhere, the guard hook, nothing left of what was removed."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROSTER = {a["role"]: a for a in json.loads((ROOT / "roster.json").read_text(encoding="utf-8"))["agents"]}
CORE = {"processor", "consultant", "nostradamus", "challenger", "reviewer", "controller", "memoryhole", "visualizer"}
SPECIALISTS = {"Device Technician", "Nutritionist", "Longevity Coach", "Sleep Coach", "Biohacker", "Research Curator",
               "Systems Engineer", "Science Writer"}
sys.path.insert(0, str(ROOT / "scripts"))
from build_agents import laws  # noqa: E402

LAWS = laws((ROOT / "playbooks/shared/persona.md").read_text(encoding="utf-8"))


def guard(event: dict, home: Path) -> str | None:
    done = subprocess.run([sys.executable, str(ROOT / "hooks/guard.py")], input=json.dumps(event), capture_output=True, text=True,
                          env={"JUMYO_HOME": str(home)}, check=True)
    return json.loads(done.stdout)["hookSpecificOutput"]["permissionDecisionReason"] if done.stdout else None


def bash(command: str, agent: str | None = None) -> dict:
    event = {"tool_name": "Bash", "tool_input": {"command": command}}
    return {**event, "agent_type": f"jumyo:{agent}"} if agent else event


def test_team_is_the_one_asked_for():
    assert CORE < set(ROSTER)
    assert {a["name"] for a in ROSTER.values() if a["tier"] == "specialist"} == SPECIALISTS


def test_every_agent_exists_and_carries_exactly_the_three_laws():
    files = {p.stem for p in (ROOT / "agents").glob("*.md")}
    assert files == set(ROSTER) - {"orchestrator"}
    assert len(re.findall(r"^\d\. \*\*", LAWS, re.M)) == 3
    for path in (ROOT / "agents").glob("*.md"):
        assert LAWS in path.read_text(encoding="utf-8"), path.name
    assert LAWS in (ROOT / "skills/start/SKILL.md").read_text(encoding="utf-8")


def test_roster_commands_exist():
    sys.path.insert(0, str(ROOT / "src"))
    from jumyo.commands import COMMANDS

    for agent in ROSTER.values():
        assert set(agent["commands"]) <= set(COMMANDS), agent["role"]


def test_playbook_references_resolve():
    pat = re.compile(r"`([a-z]+/[a-z][a-z-]*)`")
    roles = set(ROSTER) | {"shared"}
    for path in (ROOT / "playbooks").rglob("*.md"):
        for ref in pat.findall(path.read_text(encoding="utf-8")):
            if ref.split("/")[0] in roles:
                assert (ROOT / "playbooks" / ref / "SKILL.md").is_file(), f"{path}: {ref}"


@pytest.mark.parametrize(("command", "agent", "allowed"), [
    ("jumyo instances delete --instance me --confirm me", "coach", False),
    ("jumyo instances delete --instance me --confirm me", "memoryhole", True),
    ("jumyo instances delete --instance me --confirm me", None, False),
    ("jumyo plan record --instance me --file p.json", "sleep", False),
    ("jumyo plan record --instance me --file p.json", "nostradamus", True),
    ("jumyo state show --instance me --map x && jumyo ingest --instance me --file o", "biohacker", False),
    ("jumyo score --instance me", "nostradamus", False),
    ("jumyo score --instance me", "reviewer", True),
    ("python -m jumyo ingest", "coach", False),
    ("cat ~/.jumyo/inbox/lab.pdf", "coach", False),
    ("cat ~/.jumyo/inbox/lab.pdf", "processor", True),
    ("echo x >> ~/.jumyo/me/events.jsonl", "processor", False),
    ("ls -la ~/.jumyo", "coach", True),
])
def test_guard_on_commands(tmp_path, command, agent, allowed):
    assert (guard(bash(command, agent), tmp_path) is None) == allowed


def test_guard_blocks_unchosen_specialist(tmp_path):
    event = {"tool_name": "Agent", "tool_input": {"subagent_type": "jumyo:biohacker", "prompt": "{}"}}
    assert "not on this user's team" in guard(event, tmp_path)
    (tmp_path / "team.json").write_text('{"specialists": ["biohacker"]}', encoding="utf-8")
    assert guard(event, tmp_path) is None
    core = {"tool_name": "Agent", "tool_input": {"subagent_type": "jumyo:challenger", "prompt": "{}"}}
    assert guard(core, tmp_path) is None


def test_guard_leaves_other_agents_alone(tmp_path):
    assert guard({"tool_name": "Agent", "tool_input": {"subagent_type": "general-purpose"}}, tmp_path) is None


def test_guard_blocks_writing_the_log_and_reading_inbox(tmp_path):
    assert guard({"tool_name": "Write", "tool_input": {"file_path": "/x/events.jsonl"}}, tmp_path)
    read = {"tool_name": "Read", "tool_input": {"file_path": "/h/inbox/a.pdf"}, "agent_type": "jumyo:sleep"}
    assert guard(read, tmp_path)


def test_nothing_left_of_what_was_removed():
    banned = re.compile("|".join(["gr" + "ok", "insil" + "ico", "mother" + "ship", "panda" + "omics", "panda" + "claw",
                                  "evip" + "edia", "longevity[ _-]" + "master", r"\bx" + r"ai\b", "pl" + "si"]), re.I)
    skip = {"LICENSE"}
    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in skip or {".git", "__pycache__", ".pytest_cache", ".venv"} & set(path.parts) or any(p.endswith(".egg-info") for p in path.parts):
            continue
        if path.suffix in {".csv", ".png", ".pyc"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        found += [f"{path.relative_to(ROOT)}: {m.group(0)}" for m in banned.finditer(text)]
    assert not found, found[:20]


def test_the_system_is_named_in_every_place_a_user_sees_it():
    assert json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["displayName"] == "j\u016bmy\u014d"
    assert ROSTER["orchestrator"]["alias"] == "j\u016bmy\u014d"
    assert "Longevity Coach" in {a["name"] for a in ROSTER.values()}


def test_onboarding_never_asks_about_ethnicity():
    talk = (ROOT / "playbooks/orchestrator/talk/SKILL.md").read_text(encoding="utf-8")
    assert "Never ask about ethnicity" in talk and "ethnic background" not in talk
    assert "--ethnicity" not in (ROOT / "skills/start/SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("command", [
    "wc -l < ~/x/events.jsonl", "ls -la ~/x/events.jsonl 2>&1", "stat ~/x/events.jsonl > /tmp/out", "cat ~/x/events.jsonl | wc -l",
])
def test_guard_lets_reads_of_the_log_through(tmp_path, command):
    assert guard(bash(command, "processor"), tmp_path) is None


@pytest.mark.parametrize("command", [
    "echo x > ~/x/events.jsonl", "rm ~/x/events.jsonl", "sed -i '' s/a/b/ ~/x/events.jsonl", "cp /tmp/a ~/x/events.jsonl",
])
def test_guard_stops_writes_to_the_log(tmp_path, command):
    assert "append-only" in guard(bash(command, "processor"), tmp_path)


@pytest.mark.parametrize("command", [
    "git commit -q -F - <<'EOF'\nA title\n\njumyo data belongs to the user\nEOF",
    'git commit -m "first line\njumyo ingest is described here"',
    "cat > notes.md <<EOF\njumyo score --instance me\nEOF\nls",
])
def test_guard_ignores_text_that_only_looks_like_a_command(tmp_path, command):
    assert guard(bash(command, "coach"), tmp_path) is None


@pytest.mark.parametrize("command", [
    "bash <<'EOF'\njumyo score --instance me\nEOF",
    "cat notes.md <<EOF\ntext\nEOF\njumyo score --instance me",
    "git status; jumyo score --instance me",
    "X=\"a b\" jumyo score --instance me",
])
def test_guard_still_stops_real_commands(tmp_path, command):
    assert "not allowed" in guard(bash(command, "coach"), tmp_path)


def test_quoted_text_cannot_choose_a_profile(tmp_path):
    assert gate(session('git commit -m "jumyo profile use --name default\njumyo profile use --name default"'), tmp_path) is None
    assert not (tmp_path / ".jumyo/sessions/s1").exists()


def gate(event: dict, user_home: Path) -> str | None:
    done = subprocess.run([sys.executable, str(ROOT / "hooks/guard.py")], input=json.dumps(event), capture_output=True, text=True,
                          env={"HOME": str(user_home)}, check=True)
    return json.loads(done.stdout)["hookSpecificOutput"]["permissionDecisionReason"] if done.stdout else None


def session(command: str, sid: str = "s1", agent: str | None = None) -> dict:
    return {**bash(command, agent), "session_id": sid}


def test_new_session_reads_nothing_until_a_profile_is_chosen(tmp_path):
    assert "no profile is chosen" in gate(session("jumyo status --instance me"), tmp_path)
    assert "no profile is chosen" in gate(session("cat ~/.jumyo/me/subject.json"), tmp_path)
    read = {"tool_name": "Read", "tool_input": {"file_path": str(tmp_path / ".jumyo/memory.md")}, "session_id": "s1"}
    assert "no profile is chosen" in gate(read, tmp_path)
    assert gate(session("jumyo profile list"), tmp_path) is None
    assert gate(session("jumyo profile use --name default"), tmp_path) is None
    assert gate(session("jumyo status --instance me"), tmp_path) is None
    assert gate(read, tmp_path) is None
    assert "no profile is chosen" in gate(session("jumyo status --instance me", sid="other-account"), tmp_path)


def test_worker_cannot_choose_the_profile(tmp_path):
    assert gate(session("jumyo profile use --name default", agent="coach"), tmp_path)
    assert not (tmp_path / ".jumyo/sessions/s1").exists()


def test_session_stops_when_another_changes_the_profile(tmp_path):
    gate(session("jumyo profile use --name default"), tmp_path)
    (tmp_path / ".jumyo/active_profile").write_text("work", encoding="utf-8")
    assert "changed" in gate(session("jumyo status --instance me"), tmp_path)


def test_no_sharing_or_community_concept_in_the_laws():
    assert not re.search(r"communit|share|pool", LAWS, re.I)
