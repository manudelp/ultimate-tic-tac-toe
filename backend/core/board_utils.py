"""Shared board utility functions for Ultimate Tic-Tac-Toe."""
import numpy as np


def is_won(board):
    """Check if a 3x3 board is won. Returns 1, -1, or 0."""
    for i in range(3):
        if board[i, 0] == board[i, 1] == board[i, 2] != 0:
            return int(board[i, 0])
        if board[0, i] == board[1, i] == board[2, i] != 0:
            return int(board[0, i])
    if board[0, 0] == board[1, 1] == board[2, 2] != 0:
        return int(board[0, 0])
    if board[0, 2] == board[1, 1] == board[2, 0] != 0:
        return int(board[0, 2])
    return 0


def is_full(board):
    """Returns True if the board has no empty cells."""
    return np.all(board != 0)


def is_playable(board):
    """Returns True if the board is not full and not won."""
    return not is_full(board) and is_won(board) == 0


def is_over(board):
    """Returns True if the board is full or won."""
    return is_full(board) or is_won(board) != 0


def can_play(board, row, col):
    """Returns True if the cell is empty."""
    return board[row, col] == 0


def get_playable_boards(board):
    """Return list of (i, j) tuples for playable sub-boards in a 3x3x3x3 board."""
    return [(i, j) for i in range(3) for j in range(3) if is_playable(board[i, j])]


def random_move(board):
    """Pick a random empty cell. Returns (row, col)."""
    empty = np.flatnonzero(board == 0)
    if empty.size == 0:
        raise ValueError("No empty cells on board")
    return np.unravel_index(np.random.choice(empty), board.shape)


def safe_set_extractor(board, move_set):
    """Pick a move from the set that doesn't send opponent to an over-board, if possible."""
    for move in move_set:
        if not is_over(board[move]):
            return move
    return move_set.pop()


def is_edge(x, y):
    """Returns True if (x, y) is an edge position on a 3x3 grid."""
    return (x + y) % 2 == 1
