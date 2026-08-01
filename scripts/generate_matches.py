"""Generate the synthetic match dataset.

Run from the project root:

    python scripts/generate_matches.py

The output is written to data/matches.csv. The data is synthetic: it was
invented for this project so the app can demo with safe, licensed-free data.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

random.seed(42)

TEAMS = [
    ("Northside FC", "Southpark United"),
    ("Riverside City", "Eastfield Town"),
    ("Kingston Rovers", "Harborview Athletic"),
    ("Westbrook Wanderers", "Cedar Falls"),
    ("Maple Grove", "Ironbridge FC"),
    ("Foxhill Eleven", "Bayside Select"),
    ("Grandview", "Stonewall County"),
    ("Lakeside Pride", "Oakhurst FC"),
    ("Silverton", "Blue Ridge United"),
    ("Pinecrest", "Valley Athletic"),
    ("Northgate Nomads", "Riverbend FC"),
    ("Sunrise City", "Fairview SC"),
    ("Cliffside", "Meadowbrook United"),
    ("Highland Park", "Doverfield"),
]

MARKETS = ["home_win", "away_win", "draw"]


def main() -> None:
    """Generate the matches CSV file."""
    rows: list[dict[str, object]] = []
    for i, (home, away) in enumerate(TEAMS, start=1):
        # Reasonable win chances. Home teams are usually slightly better.
        home_win = random.uniform(0.32, 0.58)
        draw_prob = random.uniform(0.18, 0.30)
        away_win = max(0.05, 1.0 - home_win - draw_prob)

        # Odds are built from the probabilities plus a small bookmaker margin.
        margin = 1.06
        home_odds = round((margin / home_win) + random.uniform(0.0, 0.05), 2)
        away_odds = round((margin / away_win) + random.uniform(0.0, 0.05), 2)
        draw_odds = round((margin / draw_prob) + random.uniform(0.0, 0.05), 2)

        home_form = f"{random.randint(1, 5)}/{5}"
        away_form = f"{random.randint(1, 5)}/{5}"
        h2h = random.choice(
            [
                "home won the last 2 meetings",
                "teams split the last 2 meetings",
                "away won the last meeting",
                "first meeting between the sides",
                "home unbeaten in the last 3",
                "high scoring recent meetings",
            ]
        )

        rows.append(
            {
                "match_id": f"M{i:03d}",
                "home_team": home,
                "away_team": away,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
                "home_win_prob": round(home_win, 4),
                "draw_prob": round(draw_prob, 4),
                "away_win_prob": round(away_win, 4),
                "home_form": home_form,
                "away_form": away_form,
                "h2h_notes": h2h,
            }
        )

    out_path = Path("data") / "matches.csv"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} matches to {out_path}")


if __name__ == "__main__":
    main()
