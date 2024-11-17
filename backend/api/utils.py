# backend/api/utils.py

import numpy as np
import os

hash_winning_boards = {}

def fancyBoardPrinter(board):
    # Output the super board in a 3x3 layout
    cell_width = 2  # Adjust the width of each cell to accommodate larger numbers

    for i in range(board.shape[0]):  # Iterate over rows of subboards
        for x in range(3):  # Each subboard has 3 rows
            row_output = ""
            for j in range(board.shape[1]):  # Iterate over columns of subboards
                row_output += " | ".join(f"{num:>{cell_width}}" for num in board[i, j][x]) + "    "  # Join the rows of each subboard with adjusted width
            print(row_output)  # Print the row of the current level of subboards
        if i != 2:
            print()  # Print a separator between sets of subboard rows

def load_winning_boards(file_path):
    # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
    
    """
    Load the winning boards from a file and store them in a dictionary.
    Each board's state is stored as a key (using its byte representation) with the winner (1 or -1) as its value.
    """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                board_hex, winner = line.strip().split(':')
                hash_winning_boards[bytes.fromhex(board_hex)] = int(winner)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

def get_winner(board):
    # TIMEIT APPROVED ✅
    """
    Retrieve the winner of a board from the preloaded dictionary of winning boards.
    Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
    """
    if board.shape != (3, 3):
        raise ValueError("The board must be a 2d array with shape (3, 3).")
    
    board_key = board.tobytes()
    return hash_winning_boards.get(board_key, 0)

def get_board_results(board):
    ''' Creates a 3x3 representation of the 3x3x3x3 board, with the results of the local boars '''
    if board.shape != (3, 3, 3, 3):
        raise ValueError("The board must be a 4d array with shape (3, 3, 3, 3).")
    
    board_results = np.zeros((3, 3), dtype=int)

    board_results[0, 0], board_results[0, 1], board_results[0, 2] = get_winner(board[0, 0]), get_winner(board[0, 1]), get_winner(board[0, 2])
    board_results[1, 0], board_results[1, 1], board_results[1, 2] = get_winner(board[1, 0]), get_winner(board[1, 1]), get_winner(board[1, 2])
    board_results[2, 0], board_results[2, 1], board_results[2, 2] = get_winner(board[2, 0]), get_winner(board[2, 1]), get_winner(board[2, 2])

    return board_results

won_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_winning_boards.txt')
load_winning_boards(won_boards_hash_path)

