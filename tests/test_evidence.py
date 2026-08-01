"""Tests for the evidence and confidence helpers."""

from stakeguard.evidence import confidence, refuse_reason


def test_confidence_low_without_match():
    assert confidence(has_match=False, win_probability=None, flags_count=0, note_provided=False) == "Low"


def test_confidence_low_without_probability():
    assert confidence(has_match=True, win_probability=None, flags_count=0, note_provided=False) == "Low"


def test_confidence_high_for_clean_input():
    assert confidence(has_match=True, win_probability=0.5, flags_count=0, note_provided=False) == "High"


def test_confidence_medium_with_flags():
    assert confidence(has_match=True, win_probability=0.5, flags_count=1, note_provided=False) == "Medium"


def test_confidence_medium_with_note():
    assert confidence(has_match=True, win_probability=0.5, flags_count=0, note_provided=True) == "Medium"


def test_confidence_low_with_many_flags():
    assert confidence(has_match=True, win_probability=0.5, flags_count=2, note_provided=False) == "Low"


def test_refuse_reason_missing_match():
    assert refuse_reason(match_exists=False, market_supported=True) is not None


def test_refuse_reason_unsupported_market():
    assert refuse_reason(match_exists=True, market_supported=False) is not None


def test_refuse_reason_none_when_ok():
    assert refuse_reason(match_exists=True, market_supported=True) is None
