"""StakeGuard Streamlit entry point.

The full flow: enter a bet, see the risk assessment with evidence, then
approve, edit, or reject. No decision is logged until the user acts.

Design note: the assessment and its buttons are rendered on every script
run while an assessment exists in session state. This keeps Streamlit
button clicks working after reruns.
"""

import pandas as pd
import streamlit as st

from stakeguard import __version__, data
from stakeguard.audit import DecisionRecord, log_decision, now_iso, read_log
from stakeguard.engine import RiskAssessment, assess_bet
from stakeguard.evidence import confidence as confidence_label
from stakeguard.evidence import refuse_reason
from stakeguard.flags import collect_flags
from stakeguard.llm import explain_bet
from stakeguard.safety import mask_pii

st.set_page_config(
    page_title="StakeGuard",
    layout="wide",
)

st.title("StakeGuard")
st.caption("Your personal betting risk advisor.")

# Cached data load. The dataset is small and static.
matches = data.load_matches()

MARKETS = ["home_win", "draw", "away_win"]

RISK_BADGE_COLORS = {
    "Low": "#16a34a",
    "Medium": "#d97706",
    "High": "#dc2626",
}

BADGE_CSS = """
<style>
.badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 999px;
    color: white;
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: 0.02em;
}
</style>
"""


def risk_badge(label: str) -> str:
    """Return an HTML risk badge with the label color."""
    color = RISK_BADGE_COLORS.get(label, "#6b7280")
    return f'<span class="badge" style="background:{color}">{label} risk</span>'


def show_charts(assessment) -> None:
    """Render EV and stake comparison charts."""
    win_prob = assessment.win_probability
    expected_profit = win_prob * assessment.stake * (assessment.odds - 1.0)
    expected_loss = (1.0 - win_prob) * assessment.stake

    ev_data = pd.DataFrame(
        {
            "Amount ($)": [
                round(expected_profit, 2),
                round(-expected_loss, 2),
                round(assessment.expected_value, 2),
            ]
        },
        index=["Expected profit", "Expected loss", "Net EV"],
    )

    bankroll = st.session_state.get("current_bankroll", 1000.0)
    safe_stake = round(bankroll * 0.01, 2)
    stake_compare = pd.DataFrame(
        {
            "Stake ($)": [
                round(assessment.stake, 2),
                safe_stake,
            ]
        },
        index=["Proposed stake", "Safe stake (1% of bankroll)"],
    )

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Expected value breakdown**")
        st.bar_chart(ev_data, height=220)
    with col_chart2:
        st.markdown("**Stake comparison**")
        st.bar_chart(stake_compare, height=220)


def show_action_log() -> None:
    """Render the action log in the sidebar."""
    st.sidebar.subheader("Action log")
    rows = read_log()
    if not rows:
        st.sidebar.caption("No decisions yet.")
        return
    df = pd.DataFrame(rows)
    st.sidebar.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_order=["timestamp", "match_id", "market", "stake", "risk_label", "decision"],
    )


def compute_assessment(
    match_id: str,
    market: str,
    odds: float,
    stake: float,
    bankroll: float,
) -> RiskAssessment:
    """Build the RiskAssessment for the given inputs."""
    match = data.find_match(match_id, matches)
    if match is None:
        raise ValueError("match not found")
    win_prob = data.win_probability_for(match, market)
    return assess_bet(match_id, market, odds, stake, win_prob, bankroll)


def render_assessment(assessment, note: str) -> None:
    """Render the assessment, evidence, warning signs, and review controls."""
    flags = collect_flags(
        note=note,
        stake_percent=assessment.stake_percent_bankroll,
        edge_value=assessment.edge,
        odds=assessment.odds,
    )
    explanation = explain_bet(assessment, flags)
    match = data.find_match(assessment.match_id, matches)
    if match is None:
        st.warning(refuse_reason(match_exists=False, market_supported=True))
        return

    conf = confidence_label(
        has_match=True,
        win_probability=assessment.win_probability,
        flags_count=len(flags),
        note_provided=bool(note),
    )

    st.markdown(BADGE_CSS, unsafe_allow_html=True)
    st.subheader("Risk assessment")
    st.markdown(risk_badge(assessment.risk_label), unsafe_allow_html=True)
    st.caption(f"Confidence: {conf}")

    st.markdown("#### Risk score")
    st.progress(min(assessment.risk_score / 100.0, 1.0))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Expected value", f"${assessment.expected_value:.2f}")
    col2.metric("Implied probability", f"{assessment.implied_probability:.1%}")
    col3.metric("Risk score", f"{assessment.risk_score:.0f}/100")
    col4.metric("Stake % of bankroll", f"{assessment.stake_percent_bankroll:.1f}%")

    st.markdown("### Evidence")
    evidence = pd.DataFrame(
        [
            {
                "Match": match["home_team"] + " vs " + match["away_team"],
                "Market": assessment.market,
                "Odds": assessment.odds,
                "Implied prob": assessment.implied_probability,
                "Est. win prob": assessment.win_probability,
                "EV": assessment.expected_value,
                "Edge": assessment.edge,
                "Home form": match["home_form"],
                "Away form": match["away_form"],
            }
        ]
    )
    st.dataframe(evidence, use_container_width=True, hide_index=True)
    st.caption(f"Head to head: {match['h2h_notes']}")

    show_charts(assessment)

    if flags:
        st.markdown("### Warning signs")
        for flag in flags:
            if flag.severity == "danger":
                st.error(flag.reason)
            else:
                st.warning(flag.reason)
    else:
        st.success("No warning signs detected.")

    st.markdown("### What the numbers mean")
    st.write(explanation.summary)
    st.info(f"Safer alternative: {explanation.safer_alternative}")

    st.markdown("### Your decision")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("Approve", type="primary", key="btn_approve"):
        _record_decision("approved", assessment, conf, note)
        st.rerun()
    if col_b.button("Reject", key="btn_reject"):
        _record_decision("rejected", assessment, conf, note)
        st.rerun()
    if col_c.button("Edit bet", key="btn_edit"):
        st.session_state["editing"] = True
        st.rerun()


def _record_decision(decision: str, assessment, confidence: str, note: str) -> None:
    """Write one decision to the action log and clear the review state."""
    record = DecisionRecord(
        timestamp=now_iso(),
        match_id=assessment.match_id,
        market=assessment.market,
        odds=assessment.odds,
        stake=assessment.stake,
        risk_label=assessment.risk_label,
        confidence=confidence,
        decision=decision,
        note=mask_pii(note),
    )
    log_decision(record)
    st.session_state["last_decision"] = decision
    st.session_state["current_assessment"] = None
    st.session_state["editing"] = False


def render_edit_form() -> None:
    """Render the edit flow. Changes re-assess with the same bankroll."""
    st.subheader("Edit bet")
    st.caption("Change the stake or the market and re-assess. Nothing is final until you decide.")
    assessment = st.session_state.get("current_assessment")
    if assessment is None:
        st.session_state["editing"] = False
        return

    col1, col2 = st.columns(2)
    market = col1.selectbox(
        "Market",
        MARKETS,
        index=MARKETS.index(assessment.market),
        key="edit_market",
    )
    new_stake = col2.number_input(
        "Stake",
        min_value=0.0,
        value=float(assessment.stake),
        step=5.0,
        key="edit_stake",
    )

    bankroll = st.session_state.get("current_bankroll", 1000.0)

    if st.button("Re-assess", key="btn_reassess"):
        match = data.find_match(assessment.match_id, matches)
        if match is None:
            st.warning("Not enough evidence: this match is not in the dataset.")
            return
        # Keep the user's entered odds when the market is unchanged.
        if market == assessment.market:
            odds = st.session_state.get("current_odds", assessment.odds)
        else:
            odds = data.odds_for(match, market)
        updated = compute_assessment(
            assessment.match_id,
            market,
            odds,
            new_stake,
            bankroll,
        )
        st.session_state["current_assessment"] = updated
        st.session_state["current_odds"] = odds
        st.session_state["editing"] = False
        st.rerun()

    if st.button("Cancel edit", key="btn_cancel_edit"):
        st.session_state["editing"] = False
        st.rerun()


# Sidebar
with st.sidebar:
    st.subheader("StakeGuard")
    st.caption(f"Version {__version__}")
    st.markdown("---")
    show_action_log()
    st.markdown("---")
    st.caption("Think first. Bet smarter.")

# Edit mode takes over the main area.
if st.session_state.get("editing"):
    render_edit_form()
    st.stop()

# Enter a bet form.
st.subheader("Enter a bet")
with st.form("bet_form"):
    match_options = matches["match_id"].tolist()
    match_id = st.selectbox("Match", match_options)
    market = st.selectbox("Market", MARKETS)

    match = data.find_match(match_id, matches)
    default_odds = data.odds_for(match, market) if match is not None else 2.0

    col1, col2 = st.columns(2)
    odds = col1.number_input("Odds", min_value=1.01, value=float(default_odds), step=0.05)
    stake = col2.number_input("Stake", min_value=0.0, value=50.0, step=5.0)

    col3, col4 = st.columns(2)
    bankroll = col3.number_input("Bankroll", min_value=1.0, value=1000.0, step=50.0)
    note = col4.text_area("Mood note (optional)", placeholder="How are you feeling?")

    submitted = st.form_submit_button("Assess bet")

if submitted:
    try:
        assessment = compute_assessment(match_id, market, odds, stake, bankroll)
    except ValueError as exc:
        st.error(f"Cannot assess this bet: {exc}")
        st.stop()
    st.session_state["current_assessment"] = assessment
    st.session_state["current_bankroll"] = bankroll
    st.session_state["current_odds"] = odds
    st.session_state["current_note"] = note

# Render the assessment and review controls on every run while one exists.
assessment = st.session_state.get("current_assessment")
if assessment is not None:
    note = st.session_state.get("current_note", "")
    render_assessment(assessment, note)

if st.session_state.get("last_decision"):
    decision = st.session_state.pop("last_decision")
    if decision == "approved":
        st.success("Decision approved and logged.")
    else:
        st.info("Bet rejected and logged.")
