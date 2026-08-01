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
  - engine.py: all the risk math (implied probability, EV, risk score)
  - flags.py: the rule-based checks (emotional words, stake size, odds)
  - llm.py: talks to the LLM for explanations (coming later)
  - safety.py: PII masking, refusal logic (coming later)
  - audit.py: the action log (coming later)
- data/matches.csv: the synthetic match dataset
- scripts/generate_matches.py: rebuilds the dataset
- tests/: the automated tests

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
