# StakeGuard

**Your personal betting risk advisor. Think first, bet smarter.**

StakeGuard is a simple web app that helps you check a bet before you place
it. You enter the match, the market, the odds, and how much you want to
stake. StakeGuard does the math, shows you the real numbers, and tells you
honestly whether the bet is worth it.

It is not a tipster. It will not predict winners. It is a second pair of
eyes that protects your money, especially on the days when you feel like
chasing a loss.

## Why StakeGuard

Most bettors decide with their emotions. They bet big after a bad day, they
chase losses, and they take odds that the math says are bad value. By the
time they look at the numbers, the money is already gone.

StakeGuard changes the order:

1. You type the bet you are thinking about.
2. StakeGuard calculates the expected value, the implied probability, and a
   clear risk score in plain Python. No guesswork, no black box.
3. It checks for emotional warning signs in what you write, like tilt or
   revenge betting after a loss.
4. It shows the evidence behind every number, so you can check it yourself.
5. It suggests a safer option: a smaller stake, a different market, or no
   bet at all.
6. It waits for you. You approve, edit, or reject. Nothing is logged until
   you decide.

## Key features

- **Real risk math.** Expected value, implied probability, stake as a
  percentage of your bankroll, and a repeatable risk score.
- **Emotional detection.** Rule-based flags catch tilt words, revenge bets,
  and oversized stakes after losses.
- **Visible evidence.** Every risk label comes with the exact numbers and
  source data behind it.
- **Human in control.** Approve, Edit, or Reject. The app never finalizes a
  decision on its own.
- **Full action log.** Every decision is timestamped and stored, so you can
  see your own betting history clearly.
- **Safe by design.** PII masking, refusal when data is missing, and
  confidence labels on every assessment.

## How it works in 10 seconds

```
You enter a bet  ->  StakeGuard calculates risk  ->  You see the evidence
  ->  Approve / Edit / Reject  ->  Decision logged
```

## Getting started

```bash
# 1. Install the packages
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Full instructions are in [docs/setup.md](docs/setup.md).

## Documentation

- [Setup guide](docs/setup.md): install and run the app
- [User guide](docs/usage.md): how to use StakeGuard
- [Architecture](docs/architecture.md): how the app is built
- [Data guide](docs/data.md): the match dataset
- [Trust and safety](docs/safety.md): the safety features

## The data

The app runs on a small synthetic match dataset that ships with the project.
Synthetic data means it was generated for this project, so there are no
licensing issues and no real personal data anywhere. See
[docs/data.md](docs/data.md) for details.

## Project layout

```
app.py                 Streamlit entry point
src/stakeguard/        The logic package
docs/                  Simple-English documentation
data/                  Synthetic match dataset
tests/                 Automated tests
```

## License

See the LICENSE file in this repository.
