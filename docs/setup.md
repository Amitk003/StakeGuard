# Setup guide

This page explains how to install and run StakeGuard on your computer.

## What you need

- Python 3.11 or newer
- Git (only if you clone the repo)
- An internet connection for the first install

## Step 1: Get the code

If you have the repo link, clone it:

```
git clone <repo-url>
cd stakeguard
```

If you already have the files, skip this step.

## Step 2: Create a virtual environment

A virtual environment keeps the packages for this project separate from the
rest of your computer. Open a terminal in the project folder and run:

On Windows:

```
python -m venv .venv
.venv\Scripts\activate
```

On Mac or Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install the packages

```
pip install -r requirements.txt
```

This installs Streamlit (the web app), Pandas (data work), and the other
packages the app needs.

## Step 4: Add your API key (optional)

The app works without an API key. All risk math runs in plain Python. The
LLM layer writes nicer explanations, but it is not required: without a key
(or if the API is down), StakeGuard uses built-in template text and still
gives a full assessment.

1. Copy the file `.env.example` and name the copy `.env`.
2. Open `.env` and add your key.

Never commit the `.env` file. It is already in `.gitignore`.

## Step 5: Run the app

```
streamlit run app.py
```

Your browser should open the app. If it does not open, look at the terminal
output. The app usually runs at http://localhost:8501.

## Step 6: Run the tests

```
pytest
```

## Common problems

- "streamlit is not recognized": the virtual environment is not active, or
  you did not install the packages. Do Step 2 and Step 3 again.
- The app opens but shows an error: check the terminal for the full error
  message and make sure all packages are installed.
