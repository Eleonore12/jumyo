"""The core loop, offline: record -> project -> screen -> plan -> adopt -> score."""

from __future__ import annotations

import json

HEADER = "effective_at,text,value,unit,code_system,code\n"
MARKERS = [("Albumin", 4.3, "g/dL", "1751-7"), ("Creatinine", 0.9, "mg/dL", "2160-0"), ("Glucose", 92, "mg/dL", "2345-7"),
           ("CRP", 1.1, "mg/L", "1988-5"), ("Lymphocytes", 32, "%", "736-9"), ("MCV", 90, "fL", "787-2"), ("RDW", 12.8, "%", "788-0"),
           ("ALP", 62, "U/L", "6768-6"), ("WBC", 5.6, "10*3/uL", "6690-2")]


def labs(path, when, crp=1.1):
    rows = [f"{when}T08:00:00Z,{t},{crp if t == 'CRP' else v},{u},loinc,{c}" for t, v, u, c in MARKERS]
    path.write_text(HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    return str(path)


def person(cli, tmp_path):
    assert cli("init", "--instance", "me", "--birth-year", "1975", "--sex", "F", "--relation", "self")["ok"]
    assert cli("ingest", "--instance", "me", "--csv", labs(tmp_path / "a.csv", "2026-01-10"))["data"]["counts"]["accepted"] == 9
    return cli("project", "--instance", "me", "--map", "blood_phenoage")["data"]["state"]


def plan(tmp_path):
    rule = [{"kind": "rule", "id": "jumyo.derive.phenoage"}]
    pred = {"map_id": "blood_phenoage", "coordinate": "crp", "target": "change_from_baseline", "horizon_days": 30,
            "method": "test", "evidence_class": "rule_derived", "basis": rule}
    doc = {"objective": "lower crp",
           "actions": [{"local_id": "a1", "description": "walking", "category": "exercise", "dose": "30 min", "schedule": "daily"}],
           "claims": [{"local_id": "c1", "statement": "rule", "evidence_class": "rule_derived", "sources": rule, "supports": ["a1"]}],
           "predictions": [{**pred, "local_id": "p1", "expected": -0.2, "low": -0.8, "high": 0.2, "driven_by": ["a1"]},
                           {**pred, "local_id": "p0", "expected": 0.0, "low": -0.5, "high": 0.5, "driven_by": []}],
           "revision_rule": {"review_after_days": 30, "continue_if": "ok", "modify_if": "no change", "stop_if": "adverse"}}
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return str(path)


def test_phenoage_is_computed_by_code(cli, tmp_path):
    state = person(cli, tmp_path)
    assert 40 < state["coordinates"]["phenoage"]["value"] < 45


def test_plan_needs_screening_then_scores_against_new_results(cli, tmp_path):
    person(cli, tmp_path)
    file = plan(tmp_path)
    blocked = cli("plan", "check", "--instance", "me", "--file", file)
    assert not blocked["ok"] and blocked["error"]["violations"][0]["rule"] == "G2"
    assert cli("screen", "--instance", "me", "--file", file)["ok"]
    recorded = cli("plan", "record", "--instance", "me", "--file", file)
    assert recorded["ok"], recorded
    plan_id = recorded["data"]["plan_id"]
    assert cli("plan", "adopt", "--instance", "me", "--plan", plan_id, "--start-on", "2026-01-15")["ok"]
    assert cli("ingest", "--instance", "me", "--csv", labs(tmp_path / "b.csv", "2026-02-14", crp=0.8))["ok"]
    assert cli("project", "--instance", "me", "--map", "blood_phenoage")["ok"]
    scored = cli("score", "--instance", "me")
    assert scored["ok"], scored
    assert len(scored["data"]["scored"]) == 2, scored["data"]


def test_handoff_routes_only_through_the_orchestrator(cli, tmp_path):
    state = person(cli, tmp_path)
    msg = {"type": "result", "sender": "coach", "recipient": "orchestrator", "thread": "t1", "skill": "coach/exercise",
           "instance": "me", "summary": "ok", "states": [{"map_id": "blood_phenoage", "state_hash": state["state_hash"]}]}
    good = tmp_path / "h.json"
    good.write_text(json.dumps(msg), encoding="utf-8")
    assert cli("handoff", "check", "--file", str(good))["ok"]
    good.write_text(json.dumps({**msg, "recipient": "sleep"}), encoding="utf-8")
    assert not cli("handoff", "check", "--file", str(good))["ok"]


def test_removed_roles_are_not_valid(cli, tmp_path):
    person(cli, tmp_path)
    path = tmp_path / "h.json"
    path.write_text(json.dumps({"type": "request", "sender": "orchestrator", "recipient": "panel", "thread": "t1",
                                "skill": "panel/roster", "instance": "me", "summary": "x"}), encoding="utf-8")
    assert not cli("handoff", "check", "--file", str(path))["ok"]


def test_egress_gate_shows_rules_never_text(cli, tmp_path):
    path = tmp_path / "out.txt"
    path.write_text("Born 1975-03-14, write to someone@example.com\n", encoding="utf-8")
    data = cli("egress", "check", "--file", str(path), "--instance", "me")["data"]
    assert data["cleared_by_code"] is False
    assert {v["rule"] for v in data["violations"]} == {"exact_date", "email"}
    assert "someone" not in json.dumps(data)


def test_team_choice(cli):
    assert cli("team", "show")["data"]["configured"] is False
    on = {a["role"] for a in cli("team", "set", "--specialists", "coach,sleep")["data"]["agents"] if a["on_team"]}
    assert {"coach", "sleep", "orchestrator", "challenger"} <= on and "biohacker" not in on
    assert not cli("team", "set", "--specialists", "astrologer")["ok"]


def test_screening_warns_when_nothing_is_known_about_the_person(cli, tmp_path):
    person(cli, tmp_path)
    codes = [w["code"] for w in cli("screen", "--instance", "me", "--file", plan(tmp_path))["warnings"]]
    assert "NO_CARE_CONTEXT" in codes


def test_profiles_keep_data_apart(tmp_path, monkeypatch, capsys):
    from jumyo.cli import main

    monkeypatch.delenv("JUMYO_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    def run(*args):
        try:
            main(list(args))
        except SystemExit:
            pass
        return json.loads(capsys.readouterr().out)

    assert run("init", "--instance", "me", "--sex", "F", "--relation", "self")["ok"]
    assert [p["has_data"] for p in run("profile", "list")["data"]["profiles"]] == [True]
    assert not run("profile", "use", "--name", "work")["ok"]
    made = run("profile", "use", "--name", "work", "--new")["data"]
    assert run("home")["data"]["path"] == made["path"]
    assert run("instances", "list")["data"] == [] or not run("instances", "list")["data"].get("instances")
    assert not run("profile", "use", "--name", "default", "--new")["ok"]
    assert run("profile", "use", "--name", "default")["ok"]
    assert run("home")["data"]["path"] == str(tmp_path / ".jumyo")
