# Disclosures

This page lists everything StakeGuard depends on. It is kept honest and
complete so anyone can see exactly what the project uses.

## Dataset

- The app ships with a synthetic match dataset in `data/matches.csv`.
- The data was generated for this project by `scripts/generate_matches.py`
  with a fixed random seed. It is not real betting data.
- No real personal data, no private data, and no licensed external data is
  used anywhere in the project.
- The dataset is regenerated the same way every time, so it is reproducible.

## Software dependencies

All dependencies are listed in `requirements.txt`:

- streamlit: the web interface
- pandas: data work and evidence tables
- python-dotenv: reads settings from a local .env file
- openai: the optional AI explanation client
- pytest: the test runner
- ruff: the linter

No other third-party services are required to run the app.

## AI service (optional)

- The app can use any OpenAI-compatible chat API for plain-language
  explanations. This is optional.
- Without an API key, the app uses built-in template text. All risk math
  works without any API.
- API keys are read from a local `.env` file, which is gitignored and never
  committed.

## What was not used

- No live betting APIs
- No real match or odds feeds
- No user tracking or analytics services
- No paid services of any kind
