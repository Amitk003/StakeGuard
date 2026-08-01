"""Tests for the AI explanation layer."""

from stakeguard.engine import assess_bet
from stakeguard.flags import collect_flags
from stakeguard.llm import (
    CONFIDENCE_HIGH,
    _fallback_explanation,
    _parse_response,
    explain_bet,
)


def make_assessment(
    odds=2.0,
    stake=50,
    win_probability=0.55,
    bankroll=1000,
    match_id="M001",
):
    return assess_bet(
        match_id=match_id,
        market="home_win",
        odds=odds,
        stake=stake,
        win_probability=win_probability,
        bankroll=bankroll,
    )


def test_explain_bet_uses_fallback_without_key(monkeypatch):
    # Force no API key so the test never makes a real API call.
    monkeypatch.setattr("stakeguard.config.api_key", lambda: "")
    assessment = make_assessment()
    flags = collect_flags("", 5.0, assessment.edge, assessment.odds)
    result = explain_bet(assessment, flags)
    assert result.used_fallback is True
    assert result.summary
    assert result.safer_alternative
    assert result.confidence in ("High", "Medium", "Low")


def test_fallback_summary_mentions_risk_label():
    assessment = make_assessment(odds=6.0, stake=300, win_probability=0.2, bankroll=1000)
    flags = collect_flags("", 30.0, assessment.edge, assessment.odds)
    result = _fallback_explanation(assessment, flags)
    assert assessment.risk_label in result.summary


def test_fallback_negative_ev_mentions_loss():
    assessment = make_assessment(odds=1.5, stake=100, win_probability=0.5, bankroll=1000)
    result = _fallback_explanation(assessment, [])
    assert "negative expected value" in result.summary


def test_fallback_high_risk_suggests_no_bet():
    assessment = make_assessment(odds=8.0, stake=500, win_probability=0.1, bankroll=1000)
    flags = collect_flags("desperate", 50.0, assessment.edge, assessment.odds)
    result = _fallback_explanation(assessment, flags)
    assert "no bet" in result.safer_alternative or "reduc" in result.safer_alternative


def test_fallback_includes_flag_reasons():
    assessment = make_assessment()
    flags = collect_flags("angry and tilted", 5.0, assessment.edge, assessment.odds)
    result = _fallback_explanation(assessment, flags)
    assert "emotional language" in result.summary


def test_parse_response_plain_json():
    data = _parse_response(
        '{"summary": "Looks risky", "safer_alternative": "Bet less", '
        '"confidence": "Medium"}'
    )
    assert data["summary"] == "Looks risky"
    assert data["safer_alternative"] == "Bet less"
    assert data["confidence"] == "Medium"


def test_parse_response_code_fence():
    data = _parse_response(
        '```json\n{"summary": "ok", "safer_alternative": "no bet", '
        '"confidence": "Low"}\n```'
    )
    assert data["summary"] == "ok"
    assert data["safer_alternative"] == "no bet"
    assert data["confidence"] == "Low"


def test_fallback_confidence_high_without_flags():
    assessment = make_assessment()
    result = _fallback_explanation(assessment, [])
    assert result.confidence == CONFIDENCE_HIGH
