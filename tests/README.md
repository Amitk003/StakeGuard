# Tests folder

This folder holds the automated tests for StakeGuard.

Run all tests with:

```
pytest
```

## What is covered

- test_engine.py: the risk math (implied probability, EV, edge, stake
  percent, risk score, risk label, full assessment)
- test_flags.py: the rule-based checks (emotional language, oversized
  stake, poor value, high variance)

More tests will be added as new logic modules are built.
