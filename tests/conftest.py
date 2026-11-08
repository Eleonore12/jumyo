from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("JUMYO_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture
def cli(home, capsys):
    from jumyo.cli import main

    def run(*args: str) -> dict:
        try:
            main(list(args))
        except SystemExit:
            pass
        return json.loads(capsys.readouterr().out)

    return run
