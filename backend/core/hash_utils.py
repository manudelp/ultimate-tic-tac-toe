import numpy as np
import os


# Hash-based winner lookup (precomputed)
_hash_winning_boards = {}


def _load_winning_boards(file_path):
    """Load precomputed winning boards from file into hash table."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                board_hex, winner = line.strip().split(':')
                _hash_winning_boards[bytes.fromhex(board_hex)] = int(winner)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")


def get_winner_from_hash(board):
    """Look up winner from precomputed hash. Returns 1, -1, or 0."""
    if board.shape != (3, 3):
        raise ValueError("The board must be a 2d array with shape (3, 3).")
    return _hash_winning_boards.get(board.tobytes(), 0)


def get_board_results(board):
    """Creates a 3x3 representation of the 3x3x3x3 board with local board results."""
    if board.shape != (3, 3, 3, 3):
        raise ValueError("The board must be a 4d array with shape (3, 3, 3, 3).")
    results = np.zeros((3, 3), dtype=int)
    for i in range(3):
        for j in range(3):
            results[i, j] = get_winner_from_hash(board[i, j])
    return results


def get_winner(board_results):
    """Determine if there is a winner from the 3x3 board results. Returns 1, -1, or 0."""
    if board_results.shape != (3, 3):
        raise ValueError("The board_results must be a 2d array with shape (3, 3).")
    return get_winner_from_hash(board_results)

# Load winning boards on module import
_hash_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hash_winning_boards.txt')
_load_winning_boards(_hash_file_path)
