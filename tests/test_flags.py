"""Tests for the rule-based safety flags."""

from stakeguard.flags import (
    check_high_odds,
    check_mood_note,
    check_poor_value,
    check_stake_size,
    collect_flags,
)


def test_mood_note_clean_returns_no_flags():
    assert check_mood_note("") == []
    assert check_mood_note("Feeling good about this one") == []


def test_mood_note_detects_tilt_language():
    flags = check_mood_note("just lost three in a row and i am tilted")
    assert any(f.name == "emotional_language" for f in flags)


def test_mood_note_detects_revenge_chase():
    flags = check_mood_note("i need to chase my losses")
    assert any(f.name == "emotional_language" for f in flags)


def test_stake_size_flags_oversized_bet():
    flags = check_stake_size(25.0)
    assert any(f.name == "oversized_stake" for f in flags)


def test_stake_size_ok_for_small_bet():
    assert check_stake_size(5.0) == []


def test_poor_value_flags_negative_edge():
    flags = check_poor_value(-0.05)
    assert any(f.name == "poor_value" for f in flags)


def test_poor_value_ok_for_good_edge():
    assert check_poor_value(0.05) == []


def test_high_odds_flags_long_shot():
    flags = check_high_odds(6.0)
    assert any(f.name == "high_variance" for f in flags)


def test_high_odds_ok_for_short_odds():
    assert check_high_odds(1.8) == []


def test_collect_flags_combines_everything():
    flags = collect_flags(
        note="angry and tilted after a loss",
        stake_percent=20.0,
        edge_value=-0.1,
        odds=7.0,
    )
    names = {f.name for f in flags}
    assert "emotional_language" in names
    assert "oversized_stake" in names
    assert "poor_value" in names
    assert "high_variance" in names


def test_collect_flags_clean_bet_has_no_flags():
    flags = collect_flags(
        note="",
        stake_percent=2.0,
        edge_value=0.05,
        odds=1.8,
    )
    assert flags == []
