"""Alpha-beta search shared by Jardinerito and Jardinero.

Positions are the base-3 sub-board indexes of core.rules, so win checks, "is
this board over" and empty cells are the shared rule tables. What this module
adds is the heuristic: a weighted per-sub-board evaluation read from
data/hash_evaluated_boards.txt. The search visits moves in the same order and
breaks ties the same way as the original NumPy version, so it returns the same
moves.
"""
import ast
import os
import time

import numpy as np

from bots.base import BaseAgent
from core import rules
from core.rules import EMPTIES, OVER, RESULT_DIGIT, SIZE, WINNER, board_indexes, cells_of

_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_P3 = rules.P3

_tables = None


def _load_tables():
    global _tables
    if _tables is not None:
        return _tables

    evals = {}
    with open(os.path.join(_DATA, "hash_evaluated_boards.txt")) as handle:
        for line in handle:
            key, info = line.strip().split(":")
            evals[bytes.fromhex(key)] = float(ast.literal_eval(info)[0])

    weighted = [[0.0] * SIZE for _ in range(9)]
    for index in range(SIZE):
        cells = cells_of(index)
        value = evals[np.array(cells, dtype=int).reshape(3, 3).tobytes()]
        for sub in range(9):
            r, c = divmod(sub, 3)
            if (r + c) % 2 == 1:
                weighted[sub][index] = value
            elif sub == 4:
                weighted[sub][index] = 1.5 * value
            else:
                weighted[sub][index] = 1.25 * value

    # Playable boards were a Python set of (row, col) built in row-major order;
    # keep its iteration order so ties resolve to the same move.
    order = []
    for mask in range(512):
        playable = set()
        for sub in range(9):
            if mask >> sub & 1:
                playable.add(divmod(sub, 3))
        order.append(tuple(r * 3 + c for r, c in playable))

    _tables = {
        "over": OVER,
        "won": WINNER,
        "empties": EMPTIES,
        "weighted": weighted,
        "result_digit": RESULT_DIGIT,
        "order": order,
    }
    return _tables


def encode(board):
    """3x3x3x3 board with +1 for the side to move -> list of 9 sub-board indexes."""
    return board_indexes(board)


def search(board, board_to_play, depth):
    """Return (evaluation, [row, col, local_row, local_col]) for the side playing +1."""
    t = _load_tables()
    over = t["over"]
    won = t["won"]
    empties = t["empties"]
    w0, w1, w2, w3, w4, w5, w6, w7, w8 = t["weighted"]
    result_digit = t["result_digit"]
    order = t["order"]
    p3 = _P3

    subs = encode(board)
    results = 0
    mask = 0
    for sub in range(9):
        results += result_digit[sub][subs[sub]]
        if not over[subs[sub]]:
            mask |= 1 << sub

    def ab(btp, depth, alpha, beta, maximizing, results, mask):
        winner = won[results]
        if winner:
            if winner == 1:
                return 100_000, None
            return -100_000 - depth, None
        if depth == 0:
            balance = 0
            balance += w0[subs[0]]
            balance += w1[subs[1]]
            balance += w2[subs[2]]
            balance += w3[subs[3]]
            balance += w4[subs[4]]
            balance += w5[subs[5]]
            balance += w6[subs[6]]
            balance += w7[subs[7]]
            balance += w8[subs[8]]
            return round(balance, 4), None
        if mask == 0:
            return 0, None

        if btp >= 0:
            cells = empties[subs[btp]]
            if not cells:
                raise ValueError(f"no empty cells in forced board {divmod(btp, 3)}")
            moves = [(btp, cell) for cell in cells]
        else:
            moves = [(sub, cell) for sub in order[mask] for cell in empties[subs[sub]]]
            if not moves:
                raise ValueError("no legal moves on an open board")

        best_move = None
        digit = 1 if maximizing else 2
        if maximizing:
            best = float("-inf")
        else:
            best = float("inf")
        for sub, cell in moves:
            old = subs[sub]
            new = old + digit * p3[cell]
            subs[sub] = new
            digits = result_digit[sub]
            child_results = results - digits[old] + digits[new]
            child_mask = mask & ~(1 << sub) if over[new] else mask
            target = -1 if over[subs[cell]] else cell
            value, _ = ab(target, depth - 1, alpha, beta, not maximizing, child_results, child_mask)
            subs[sub] = old
            if maximizing:
                if value > best:
                    best = value
                    best_move = (sub, cell)
                alpha = max(alpha, value)
            else:
                if value < best:
                    best = value
                    best_move = (sub, cell)
                beta = min(beta, value)
            if beta <= alpha:
                break
        return best, best_move

    btp = -1 if board_to_play is None else board_to_play[0] * 3 + board_to_play[1]
    value, move = ab(btp, depth, float("-inf"), float("inf"), True, results, mask)
    if move is None:
        return value, None
    sub, cell = move
    return value, [sub // 3, sub % 3, cell // 3, cell % 3]


class AlphaBetaAgent(BaseAgent):
    """Opens in the center, then searches to depth_local on a forced board
    and depth_global when the next board is free."""

    depth_local = 5
    depth_global = 4

    def load(self):
        super().load()
        _load_tables()

    def choose(self, position):
        start = time.perf_counter()
        if position.is_empty():
            return 1, 1, 1, 1
        board_to_play = position.forced_board
        depth = self.depth_global if board_to_play is None else self.depth_local
        _, move = search(position.mover_board(), board_to_play, depth)
        if move is None:
            raise ValueError(f"{self.name} found no move (btp={board_to_play})")
        elapsed = time.perf_counter() - start
        print(f"{self.name} took {elapsed:.4f}s alpha-beta depth={depth}, btp={board_to_play}")
        return tuple(move)
