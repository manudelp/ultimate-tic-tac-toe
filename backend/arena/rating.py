"""Rate the live bots against each other and write backend/data/bot_ratings.json.

Every pair plays the same seeded random openings, each one twice with colors
swapped, so neither side gets the better seat. Results feed a Bradley-Terry fit
on the Elo scale, with Randy pinned at RANDY_RATING: random play is the one
opponent that never changes, so the numbers stay comparable across runs.
"""
import contextlib
import itertools
import json
import math
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

from arena.match import play_game
from arena.paths import REPO_ROOT
from core.engine import GameEngine
from core.position import Position

RATINGS_FILE = REPO_ROOT / "backend" / "data" / "bot_ratings.json"
RANDY_ID = 0
RANDY_RATING = 500
# One imaginary draw per pair keeps a clean sweep from pushing a rating to infinity.
PRIOR_DRAWS = 1.0


def random_opening(plies, seed):
    """Seeded random legal plies from the empty board, replayable as a move list."""
    rng = random.Random(seed)
    for _ in range(100):
        engine = GameEngine(time_per_player=None)
        moves = []
        while len(moves) < plies and engine.status == "ongoing":
            sub, cell = rng.choice(sorted(Position.from_engine(engine).legal_moves()))
            move = (sub // 3, sub % 3, cell // 3, cell % 3)
            engine.make_move(engine.active_player, *move)
            moves.append(move)
        if engine.status == "ongoing":
            return moves
    raise RuntimeError("could not find an unfinished opening")


def _engine_from_moves(moves):
    engine = GameEngine(time_per_player=None)
    for move in moves:
        engine.make_move(engine.active_player, *move)
    return engine


def _play_pair(task):
    """Play one pair over every opening, both colors. Runs in a worker process."""
    from arena.players import make_player

    id_a, id_b, openings = task
    score_a = 0.0
    games = 0
    # The bots narrate every move; keep the worker quiet.
    with open(os.devnull, "w") as quiet, contextlib.redirect_stdout(quiet):
        a = make_player(str(id_a))
        b = make_player(str(id_b))
        for moves in openings:
            for a_is_x in (True, False):
                x, o = (a, b) if a_is_x else (b, a)
                winner = play_game(x, o, engine=_engine_from_moves(moves))
                if winner == 0:
                    score_a += 0.5
                elif (winner == 1) == a_is_x:
                    score_a += 1.0
                games += 1
    return id_a, id_b, score_a, games


def fit_ratings(results, ids):
    """Bradley-Terry by minorization-maximization (Hunter 2004), on the Elo scale.

    `results` maps (a, b) to (score for a, games). Draws count half to each side.
    """
    score = {i: 0.0 for i in ids}
    games = {}
    for (a, b), (s, n) in results.items():
        n_total = n + PRIOR_DRAWS
        score[a] += s + PRIOR_DRAWS / 2
        score[b] += (n - s) + PRIOR_DRAWS / 2
        games[(a, b)] = games[(b, a)] = n_total

    strength = {i: 1.0 for i in ids}
    for _ in range(10_000):
        updated = {}
        for i in ids:
            denom = sum(
                games[(i, j)] / (strength[i] + strength[j])
                for j in ids
                if (i, j) in games
            )
            updated[i] = score[i] / denom if denom else strength[i]
        mean_log = sum(math.log(v) for v in updated.values()) / len(updated)
        updated = {i: v / math.exp(mean_log) for i, v in updated.items()}
        delta = max(abs(math.log(updated[i] / strength[i])) for i in ids)
        strength = updated
        if delta < 1e-10:
            break

    elo = {i: 400 * math.log10(strength[i]) for i in ids}
    shift = RANDY_RATING - elo[RANDY_ID] if RANDY_ID in elo else RANDY_RATING - min(elo.values())
    return {i: elo[i] + shift for i in ids}


def rate(openings=12, plies=2, seed=0, workers=4):
    from bots import AGENTS

    ids = sorted(AGENTS)
    opening_moves = [random_opening(plies, seed * 1000 + k) for k in range(openings)]
    tasks = [(a, b, opening_moves) for a, b in itertools.combinations(ids, 2)]

    started = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for id_a, id_b, score_a, games in pool.map(_play_pair, tasks):
            results[(id_a, id_b)] = (score_a, games)
            name_a, name_b = AGENTS[id_a].name, AGENTS[id_b].name
            print(f"{name_a} {score_a:g} - {games - score_a:g} {name_b}  ({games} games)")

    ratings = fit_ratings(results, ids)
    report = {
        "generated": date.today().isoformat(),
        "method": "round robin, Bradley-Terry fit on the Elo scale, Randy pinned",
        "randyRating": RANDY_RATING,
        "openings": openings,
        "openingPlies": plies,
        "seed": seed,
        "bots": {
            str(i): {"name": AGENTS[i].name, "rating": round(ratings[i])}
            for i in ids
        },
        "pairs": [
            {"a": a, "b": b, "scoreA": s, "games": n}
            for (a, b), (s, n) in sorted(results.items())
        ],
    }
    RATINGS_FILE.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {RATINGS_FILE} in {time.time() - started:.0f}s")
    for i in sorted(ids, key=lambda k: ratings[k]):
        print(f"  {AGENTS[i].name:12} {ratings[i]:7.0f}")
    return ratings
