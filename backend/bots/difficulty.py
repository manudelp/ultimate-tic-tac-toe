"""Turn a bot's measured rating into the level players see.

Ratings come from `python -m arena rate`, which pins Randy (random play) at 500.
Each level is 400 points wide: at that gap the stronger side scores about 91%,
so every step up is a clearly harder opponent, not a coin flip.
"""
import json
import pathlib

RATINGS_FILE = pathlib.Path(__file__).resolve().parents[1] / "data" / "bot_ratings.json"
BASE = 500
STEP = 400
LABELS = ["Beginner", "Easy", "Intermediate", "Hard", "Expert"]


def load_ratings(path=RATINGS_FILE):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return {int(k): v["rating"] for k, v in data.get("bots", {}).items()}


def level_for(rating):
    """1..5. Level n is centered on BASE + (n - 1) * STEP, so Randy sits mid level 1."""
    if rating is None:
        return None
    return max(1, min(len(LABELS), 1 + int((rating - BASE + STEP / 2) // STEP)))


def describe(rating):
    level = level_for(rating)
    return {
        "rating": rating,
        "level": level,
        "label": LABELS[level - 1] if level else "Unrated",
        "maxLevel": len(LABELS),
    }
