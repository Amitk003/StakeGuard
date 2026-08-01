# Architecture diagram

This page shows how StakeGuard works from input to output. The diagram uses
Mermaid, which renders automatically on GitHub and in many Markdown editors.

## Flow diagram

```mermaid
flowchart LR
    A[User enters a bet] --> B[Input layer]
    B --> C[Calculation engine]
    C --> D[Rule checks]
    D --> E[AI explanation]
    E --> F[Evidence display]
    F --> G{Human decision}
    G -->|Approve| H[Action log]
    G -->|Reject| H[Action log]
    G -->|Edit| B
    H --> I[Timestamped record]
```

## What each box does

- Input layer: match, market, odds, stake, bankroll, optional mood note.
- Calculation engine: implied probability, expected value, risk score.
- Rule checks: emotional language, oversized stake, poor value, high
  variance.
- AI explanation: plain-language summary and a safer alternative. Uses
  template text when no API key is set.
- Evidence display: the exact numbers, source table, and warning signs.
- Human decision: Approve, Reject, or Edit. Nothing is logged without it.
- Action log: every decision with a timestamp.

## Component diagram

```mermaid
flowchart TB
    subgraph UI[Streamlit app]
        app[app.py]
    end
    subgraph Logic[stakeguard package]
        engine[engine.py - risk math]
        flags[flags.py - rule checks]
        llm[llm.py - explanations]
        evidence[evidence.py - confidence]
        safety[safety.py - PII masking]
        audit[audit.py - action log]
        data_module[data.py - dataset loader]
    end
    subgraph Files[Files]
        csv[data/matches.csv]
        log[action_log.csv]
    end
    app --> data_module
    app --> engine
    app --> flags
    app --> llm
    app --> evidence
    app --> safety
    app --> audit
    data_module --> csv
    audit --> log
```
