# Launch checklist

Use this page before you share StakeGuard or record a demo. It makes sure
the app is ready and nothing is left behind.

## Code and repo

- [ ] All work is merged into main and pushed
- [ ] Commit messages are clear and small
- [ ] No API keys, tokens, or secrets are committed
- [ ] The .env file is not in the repository
- [ ] The memory folder is not pushed to GitHub

## App works

- [ ] `pip install -r requirements.txt` works on a clean machine
- [ ] `streamlit run app.py` starts without errors
- [ ] A good-value bet shows Low or Medium risk
- [ ] An emotional or oversized bet shows High risk with warning signs
- [ ] Approve, Edit, and Reject all work
- [ ] Decisions appear in the action log with timestamps
- [ ] An unknown match shows a refusal message, not a guess
- [ ] The app works without an API key (template explanations)

## Tests and quality

- [ ] `pytest` passes
- [ ] `ruff check .` passes

## Demo

- [ ] One success case: a sensible bet assessed and approved
- [ ] One limitation case: an emotional or bad-value bet rejected
- [ ] One refusal case: a match with not enough data
- [ ] The demo is under 10 minutes
- [ ] The demo covers: problem, user, flow, safety feature, result,
      limitation

## Docs

- [ ] README explains what the app does and how to run it
- [ ] docs/setup.md is accurate
- [ ] docs/disclosures.md is complete
- [ ] The architecture diagram renders correctly
