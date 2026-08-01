"""Match dataset loader for StakeGuard.

Loads the synthetic match CSV and provides helpers to look up a match and
its odds and win probabilities by market.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "matches.csv"

# Markets the app understands, mapped to dataset columns.
MARKET_ODDS_COLUMN = {
    "home_win": "home_odds",
    "draw": "draw_odds",
    "away_win": "away_odds",
}
MARKET_PROB_COLUMN = {
    "home_win": "home_win_prob",
    "draw": "draw_prob",
    "away_win": "away_win_prob",
}


def load_matches() -> pd.DataFrame:
    """Load the full match dataset as a DataFrame."""
    return pd.read_csv(DATA_PATH)


def find_match(match_id: str, df: pd.DataFrame) -> pd.Series | None:
    """Return the row for a match id, or None if it does not exist."""
    matches = df[df["match_id"] == match_id]
    if matches.empty:
        return None
    return matches.iloc[0]


def odds_for(match: pd.Series, market: str) -> float:
    """Return the dataset odds for a market on a match."""
    return float(match[MARKET_ODDS_COLUMN[market]])


def win_probability_for(match: pd.Series, market: str) -> float:
    """Return the estimated win probability for a market on a match."""
    return float(match[MARKET_PROB_COLUMN[market]])
