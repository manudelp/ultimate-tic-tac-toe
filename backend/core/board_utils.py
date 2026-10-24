"""Board helpers over numpy sub-boards. The rules themselves live in core.rules."""
import numpy as np

from core.rules import EMPTIES, FULL, OVER, WINNER, sub_index


def is_won(board):
    """Check if a 3x3 board is won. Returns 1, -1, or 0."""
    return WINNER[sub_index(board)]


def is_full(board):
    """Returns True if the board has no empty cells."""
    return FULL[sub_index(board)]


def is_playable(board):
    """Returns True if the board is not full and not won."""
    return not OVER[sub_index(board)]


def is_over(board):
    """Returns True if the board is full or won."""
    return OVER[sub_index(board)]


def can_play(board, row, col):
    """Returns True if the cell is empty."""
    return board[row, col] == 0


def get_playable_boards(board):
    """Return list of (i, j) tuples for playable sub-boards in a 3x3x3x3 board."""
    return [(i, j) for i in range(3) for j in range(3) if is_playable(board[i, j])]


def random_move(board):
    """Pick a random empty cell. Returns (row, col)."""
    empty = EMPTIES[sub_index(board)]
    if not empty:
        raise ValueError("No empty cells on board")
    return divmod(int(np.random.choice(empty)), 3)


def safe_set_extractor(board, move_set):
    """Pick a move from the set that doesn't send opponent to an over-board, if possible."""
    for move in move_set:
        if not is_over(board[move]):
            return move
    return move_set.pop()


def is_edge(x, y):
    """Returns True if (x, y) is an edge position on a 3x3 grid."""
    return (x + y) % 2 == 1
