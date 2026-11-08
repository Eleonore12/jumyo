"""JSON Schemas of the documents the agents read or writes, exported to contracts/ (`jumyo contracts export`)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from jumyo.files import atomic_write_json
from jumyo.life.models import ObservationInput
from jumyo.map.models import MapContract, StateDocument
from jumyo.map.protocol import Handoff
from jumyo.paths import REPO_ROOT
from jumyo.policy.models import PlanInput
from jumyo.report import DashboardPayload

EXPORTED: tuple[type[BaseModel], ...] = (ObservationInput, MapContract, PlanInput, StateDocument, DashboardPayload, Handoff)


def export_json_schemas(out_dir: Path | str = REPO_ROOT / "contracts") -> list[str]:
    """Write contracts/<Model>.schema.json for the exported models; returns the written paths."""
    out = Path(out_dir)
    written = []
    for m in EXPORTED:
        path = out / f"{m.__name__}.schema.json"
        atomic_write_json(path, {"$schema": "https://json-schema.org/draft/2020-12/schema", **m.model_json_schema()})
        written.append(str(path))
    return written
