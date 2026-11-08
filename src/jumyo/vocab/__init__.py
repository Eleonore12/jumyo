"""Every enum in jūmyō, nothing enumerated inline elsewhere."""

from __future__ import annotations

import re
from collections.abc import Iterable
from enum import StrEnum
from typing import Any


def fold(text: Any) -> str:
    """Lower-case letters and digits only, so `ABC-123`, `abc 123` and `abc123` compare equal."""
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


class EvidenceClass(StrEnum):
    # member order is significant: strongest first (rank 4 .. 0)
    EVIDENCE_BACKED = "evidence_backed"
    RULE_DERIVED = "rule_derived"
    MODEL_DERIVED = "model_derived"
    HYPOTHESIS_ONLY = "hypothesis_only"
    UNKNOWN = "unknown"

    @property
    def rank(self) -> int:
        members = list(EvidenceClass)
        return len(members) - 1 - members.index(self)

    @classmethod
    def top(cls, values: Iterable[EvidenceClass]) -> EvidenceClass | None:
        """The strongest of values (None when there are none)."""
        return max(values, key=lambda e: e.rank, default=None)


class CorrespondenceType(StrEnum):
    TERMINOLOGY = "terminology"
    EXPERT = "expert"
    STATISTICAL = "statistical"
    MECHANISTIC = "mechanistic"
    VALIDATED = "validated"
    UNMAPPED = "unmapped"


class ClaimLevel(StrEnum):
    DESIGNED = "designed"
    INSTANTIATED = "instantiated"
    EXERCISED = "exercised"


class BotRole(StrEnum):
    """The jūmyō team on Claude Code; the roster (slug -> display name, core vs opt-in specialists, skills) is playbooks/shared/team.
    Every handoff has the orchestrator (jūmyō) on one end; only jūmyō talks to the user."""

    ORCHESTRATOR = "orchestrator"
    PROCESSOR = "processor"
    CONSULTANT = "consultant"
    NOSTRADAMUS = "nostradamus"
    CHALLENGER = "challenger"
    REVIEWER = "reviewer"
    CONTROLLER = "controller"
    MEMORYHOLE = "memoryhole"
    VISUALIZER = "visualizer"
    WEARABLES = "wearables"
    NUTRITIONIST = "nutritionist"
    COACH = "coach"
    SLEEP = "sleep"
    BIOHACKER = "biohacker"
    EXPLORER = "explorer"
    ENGINEER = "engineer"
    WRITER = "writer"


class HandoffKind(StrEnum):
    REQUEST = "request"  # orchestrator -> another bot: run a skill
    RESULT = "result"  # another bot -> orchestrator
    QUESTION = "question"  # another bot -> orchestrator: for the user (only the orchestrator asks the user)
    ANSWER = "answer"  # orchestrator -> the asking bot: the user's answers


class EventType(StrEnum):
    OBSERVATION = "observation"
    RETRACTION = "retraction"
    SCREENING = "screening"
    PLAN = "plan"
    PLAN_STATUS = "plan_status"
    PREDICTION_SCORE = "prediction_score"


class ObservationKind(StrEnum):
    MEASUREMENT = "measurement"
    MEDICATION = "medication"
    CONDITION = "condition"
    ALLERGY = "allergy"
    INTERVENTION = "intervention"
    SYMPTOM = "symptom"
    LIFESTYLE = "lifestyle"
    ARTIFACT = "artifact"
    NOTE = "note"
    GOAL = "goal"  # what the user wants to reach, e.g. "run 10 km"; resolved when reached or dropped
    PREFERENCE = "preference"  # standing choices and constraints: diet, budget band, schedule


class ClinicalStatus(StrEnum):
    ACTIVE = "active"
    STOPPED = "stopped"
    RESOLVED = "resolved"
    UNKNOWN = "unknown"


class CodeSystem(StrEnum):
    LOINC = "loinc"
    RXNORM = "rxnorm"
    SNOMED = "snomed"
    ICD10CM = "icd10cm"
    CPG = "cpg"
    FREE = "free"


class OriginKind(StrEnum):
    USER_UPLOAD = "user_upload"
    FHIR = "fhir"
    CSV = "csv"
    LLM_EXTRACTION = "llm_extraction"
    DEVICE = "device"
    METHYLATION = "methylation"
    EXTENSION = "extension"  # produced by an importer extension


class ExtensionKind(StrEnum):
    IMPORTER = "importer"  # Life: a new input format -> observations
    DERIVER = "deriver"  # Map: a new derived value (derive engine extension)
    EVIDENCE_SOURCE = "evidence_source"  # Policy: a new place to search for evidence


class TimeBasis(StrEnum):
    DOCUMENT = "document"
    USER_STATED = "user_stated"
    ASSUMED = "assumed"


class Sex(StrEnum):
    M = "M"
    F = "F"
    X = "X"
    UNKNOWN = "unknown"


class NoteTopic(StrEnum):
    TARGET = "target"
    REPURPOSING = "repurposing"
    METHOD = "method"
    HALLMARK = "hallmark"


class Ethnicity(StrEnum):
    EUROPEAN = "european"
    AFRICAN = "african"
    MIDDLE_EASTERN = "middle_eastern"
    SOUTH_ASIAN = "south_asian"
    EAST_ASIAN = "east_asian"
    SOUTHEAST_ASIAN = "southeast_asian"
    LATIN_AMERICAN = "latin_american"
    OTHER = "other"


class LabFlag(StrEnum):
    """The lab's own mark on a result, as printed (H, L, HH/LL or critical, A or *)."""

    HIGH = "high"
    LOW = "low"
    CRITICAL = "critical"
    ABNORMAL = "abnormal"


class Relation(StrEnum):
    """Who an instance is, relative to the user. Instance names are neutral labels (mother, sample-1), never names."""

    SELF = "self"
    FAMILY = "family"
    OTHER = "other"
    SAMPLE = "sample"  # a story or test person, not a real one


class CoordinateKind(StrEnum):
    MEASURED = "measured"
    DERIVED = "derived"
    SET = "set"


class ExportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"


class ReportFormat(StrEnum):
    HTML = "html"
    PDF = "pdf"


class ValueStatus(StrEnum):
    PRESENT = "present"
    STALE = "stale"
    MISSING = "missing"
    ERROR = "error"


class Severity(StrEnum):
    # member order is significant: mildest first (rank 0 .. 2)
    NONE = "none"
    CAUTION = "caution"
    BLOCK = "block"

    @property
    def rank(self) -> int:
        return list(Severity).index(self)

    @classmethod
    def top(cls, values: Iterable[Severity]) -> Severity:
        """The most severe of values (none when there are none)."""
        return max(values, key=lambda s: s.rank, default=cls.NONE)


class ActionCategory(StrEnum):
    DRUG = "drug"
    SUPPLEMENT = "supplement"
    DIET = "diet"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    TEST = "test"
    OTHER = "other"


class PlanState(StrEnum):
    PROPOSED = "proposed"
    ADOPTED = "adopted"
    COMPLETED = "completed"
    STOPPED = "stopped"
    SUPERSEDED = "superseded"


class PlanDecision(StrEnum):
    ADOPT = "adopt"
    CONTINUE = "continue"
    MODIFY = "modify"
    STOP = "stop"
    COMPLETE = "complete"


class PredictionTarget(StrEnum):
    LEVEL = "level"
    CHANGE_FROM_BASELINE = "change_from_baseline"


class ScoreStatus(StrEnum):
    SCORED = "scored"
    MISSED = "missed"
    VOID = "void"


class SourceKind(StrEnum):
    PMID = "pmid"
    DOI = "doi"
    NCT = "nct"
    LABEL = "label"
    MODEL = "model"
    RULE = "rule"


class BlockType(StrEnum):
    MARKDOWN = "markdown"
    KV = "kv"
    TABLE = "table"
    TIMESERIES = "timeseries"
    LIST = "list"
    TIMELINE = "timeline"


# Small enums the spec writes inline in section 3/4/8/9; kept here so there is one vocabulary.


class Comparator(StrEnum):
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="


class DeriveEngine(StrEnum):
    NATIVE = "native"  # built-in formulas (jumyo.map.derive)
    EXPR = "expr"  # a safe formula written in the map (jumyo.map.formula)
    EXTENSION = "extension"  # an installed deriver extension (jumyo.extensions); model = extension id
    BIOLEARN = "biolearn"


class MatchKind(StrEnum):
    CODE = "code"
    DERIVED = "derived"


class Direction(StrEnum):
    UP = "up"
    DOWN = "down"
    NONE = "none"


class SourceStatus(StrEnum):
    OK = "ok"
    NOT_FOUND = "not_found"
    ERROR = "error"


class ReferenceKind(StrEnum):
    CODE_SYSTEM = "code_system"
    TERMINOLOGY_API = "terminology_api"
    EVIDENCE_SOURCE = "evidence_source"
    LABEL_SOURCE = "label_source"
    CLOCK_LIBRARY = "clock_library"
    MODEL = "model"
    PAPER = "paper"
    JOURNAL = "journal"
    DIGEST = "digest"  # curated paper digests, event calendars, industry reports
    BASE_RATE = "base_rate"  # population mortality, incidence and prevalence tables: absolute risks for predictions
    DEVICE_DATA = "device_data"  # wearable and device data platforms (wearables/import)


class SearchSource(StrEnum):
    PUBMED = "pubmed"
    EUROPEPMC = "europepmc"
    CTGOV = "ctgov"
    OPENFDA = "openfda"


# Source kinds that make a claim evidence_backed (ClaimInput coherence).
LITERATURE_SOURCE_KINDS = frozenset(
    {SourceKind.PMID, SourceKind.DOI, SourceKind.NCT, SourceKind.LABEL}
)


# ---------------------------------------------------------------- Policy gates, due states


class GateId(StrEnum):
    """Plan gates; the `rule` of a plan violation."""

    G1 = "G1"  # map exists and its projected state is current
    G2 = "G2"  # a fresh screening event for every action and the current care context
    G3 = "G3"  # screening outcome: block drops the action, caution needs an acknowledgement
    G4 = "G4"  # claim coherence (a parse error of the plan contract)
    G5 = "G5"  # every cited source verified
    G6 = "G6"  # actions supported by claims of the map's minimum evidence class
    G7 = "G7"  # predictions on predictable coordinates with a usable baseline
    G8 = "G8"  # supersedes a live plan


class DueState(StrEnum):
    """`jumyo due`: a prediction whose score window is open."""

    DUE = "due"  # an eligible observation exists; `jumyo score` will score it
    MISSED = "missed"  # the window closed without one
    AWAITING = "awaiting"  # the window is open, no eligible observation yet
