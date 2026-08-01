"""AI explanation layer for StakeGuard.

The risk math never depends on this module. The LLM only writes the
plain-language summary and the safer alternative. If no API key is set, or
the call fails, we fall back to clear template text so the app always works.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from openai import OpenAI

from stakeguard import config
from stakeguard.engine import RiskAssessment
from stakeguard.flags import Flag

CONFIDENCE_HIGH = "High"
CONFIDENCE_MEDIUM = "Medium"
CONFIDENCE_LOW = "Low"

SYSTEM_PROMPT = (
    "You are StakeGuard, a responsible betting risk advisor. "
    "You help a bettor decide if a proposed bet is worth the risk. "
    "You never predict winners. You only use the numbers you are given. "
    "Reply with valid JSON only, with three fields: "
    'summary (a short plain-language risk explanation), '
    'safer_alternative (one concrete safer option, or "no bet"), and '
    'confidence ("High", "Medium", or "Low"). '
    "Do not mention bookmakers by name. Do not encourage gambling."
)


@dataclass(frozen=True)
class AIExplanation:
    """The AI-generated text parts of an assessment."""

    summary: str
    safer_alternative: str
    confidence: str
    used_fallback: bool


def _build_user_prompt(
    assessment: RiskAssessment,
    flags: list[Flag],
) -> str:
    """Turn the calculated numbers into a prompt for the LLM."""
    lines = [
        f"Match: {assessment.match_id}",
        f"Market: {assessment.market}",
        f"Odds: {assessment.odds}",
        f"Stake: {assessment.stake}",
        f"Implied probability from odds: {assessment.implied_probability}",
        f"Estimated win probability: {assessment.win_probability}",
        f"Expected value: {assessment.expected_value}",
        f"Edge: {assessment.edge}",
        f"Stake as percent of bankroll: {assessment.stake_percent_bankroll}",
        f"Risk score: {assessment.risk_score}",
        f"Risk label: {assessment.risk_label}",
    ]
    if flags:
        flag_text = "; ".join(f.reason for f in flags)
        lines.append(f"Safety flags raised: {flag_text}")
    else:
        lines.append("Safety flags raised: none")
    return "\n".join(lines)


def _fallback_explanation(
    assessment: RiskAssessment,
    flags: list[Flag],
) -> AIExplanation:
    """Return a clear template explanation when no LLM is available."""
    parts = [f"This bet is rated {assessment.risk_label} risk."]
    if assessment.expected_value < 0:
        parts.append(
            "The math says the bet has negative expected value, so on "
            "average it would lose money over many similar bets."
        )
    else:
        parts.append(
            "The math says the bet has positive expected value, but "
            "positive EV is not a guarantee for a single bet."
        )
    if flags:
        parts.append(
            "Warning signs were found: "
            + ", ".join(f.reason for f in flags)
            + "."
        )
    summary = " ".join(parts)

    if assessment.risk_label == "High":
        safer = (
            "Consider not betting, or reduce the stake well below "
            f"{assessment.stake} and pick a market with better value."
        )
    else:
        safer = (
            "Consider a smaller stake or a market with shorter odds if you "
            "still want to bet."
        )
    confidence = CONFIDENCE_MEDIUM if flags else CONFIDENCE_HIGH
    return AIExplanation(
        summary=summary,
        safer_alternative=safer,
        confidence=confidence,
        used_fallback=True,
    )


def _parse_response(content: str) -> dict[str, str]:
    """Extract the three fields from an LLM JSON reply."""
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json")
    data = json.loads(text)
    summary = str(data.get("summary", "")).strip()
    safer = str(data.get("safer_alternative", "")).strip()
    confidence = str(data.get("confidence", CONFIDENCE_MEDIUM)).strip()
    return {"summary": summary, "safer_alternative": safer, "confidence": confidence}


def explain_bet(
    assessment: RiskAssessment,
    flags: list[Flag],
) -> AIExplanation:
    """Return the AI explanation, using the fallback if needed."""
    key = config.api_key()
    if not key:
        return _fallback_explanation(assessment, flags)

    client = OpenAI(
        api_key=key,
        base_url=config.base_url() or None,
    )
    try:
        response = client.chat.completions.create(
            model=config.model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(assessment, flags)},
            ],
            temperature=0.3,
            max_tokens=250,
        )
        content = response.choices[0].message.content or ""
        data = _parse_response(content)
        if not data["summary"]:
            raise ValueError("LLM returned an empty summary")
        return AIExplanation(
            summary=data["summary"],
            safer_alternative=data["safer_alternative"] or "Consider not betting.",
            confidence=data["confidence"],
            used_fallback=False,
        )
    except Exception:  # noqa: BLE001 - any failure falls back so the demo never breaks
        return _fallback_explanation(assessment, flags)
