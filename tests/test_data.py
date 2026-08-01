"""Tests for the match dataset loader."""

from stakeguard import data


def test_load_matches_has_rows():
    df = data.load_matches()
    assert len(df) >= 10
    assert "match_id" in df.columns


def test_find_match_exists():
    df = data.load_matches()
    match = data.find_match("M001", df)
    assert match is not None
    assert match["home_team"]


def test_find_match_missing_returns_none():
    df = data.load_matches()
    assert data.find_match("M999", df) is None


def test_odds_for_home_win():
    df = data.load_matches()
    match = data.find_match("M001", df)
    odds = data.odds_for(match, "home_win")
    assert odds > 1.0


def test_win_probability_in_range():
    df = data.load_matches()
    match = data.find_match("M001", df)
    prob = data.win_probability_for(match, "away_win")
    assert 0.0 < prob < 1.0


def test_market_columns_are_consistent():
    df = data.load_matches()
    for market in ("home_win", "draw", "away_win"):
        assert data.MARKET_ODDS_COLUMN[market] in df.columns
        assert data.MARKET_PROB_COLUMN[market] in df.columns
