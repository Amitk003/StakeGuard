"""Action log for StakeGuard.

Every decision is recorded with a timestamp: what was proposed, the risk
label, the confidence, and what the user decided. The log is a CSV file so
it is easy to read, export, and demo.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_LOG_PATH = Path("action_log.csv")

LOG_COLUMNS = [
    "timestamp",
    "match_id",
    "market",
    "odds",
    "stake",
    "risk_label",
    "confidence",
    "decision",
    "note",
]


@dataclass(frozen=True)
class DecisionRecord:
    """One logged decision."""

    timestamp: str
    match_id: str
    market: str
    odds: float
    stake: float
    risk_label: str
    confidence: str
    decision: str  # approved, rejected, or edited
    note: str = ""


def now_iso() -> str:
    """Return the current UTC time as an ISO string."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def log_decision(record: DecisionRecord, path: Path = DEFAULT_LOG_PATH) -> None:
    """Append one decision to the action log CSV."""
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow(asdict(record))


def read_log(path: Path = DEFAULT_LOG_PATH) -> list[dict[str, str]]:
    """Return every logged decision as a list of dicts."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
