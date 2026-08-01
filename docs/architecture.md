# How the app is built

This page explains the parts of StakeGuard and how data moves through it.

## The flow

A user enters a proposed bet. The app does the following steps in order:

1. Read the input (match, market, odds, stake, optional mood note).
2. Load the match data (synthetic dataset of matches with odds and stats).
3. Calculate the numbers with plain Python code:
   - Implied probability from the odds
   - Expected value (EV) of the bet
   - Risk score based on stake size, odds value, and variance
   - Stake as a percentage of bankroll
4. Check rule-based flags:
   - Emotional keywords in the mood note (tilt, revenge, chase, etc.)
   - High stake compared to bankroll
   - Poor value odds
5. Ask the LLM to write a plain-language risk explanation and a safer
   alternative (bet smaller, different market, or no bet).
6. Show the evidence: the exact numbers and the source table rows.
7. Wait for the human. The user must Approve, Edit, or Reject.
8. Write the decision to the action log with a timestamp.

## The code layout

- app.py: the Streamlit entry point. This is the web page.
- src/stakeguard/: the logic package.
  - config.py: reads settings from .env
  - engine.py: all the risk math (probability, EV, risk score)
  - flags.py: the rule-based checks (emotional words, stake size)
  - llm.py: talks to the LLM for explanations
  - safety.py: PII masking, refusal logic
  - audit.py: the action log
- data/: the synthetic match dataset (CSV)
- tests/: the automated tests

## Design rules

- The math never depends on the LLM. If the LLM fails, the numbers still
  work and the app shows a fallback explanation.
- The human gate is real. No decision is logged unless the user clicks a
  button.
- Every module has one job. Keep it small and easy to read.
