"""The rules of Ultimate Tic-Tac-Toe, in one place.

Nine cells holding 0, +1 or -1 encode as one base-3 integer: digit r*3+c carries
cell (r, c), where 0 is empty, 1 is +1 and 2 is -1. Every rule question is then a
list lookup. The tables below are derived from `line_winner` when this module is
imported, so there is one implementation of "who won this" and 19,683 cached
answers to it.

The same tables serve both scales, because a sub-board of cells and the grid of
sub-board results are both nine values drawn from {0, +1, -1}.

Hot loops should bind the tables to locals (`over = rules.OVER`) rather than
reaching through the module on every node.
"""
import numpy as np

SIZE = 3 ** 9
P3 = tuple(3 ** i for i in range(9))

# Rows, then columns, then diagonals. The order is visible only on boards where
# both players hold a line, which legal play cannot reach.
LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)

_DIGIT = {0: 0, 1: 1, -1: 2}
_VALUE = (0, 1, -1)


def line_winner(cells):
    """Winner of nine cells as +1, -1 or 0. The one implementation of the rule."""
    for a, b, c in LINES:
        if cells[a] == cells[b] == cells[c] != 0:
            return cells[a]
    return 0


def cells_of(index):
    """The nine cell values behind a sub-board index, in cell order."""
    return [_VALUE[(index // P3[i]) % 3] for i in range(9)]


def _build():
    winner = [0] * SIZE
    full = [False] * SIZE
    over = [False] * SIZE
    empties = [()] * SIZE
    result_digit = [[0] * SIZE for _ in range(9)]
    wins_for = {1: [()] * SIZE, -1: [()] * SIZE}
    for index in range(SIZE):
        cells = cells_of(index)
        won = line_winner(cells)
        gaps = tuple(i for i in range(9) if cells[i] == 0)
        winner[index] = won
        full[index] = not gaps
        over[index] = bool(won) or not gaps
        empties[index] = gaps
        for sub in range(9):
            result_digit[sub][index] = _DIGIT[won] * P3[sub]
        if not won:
            for player in (1, -1):
                winning = []
                for cell in gaps:
                    cells[cell] = player
                    if line_winner(cells) == player:
                        winning.append(divmod(cell, 3))
                    cells[cell] = 0
                wins_for[player][index] = tuple(winning)
    return winner, full, over, empties, result_digit, wins_for


WINNER, FULL, OVER, EMPTIES, RESULT_DIGIT, _WINS_FOR = _build()


def winning_cells(cells, player):
    """A fresh set of (row, col) cells that would complete a line for `player`.

    Callers treat the result as their own and may consume it, so each call
    builds a new set.
    """
    return set(_WINS_FOR[player][sub_index(cells)])


def sub_index(cells):
    """Nine values in cell order, or a 3x3 array, to a sub-board index."""
    flat = cells.reshape(9) if isinstance(cells, np.ndarray) else cells
    index = 0
    for cell in range(9):
        index += _DIGIT[int(flat[cell])] * P3[cell]
    return index


def board_indexes(board):
    """A 3x3x3x3 board to the nine sub-board indexes, sub-boards in row-major order."""
    flat = np.asarray(board, dtype=int).reshape(9, 9)
    return [sub_index(flat[sub]) for sub in range(9)]


def meta_index(subs):
    """The grid of sub-board results, itself encoded as a sub-board index."""
    index = 0
    for sub in range(9):
        index += RESULT_DIGIT[sub][subs[sub]]
    return index


def outcome(subs):
    """(status, winner) for a position: ongoing, won with +1/-1, or draw with None."""
    winner = WINNER[meta_index(subs)]
    if winner:
        return "won", winner
    if any(not OVER[subs[sub]] for sub in range(9)):
        return "ongoing", None
    return "draw", None


def forced_sub_after(subs, cell):
    """The sub-board the opponent is sent to, or None when they may choose."""
    return None if OVER[subs[cell]] else cell


def legal_cells(subs, forced):
    """(sub, cell) pairs playable now. `forced` is a sub-board index or None."""
    if forced is not None:
        return [(forced, cell) for cell in EMPTIES[subs[forced]]]
    return [
        (sub, cell)
        for sub in range(9)
        if not OVER[subs[sub]]
        for cell in EMPTIES[subs[sub]]
    ]
