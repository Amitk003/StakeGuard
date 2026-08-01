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
  - data.py: loads the match dataset and looks up odds and probabilities
  - engine.py: all the risk math (implied probability, EV, risk score)
  - flags.py: the rule-based checks (emotional words, stake size, odds)
  - llm.py: writes the plain-language explanation and safer alternative
  - safety.py: PII masking for notes before they are logged
  - audit.py: the timestamped action log (CSV)
- data/matches.csv: the synthetic match dataset
- scripts/generate_matches.py: rebuilds the dataset
- tests/: the automated tests

## The human gate (app.py)

1. The user enters the match, market, odds, stake, bankroll, and an optional
   mood note.
2. The app calculates the assessment and shows the evidence table and any
   warning signs.
3. The user must click Approve, Reject, or Edit.
4. Edit lets the user change the stake or market and re-assess.
5. Only after a click is the decision written to the action log with a
   timestamp.

Nothing is logged automatically. The buttons are the only way to record a
decision.

## The action log (audit.py)

Each row in action_log.csv holds: timestamp, match, market, odds, stake,
risk label, confidence, decision (approved, rejected, edited), and a masked
note. The file is created at runtime and is gitignored.

## The AI layer (llm.py)

The LLM only writes text. It never does math. It receives the calculated
numbers and the raised flags, and returns three things as JSON:

- summary: a plain-language risk explanation
- safer_alternative: one concrete safer option
- confidence: High, Medium, or Low

If no API key is set, or the API call fails, the app falls back to clear
template text built from the same numbers. The demo always works.

## The risk math (engine.py)

- implied probability = 1 / odds
- expected value (EV) = win chance x profit - loss chance x stake
- edge = win chance - implied probability
- stake % of bankroll = stake / bankroll x 100
- risk score (0 to 100) = stake size part (0-40) + bad edge part (0-35)
  + stake pressure part (0-25)
- risk label: under 30 is Low, under 60 is Medium, else High

## The rule checks (flags.py)

Every flag has a name and a reason so the evidence layer can show it:

- emotional_language: tilt words in the mood note (chase, revenge, etc.)
- oversized_stake: stake above 10% of the bankroll
- poor_value: clearly negative edge (below -2%)
- high_variance: long shot odds of 5.0 or higher


## Design rules

- The math never depends on the LLM. If the LLM fails, the numbers still
  work and the app shows a fallback explanation.
- The human gate is real. No decision is logged unless the user clicks a
  button.
- Every module has one job. Keep it small and easy to read.
