"""Evidence and confidence helpers for StakeGuard.

Confidence tells the user how much to trust the assessment. It is based on
data quality, not guesswork. The refusal helper keeps the app honest: when
the data cannot answer, the app says so.
"""

from __future__ import annotations

from dataclasses import dataclass

CONFIDENCE_HIGH = "High"
CONFIDENCE_MEDIUM = "Medium"
CONFIDENCE_LOW = "Low"


@dataclass(frozen=True)
class EvidenceBundle:
    """The evidence behind one assessment."""

    match_id: str
    home_team: str
    away_team: str
    market: str
    odds: float
    win_probability: float
    implied_probability: float
    home_form: str
    away_form: str
    h2h_notes: str


def confidence(
    has_match: bool,
    win_probability: float | None,
    flags_count: int,
    note_provided: bool,
) -> str:
    """Return a confidence label from High, Medium, or Low.

    Rules:
    - Without a match or a win probability, confidence is Low.
    - A match with a probability is Medium at minimum.
    - Flags or an emotional note lower the label by one step.
    - Clean input with a known match is High.
    """
    if not has_match or win_probability is None:
        return CONFIDENCE_LOW

    label = CONFIDENCE_HIGH
    if flags_count > 0 or note_provided:
        label = CONFIDENCE_MEDIUM
    if flags_count >= 2:
        label = CONFIDENCE_LOW
    return label


def refuse_reason(match_exists: bool, market_supported: bool) -> str | None:
    """Return a refusal message, or None when the bet can be assessed."""
    if not match_exists:
        return "Not enough evidence: this match is not in the dataset."
    if not market_supported:
        return "Not enough evidence: this market is not supported."
    return None
