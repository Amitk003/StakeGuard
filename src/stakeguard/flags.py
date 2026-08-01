"""Rule-based safety flags for StakeGuard.

These checks are simple and transparent. Each flag has a reason string so
the evidence layer can show why the flag was raised.
"""

from __future__ import annotations

from dataclasses import dataclass

# Words and short phrases that suggest emotional or tilt betting.
EMOTIONAL_PATTERNS: list[str] = [
    "tilt",
    "revenge",
    "chase",
    "chasing",
    "lost 3",
    "lost three",
    "lost 2",
    "lost two",
    "lost last",
    "can't lose",
    "cannot lose",
    "double down",
    "make it back",
    "get even",
    "bet it all",
    "sure thing",
    "feeling lucky",
    "desperate",
    "angry",
    "frustrated",
]

# Stake above this share of the bankroll is flagged as a warning.
MAX_STAKE_PERCENT = 10.0

# Stake above this share is flagged as a danger.
DANGER_STAKE_PERCENT = 20.0

# A positive edge below this value counts as poor value.
POOR_VALUE_THRESHOLD = -0.02


@dataclass(frozen=True)
class Flag:
    """One raised safety flag with a human-readable reason."""

    name: str
    reason: str
    severity: str  # info, warning, or danger


def check_mood_note(note: str) -> list[Flag]:
    """Return flags for emotional language in the user's note."""
    if not note:
        return []
    lowered = note.lower()
    found = [p for p in EMOTIONAL_PATTERNS if p in lowered]
    if not found:
        return []
    return [
        Flag(
            name="emotional_language",
            reason=f"The note contains emotional language: {', '.join(found)}",
            severity="warning",
        )
    ]


def check_stake_size(stake_percent: float) -> list[Flag]:
    """Return a flag when the stake is too big compared to the bankroll."""
    if stake_percent > DANGER_STAKE_PERCENT:
        return [
            Flag(
                name="oversized_stake",
                reason=(
                    f"The stake is {stake_percent:.1f}% of the bankroll, "
                    f"far above the safe limit of {MAX_STAKE_PERCENT:.0f}%"
                ),
                severity="danger",
            )
        ]
    if stake_percent > MAX_STAKE_PERCENT:
        return [
            Flag(
                name="oversized_stake",
                reason=(
                    f"The stake is {stake_percent:.1f}% of the bankroll, "
                    f"above the safe limit of {MAX_STAKE_PERCENT:.0f}%"
                ),
                severity="warning",
            )
        ]
    return []


def check_poor_value(edge_value: float) -> list[Flag]:
    """Return a flag when the bet has clearly negative value."""
    if edge_value < POOR_VALUE_THRESHOLD:
        return [
            Flag(
                name="poor_value",
                reason=(
                    f"The odds imply a worse chance than the estimated "
                    f"probability. Edge is {edge_value:.2%}"
                ),
                severity="warning",
            )
        ]
    return []


def check_high_odds(odds: float) -> list[Flag]:
    """Return a flag for very long shot bets, which are high variance."""
    if odds >= 5.0:
        return [
            Flag(
                name="high_variance",
                reason="The odds are long, so this bet is high variance",
                severity="warning",
            )
        ]
    return []


def collect_flags(
    note: str,
    stake_percent: float,
    edge_value: float,
    odds: float,
) -> list[Flag]:
    """Run all rule checks and return every raised flag."""
    flags: list[Flag] = []
    flags.extend(check_mood_note(note))
    flags.extend(check_stake_size(stake_percent))
    flags.extend(check_poor_value(edge_value))
    flags.extend(check_high_odds(odds))
    return flags
