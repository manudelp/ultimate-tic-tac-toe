"""Time the alpha-beta bots on fixed positions and pin the moves they choose.

    uv run python dev/bench/bench_bots.py record   # save reference moves
    uv run python dev/bench/bench_bots.py check    # compare against them

Positions come from seeded random play, so every run sees the same boards.
"""
import json
import pathlib
import random
import sys
import time

BACKEND = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from core.engine import GameEngine  # noqa: E402

REFERENCE = pathlib.Path(__file__).with_name("reference_moves.json")
PLIES = [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 34, 38, 42]
SEEDS = [11, 23]


def positions():
    out = []
    for seed in SEEDS:
        for ply in PLIES:
            rng = random.Random(seed * 1000 + ply)
            for _ in range(50):
                engine = GameEngine(time_per_player=None)
                for _ in range(ply):
                    if engine.status != "ongoing":
                        break
                    legal = engine.get_legal_moves()
                    engine.make_move(engine.active_player, *rng.choice(legal))
                if engine.status == "ongoing" and len(engine.moves) == ply:
                    break
            else:
                continue
            out.append({
                "id": f"s{seed}-p{ply}",
                "board": engine.board.tolist(),
                "mover": int(engine.active_player),
                "forced": list(engine.forced_board) if engine.forced_board else None,
            })
    return out


def load_bots(names):
    from bots.jardishow import JardiShowAgent
    from bots.jardito import JardineritoAgent

    table = {"jardinerito": JardineritoAgent, "jardinero": JardiShowAgent}
    bots = {}
    for name in names:
        bot = table[name]()
        bot.load()
        bots[name] = bot
    return bots


def run(bot, position):
    import numpy as np

    from core.position import Position

    bot.reset()
    board = np.array(position["board"], dtype=int)
    forced = tuple(position["forced"]) if position["forced"] else None
    state = Position.from_board(board, position["mover"], forced)
    start = time.perf_counter()
    move = bot.choose(state)
    elapsed = time.perf_counter() - start
    return [int(x) for x in move], elapsed


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else ["jardinerito", "jardinero"]
    reference = json.loads(REFERENCE.read_text()) if REFERENCE.exists() else {}
    bots = load_bots(names)
    pos = positions()
    mismatches = 0
    for name, bot in bots.items():
        total = 0.0
        worst = 0.0
        rows = reference.setdefault(name, {})
        for position in pos:
            move, elapsed = run(bot, position)
            total += elapsed
            worst = max(worst, elapsed)
            key = position["id"]
            if mode == "record":
                rows[key] = {"move": move, "seconds": round(elapsed, 4)}
            else:
                expected = rows.get(key)
                if expected is None:
                    print(f"{name} {key}: no reference")
                    continue
                speedup = expected["seconds"] / elapsed if elapsed > 0 else float("inf")
                same = expected["move"] == move
                mismatches += 0 if same else 1
                flag = "" if same else f"  MISMATCH, expected {expected['move']}"
                print(
                    f"{name:12} {key:8} {elapsed:7.3f}s  was {expected['seconds']:7.3f}s  "
                    f"x{speedup:6.1f}{flag}"
                )
        print(f"{name}: {len(pos)} positions, total {total:.2f}s, worst {worst:.2f}s")
    if mode == "record":
        REFERENCE.write_text(json.dumps(reference, indent=1))
        print(f"wrote {REFERENCE}")
    elif mismatches:
        raise SystemExit(f"{mismatches} moves differ from the reference")
    else:
        print("all moves match the reference")


if __name__ == "__main__":
    main()
