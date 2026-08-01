"""Tests for the PII masking helpers."""

from stakeguard.safety import mask_pii


def test_masks_email():
    assert mask_pii("contact me at jane@example.com") == "contact me at [email]"


def test_masks_phone():
    assert mask_pii("call me at 555-123-4567") == "call me at [phone]"


def test_masks_social_handle():
    assert mask_pii("check @jane_writes") == "check [handle]"


def test_masks_multiple_pii():
    result = mask_pii("jane@example.com and 555-123-4567 and @jane")
    assert "[email]" in result
    assert "[phone]" in result
    assert "[handle]" in result


def test_plain_text_unchanged():
    assert mask_pii("felt tilted after losing") == "felt tilted after losing"


def test_empty_text_returns_empty():
    assert mask_pii("") == ""
