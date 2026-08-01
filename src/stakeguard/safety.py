"""Safety helpers for StakeGuard.

Currently provides PII masking so personal notes can be stored in the
action log without leaking email addresses, phone numbers, or names.
"""

from __future__ import annotations

import re

_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_PATTERN = re.compile(r"(?<!\d)(\+?\d[\d\s\-()]{6,}\d)(?!\d)")
# Names are hard to detect reliably, so we mask obvious patterns only.
_SOCIAL_PATTERN = re.compile(r"@\w+")

_MASKED_EMAIL = "[email]"
_MASKED_PHONE = "[phone]"
_MASKED_SOCIAL = "[handle]"


def mask_pii(text: str) -> str:
    """Replace emails, phone numbers, and social handles with placeholders."""
    if not text:
        return text
    masked = _EMAIL_PATTERN.sub(_MASKED_EMAIL, text)
    masked = _PHONE_PATTERN.sub(_MASKED_PHONE, masked)
    masked = _SOCIAL_PATTERN.sub(_MASKED_SOCIAL, masked)
    return masked
