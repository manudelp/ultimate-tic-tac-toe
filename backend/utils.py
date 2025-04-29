import numpy as np
import os

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

# Get the results of the board
def get_board_results(board):
    ''' Creates a 3x3 representation of the 3x3x3x3 board, with the results of the local boars '''
    if board.shape != (3, 3, 3, 3):
        raise ValueError("The board must be a 4d array with shape (3, 3, 3, 3).")
    
    board_results = np.zeros((3, 3), dtype=int)

    for rows in range(3):
        for cols in range(3):
            board_results[rows, cols] = get_GlobalWinner(board[rows, cols])

    return board_results


# Load the winning boards from the hashed file
hash_winning_boards = {}
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

# Get the global game winner
def get_GlobalWinner(board):
    # TIMEIT APPROVED ✅
    """
    Retrieve the winner of a board from the preloaded dictionary of winning boards.
    Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
    """
    if board.shape != (3, 3):
        raise ValueError("The board must be a 2d array with shape (3, 3).")
    
    board_key = board.tobytes()
    return hash_winning_boards.get(board_key, 0)

# Add missing function to check winner from board results
def get_winner(board_results):
    """
    Determine if there is a winner from the board results.
    Returns 1 if player 1 won, -1 if player -1 won, or 0 if there is no winner yet.
    """
    if board_results.shape != (3, 3):
        raise ValueError("The board_results must be a 2d array with shape (3, 3).")
    
    return get_GlobalWinner(board_results)

# Determine the absolute path to the hash_winning_boards.txt file
hash_file_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_winning_boards.txt')

# Load the winning boards using the determined path
load_winning_boards(hash_file_path)
