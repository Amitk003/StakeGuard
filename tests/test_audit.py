"""Tests for the action log."""

from pathlib import Path

from stakeguard.audit import DecisionRecord, log_decision, read_log


def make_record(decision="approved", note=""):
    return DecisionRecord(
        timestamp="2026-08-01T10:00:00+00:00",
        match_id="M001",
        market="home_win",
        odds=2.1,
        stake=50,
        risk_label="Low",
        confidence="High",
        decision=decision,
        note=note,
    )


def test_log_then_read_roundtrip(tmp_path):
    path = Path(tmp_path) / "log.csv"
    log_decision(make_record(), path)
    rows = read_log(path)
    assert len(rows) == 1
    assert rows[0]["match_id"] == "M001"
    assert rows[0]["decision"] == "approved"
    assert rows[0]["odds"] == "2.1"


def test_read_log_missing_file(tmp_path):
    path = Path(tmp_path) / "missing.csv"
    assert read_log(path) == []


def test_append_multiple_records(tmp_path):
    path = Path(tmp_path) / "log.csv"
    log_decision(make_record(decision="approved"), path)
    log_decision(make_record(decision="rejected"), path)
    rows = read_log(path)
    assert len(rows) == 2
    assert rows[0]["decision"] == "approved"
    assert rows[1]["decision"] == "rejected"


def test_log_includes_note(tmp_path):
    path = Path(tmp_path) / "log.csv"
    log_decision(make_record(note="felt tilted"), path)
    rows = read_log(path)
    assert rows[0]["note"] == "felt tilted"
