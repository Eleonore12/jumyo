"""`jumyo egress check`: the code gate on anything about a person that is about to leave the computer (an export
the user hands over, a draft report, a search query). It scans strings for identifying patterns and reports
{path, rule}, never the text it found. Judgment on top (playbook controller/egress) may only add rejections."""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterator
from typing import Any

from jumyo import files
from jumyo.paths import validate_id

_MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
_MONTH = rf"(?:{_MONTHS})[a-z]*\.?"
_DAY = r"\d{1,2}(?:st|nd|rd|th)?"
PATTERNS = {
    "exact_date": re.compile(rf"\b\d{{4}}-\d{{2}}-\d{{2}}|\b\d{{4}}[./-]\d{{1,2}}[./-]\d{{1,2}}\b"
                             rf"|(?<![\d.])\d{{1,2}}([./-])\d{{1,2}}\1(?:\d{{4}}|\d{{2}})(?![\d.])"
                             rf"|{_DAY}\s+{_MONTH}\s+\d{{2,4}}|\b{_MONTH}\s+{_DAY},?\s+\d{{2,4}}", re.I),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "id_number": re.compile(r"\d[\d\s().-]{6,}\d"),
    "internal_id": re.compile(r"\b(?:s_[0-9a-f]{12}|evt_[0-9a-f]{8,32})\b"),
}
YEARS = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")  # year ranges are not id numbers
FORBIDDEN_KEYS = frozenset({"subject_id", "instance", "birth_year", "event_id", "event_ids", "path", "original_path"})


def _normal(text: str) -> str:
    """NFKC with format characters (zero-width and the like) removed, so a pattern cannot be hidden."""
    return "".join(ch for ch in unicodedata.normalize("NFKC", text) if unicodedata.category(ch) != "Cf")


def _walk(obj: Any, at: str = "$") -> Iterator[tuple[str, Any, bool]]:
    if isinstance(obj, dict):
        for n, (key, value) in enumerate(obj.items()):
            yield f"{at}.#key[{n}]", key, True
            yield from _walk(value, f"{at}.#key[{n}]")
    elif isinstance(obj, list):
        for n, value in enumerate(obj):
            yield from _walk(value, f"{at}[{n}]")
    elif isinstance(obj, str):
        yield at, obj, False


def violations(doc: Any, instance: str | None = None) -> list[dict[str, str]]:
    """{path, rule} for every identifying pattern in `doc`. Empty means the code gate found nothing, not that it is safe."""
    named = re.compile(rf"\b{re.escape(instance)}\b", re.I) if instance else None
    out = []
    for path, value, is_key in _walk(doc):
        text = _normal(str(value))
        if is_key and text in FORBIDDEN_KEYS:
            out.append({"path": path, "rule": "forbidden_field"})
        for rule, pattern in PATTERNS.items():
            if pattern.search(YEARS.sub(" ", text) if rule == "id_number" else text):
                out.append({"path": path, "rule": rule})
        if named and named.search(text):
            out.append({"path": path, "rule": "instance_name"})
    return out


def check(file: str, instance: str | None = None) -> dict[str, Any]:
    """`jumyo egress check --file F`: a JSON file is walked field by field, any other file is read line by line."""
    if instance:
        validate_id(instance, "instance name")
    text = files.read_input_text(file)
    try:
        doc: Any = json.loads(text)
    except ValueError:
        doc = text.splitlines()
    found = violations(doc, instance)
    return {"cleared_by_code": not found, "violations": found}
