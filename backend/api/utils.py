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

    board_results[0, 0], board_results[0, 1], board_results[0, 2] = get_winner(board[0, 0]), get_winner(board[0, 1]), get_winner(board[0, 2])
    board_results[1, 0], board_results[1, 1], board_results[1, 2] = get_winner(board[1, 0]), get_winner(board[1, 1]), get_winner(board[1, 2])
    board_results[2, 0], board_results[2, 1], board_results[2, 2] = get_winner(board[2, 0]), get_winner(board[2, 1]), get_winner(board[2, 2])

    return board_results

# Load the winning boards from the hashed file
hash_won_boards = {}
hash_over_boards = {}
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
                hash_won_boards[bytes.fromhex(board_hex)] = int(winner)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

def load_over_boards(file_path):
    # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
    ''' Loads the over boards from a file and stores them in a dictionary 
    Each board's state is stored as a key (using its byte representation)
    '''
    try:
        with open(file_path, 'r') as file:
            for line in file:
                board_hex = line.strip()
                hash_over_boards[bytes.fromhex(board_hex)] = True
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Over boards will not be loaded.")    

# Get the global game winner
def get_winner(board):
    # TIMEIT APPROVED ✅
    """
    Retrieve the winner of a board from the preloaded dictionary of winning boards.
    Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
    """
    if board.shape != (3, 3):
        raise ValueError("The board must be a 2d array with shape (3, 3).")
    
    board_key = board.tobytes()
    return hash_won_boards.get(board_key, 0)

def get_isOver(board):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is over, False otherwise '''
    board_key = board.tobytes()
    return hash_over_boards.get(board_key, False)

def get_isDraw(board):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is over, False otherwise 
    Since it is always called after checking for a win, it is taken as being a draw '''
    return (np.count_nonzero(board) == 9)

def is_game_over(board):
    # TIMEIT APPROVED ✅
    ''' Returns True if the global board is over, False otherwise '''
    not_over_locals = []
    for i in range(3):
        for j in range(3):
            if not get_isOver(board[i, j]):
                not_over_locals.append((i, j))
    if len(not_over_locals) == 0:
        return True
    return False

def get_globalWinner(board):
    # TIMEIT APPROVED ✅
    ''' Returns the winner of the global board '''
    board_results = get_board_results(board)
    return get_winner(board_results)

# Determine the absolute path to the hash_winning_boards.txt file
won_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_winning_boards.txt')
over_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_over_boards.txt')

# Load the winning boards using the determined path
load_winning_boards(won_boards_hash_path)
load_over_boards(over_boards_hash_path)

# Over Board Example
over_local_board = np.array([[-1, 0, 1], 
                              [1, 0, 1], 
                              [-1, 0, 1]],)

not_over_local_board = np.array([[-1, 0, 1], 
                              [1, 0, 0], 
                              [-1, 0, 1]],)

board_test = np.zeros((3, 3, 3, 3), dtype=int)
board_test[0, 0] = over_local_board
board_test[0, 1] = over_local_board
board_test[0, 2] = over_local_board
board_test[1, 0] = over_local_board
board_test[1, 1] = over_local_board
board_test[1, 2] = over_local_board
board_test[2, 0] = over_local_board
board_test[2, 1] = over_local_board
board_test[2, 2] = over_local_board

# Tests
print(f"Board results are\n {get_board_results(board_test)}")
print(f"Is the board over? {is_game_over(board_test)}")