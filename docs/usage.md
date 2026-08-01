# User guide

This page explains how to use StakeGuard as a bettor.

## Start the app

Follow the setup guide, then run:

```
streamlit run app.py
```

## Enter a bet

Fill in the form:

- Match: pick a match from the list
- Market: pick a market (for example home win, away win, draw)
- Odds: the odds you were offered (for example 2.10)
- Stake: how much you plan to bet
- Bankroll (optional): your total betting budget
- Mood note (optional): write how you feel, for example "lost 3 in a row"

The more honest the mood note, the better the advice.

## Read the assessment

The app shows:

- A risk label: Low, Medium, or High
- The expected value of the bet
- The implied probability
- The risk score and how it was calculated
- The evidence: the source table and the numbers used
- A plain-language explanation
- A safer alternative, when one exists

## Approve, Edit, or Reject

- Approve: you accept the bet as proposed. It is logged as approved.
- Edit: change the stake or market. The app recalculates the whole
  assessment with the new values.
- Reject: you decline the bet. It is logged as rejected.

Nothing is saved until you click one of these buttons.

## Check the action log

The sidebar shows the action log: every decision with its timestamp, risk
label, and your choice. This is your record of how you bet.
