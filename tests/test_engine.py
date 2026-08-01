"""Tests for the StakeGuard calculation engine."""

import pytest

from stakeguard.engine import (
    assess_bet,
    edge,
    expected_value,
    implied_probability,
    risk_label,
    risk_score,
    stake_percent_of_bankroll,
)


def test_implied_probability_evens():
    assert implied_probability(2.0) == 0.5


def test_implied_probability_odds_three():
    assert implied_probability(3.0) == pytest.approx(0.3333, abs=0.001)


def test_implied_probability_rejects_odds_below_one():
    with pytest.raises(ValueError):
        implied_probability(1.0)


def test_expected_value_fair_bet_is_zero():
    # 2.0 odds with a 50% chance means zero EV.
    assert expected_value(100, 2.0, 0.5) == pytest.approx(0.0)


def test_expected_value_good_bet_is_positive():
    # 3.0 odds with a 40% chance: EV = 0.4*200 - 0.6*100 = 20
    assert expected_value(100, 3.0, 0.4) == pytest.approx(20.0)


def test_expected_value_bad_bet_is_negative():
    # 1.5 odds with a 50% chance: EV = 0.5*50 - 0.5*100 = -25
    assert expected_value(100, 1.5, 0.5) == pytest.approx(-25.0)


def test_expected_value_rejects_bad_inputs():
    with pytest.raises(ValueError):
        expected_value(-1, 2.0, 0.5)
    with pytest.raises(ValueError):
        expected_value(100, 1.0, 0.5)
    with pytest.raises(ValueError):
        expected_value(100, 2.0, 1.5)


def test_edge_positive_when_odds_understate_chance():
    # Real chance 60%, odds imply 50% -> positive edge.
    assert edge(2.0, 0.6) == pytest.approx(0.1)


def test_stake_percent_of_bankroll():
    assert stake_percent_of_bankroll(50, 1000) == pytest.approx(5.0)


def test_stake_percent_rejects_zero_bankroll():
    with pytest.raises(ValueError):
        stake_percent_of_bankroll(50, 0)


def test_risk_score_bounds():
    assert 0.0 <= risk_score(0, 0, 0, 1000) <= 100.0
    assert 0.0 <= risk_score(50, -0.5, 500, 1000) <= 100.0


def test_risk_score_rises_with_bigger_stake():
    low = risk_score(2.0, 0.0, 20, 1000)
    high = risk_score(20.0, 0.0, 200, 1000)
    assert high > low


def test_risk_label_thresholds():
    assert risk_label(10.0) == "Low"
    assert risk_label(40.0) == "Medium"
    assert risk_label(70.0) == "High"


def test_assess_bet_full_calculation():
    result = assess_bet(
        match_id="M001",
        market="home_win",
        odds=2.0,
        stake=50,
        win_probability=0.55,
        bankroll=1000,
    )
    assert result.risk_label in ("Low", "Medium", "High")
    assert result.implied_probability == pytest.approx(0.5)
    # EV = 0.55 * 50 * 1 - 0.45 * 50 = 27.5 - 22.5 = 5.0
    assert result.expected_value == pytest.approx(5.0)
    assert result.stake_percent_bankroll == pytest.approx(5.0)
