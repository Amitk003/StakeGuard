"""Core risk math for StakeGuard.

All numbers here are computed in plain Python. The LLM is never used for
math. These functions are small and easy to test.
"""

from __future__ import annotations

from dataclasses import dataclass

RISK_LOW = "Low"
RISK_MEDIUM = "Medium"
RISK_HIGH = "High"


@dataclass(frozen=True)
class RiskAssessment:
    """The calculated part of a bet assessment."""

    match_id: str
    market: str
    odds: float
    stake: float
    implied_probability: float
    win_probability: float
    expected_value: float
    edge: float
    stake_percent_bankroll: float
    risk_score: float
    risk_label: str


def implied_probability(odds: float) -> float:
    """Convert decimal odds into implied probability.

    Example: odds 2.0 means the market implies a 50% chance.
    """
    if odds <= 1.0:
        raise ValueError("odds must be greater than 1.0")
    return 1.0 / odds


def expected_value(stake: float, odds: float, win_probability: float) -> float:
    """Return the expected profit of a bet in the same currency as stake.

    Positive EV means the bet is good on average. Negative EV means it is
    bad on average.
    """
    if stake < 0:
        raise ValueError("stake must not be negative")
    if odds <= 1.0:
        raise ValueError("odds must be greater than 1.0")
    if not 0.0 <= win_probability <= 1.0:
        raise ValueError("win_probability must be between 0 and 1")
    win_profit = stake * (odds - 1.0)
    loss = stake
    return (win_probability * win_profit) - ((1.0 - win_probability) * loss)


def edge(odds: float, win_probability: float) -> float:
    """Return the value edge: how much better the real chance is than the
    odds imply. Positive means the odds understate the real chance."""
    return win_probability - implied_probability(odds)


def stake_percent_of_bankroll(stake: float, bankroll: float) -> float:
    """Return the stake as a percentage of the bankroll (0 to 100)."""
    if bankroll <= 0:
        raise ValueError("bankroll must be greater than 0")
    if stake < 0:
        raise ValueError("stake must not be negative")
    return (stake / bankroll) * 100.0


def risk_score(
    stake_percent: float,
    edge_value: float,
    stake: float,
    bankroll: float,
) -> float:
    """Return a risk score from 0 (safe) to 100 (very risky).

    The score combines three parts with fixed weights:
    - stake size relative to bankroll (0 to 40)
    - negative edge, how bad the value is (0 to 35)
    - absolute stake pressure on the bankroll (0 to 25)
    """
    stake_component = min(stake_percent * 2.0, 40.0)

    if edge_value >= 0:
        edge_component = 0.0
    else:
        edge_component = min(abs(edge_value) * 350.0, 35.0)

    stake_ratio = stake / bankroll if bankroll > 0 else 0.0
    pressure_component = min(stake_ratio * 250.0, 25.0)

    score = stake_component + edge_component + pressure_component
    return round(min(max(score, 0.0), 100.0), 1)


def risk_label(score: float) -> str:
    """Turn a risk score into a simple label."""
    if score >= 60.0:
        return RISK_HIGH
    if score >= 30.0:
        return RISK_MEDIUM
    return RISK_LOW


def assess_bet(
    match_id: str,
    market: str,
    odds: float,
    stake: float,
    win_probability: float,
    bankroll: float,
) -> RiskAssessment:
    """Run the full calculation for one bet and return the assessment."""
    implied = implied_probability(odds)
    ev = expected_value(stake, odds, win_probability)
    edge_value = edge(odds, win_probability)
    stake_percent = stake_percent_of_bankroll(stake, bankroll)
    score = risk_score(stake_percent, edge_value, stake, bankroll)

    return RiskAssessment(
        match_id=match_id,
        market=market,
        odds=round(odds, 2),
        stake=round(stake, 2),
        implied_probability=round(implied, 4),
        win_probability=round(win_probability, 4),
        expected_value=round(ev, 2),
        edge=round(edge_value, 4),
        stake_percent_bankroll=round(stake_percent, 2),
        risk_score=score,
        risk_label=risk_label(score),
    )
