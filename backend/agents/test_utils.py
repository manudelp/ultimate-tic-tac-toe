import numpy as np
import os
from colorama import Style, Fore

# Board Printer
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

# Hashes
hash_won_boards = {}
hash_over_boards = {}

# Hashing Functions
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

# Local Board Functions
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

def get_isOver(board) -> bool:
    # TIMEIT APPROVED ✅
    ''' Returns whether the board is over'''
    board_key = board.tobytes()
    return hash_over_boards.get(board_key, False)

def get_isOpen(board) -> bool:
    # TIMEIT APPROVED ✅
    ''' Returns whether the board is open'''
    return not get_isOver(board)

def is_board_open(board, r, c):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is open, False otherwise '''
    return get_isOpen(board[r, c])

def get_isFull(board):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is over, False otherwise 
    Since it is always called after checking for a win, it is taken as being a draw '''
    return (np.count_nonzero(board) == 9)

# Global Board Functions
def get_board_results(board):
    ''' Creates a 3x3 representation of the 3x3x3x3 board, with the results of the local boars '''
    if board.shape != (3, 3, 3, 3):
        raise ValueError("The board must be a 4d array with shape (3, 3, 3, 3).")
    
    board_results = np.zeros((3, 3), dtype=int)

    board_results[0, 0], board_results[0, 1], board_results[0, 2] = get_winner(board[0, 0]), get_winner(board[0, 1]), get_winner(board[0, 2])
    board_results[1, 0], board_results[1, 1], board_results[1, 2] = get_winner(board[1, 0]), get_winner(board[1, 1]), get_winner(board[1, 2])
    board_results[2, 0], board_results[2, 1], board_results[2, 2] = get_winner(board[2, 0]), get_winner(board[2, 1]), get_winner(board[2, 2])

    return board_results

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

# Hash Loading
won_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_winning_boards.txt')
over_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_over_boards.txt')

load_winning_boards(won_boards_hash_path)
load_over_boards(over_boards_hash_path)

# Game Simulation Functions


# Play one game with detailed logging
def play_single_game(agent1, agent2, first_player_is_agent1: bool) -> int:
    """Simulates a single game between two agents, represented by 1 and -1
    And returns the winner of the game, or 0 of it's a draw

    Args:
        agent1 (class): One of the two agents to play
        agent2 (class): One of the two agents to play
        first_player_is_agent1 (bool): If True, agent1 plays first, else agent2 plays first. Useful for simulating multiple games with alternating starting agents

    Returns:
        int: 1 if the agent playing with 1 wins, -1 if the agent playing with -1 wins, 0 if it's a draw
    """

    # Initialize game board
    board = np.zeros((3, 3, 3, 3), dtype=int)
    current_agent = agent1 if first_player_is_agent1 else agent2
    opponent_agent = agent2 if first_player_is_agent1 else agent1
    board_to_play = None  # Initial freedom to choose any board
    turn = 1

    while True:
        # Determine if current agent is playing as 1 or -1
        agent_marker = 1 if current_agent == agent1 else -1
        agent_name = str(agent1) if agent_marker == 1 else str(agent2)
        
        # Pass the negated board if agent is playing as -1
        current_board = board if agent_marker == 1 else -1 * board

        # Print the board before the agent makes a move
        # print(f"\nCurrent board before {agent_name}'s move:")
        # fancyBoardPrinter(board)

        # Current agent makes a move
        move = current_agent.action(current_board, board_to_play)
        global_row, global_col, local_row, local_col = move

        # Log the move details
        # print(f"Turn {turn}: {agent_name} (playing as {'1' if agent_marker == 1 else '-1'}) chose move: {(int(global_row), int(global_col), int(local_row), int(local_col))}")

        # Update the board with the move
        board[global_row, global_col, local_row, local_col] = agent_marker

        # Print the updated board for debugging purposes
        # print(f"Updated board after {agent_name}'s move:")
        # fancyBoardPrinter(board)

        # Check if game is over
        winner = get_globalWinner(board)
        if winner != 0:
            # print(f"Game over! {agent_name} wins!")
            return winner
        
        if is_game_over(board):
            return winner

        # Determine next board_to_play based on this move
        board_to_play = (local_row, local_col) if is_board_open(board, local_row, local_col) else None

        # Swap agents for the next turn
        current_agent, opponent_agent = opponent_agent, current_agent
        turn += 1

# Run multiple games and alternate starting agent
def play_multiple_games(agent1, agent2, rounds):    
    agent1_wins, agent2_wins, draws = 0, 0, 0
    for round_num in range(rounds):
        # Alternate starting turns
        result1 = play_single_game(agent1, agent2, first_player_is_agent1=True)
        reset_agents(agent1, agent2)
        result2 = play_single_game(agent1, agent2, first_player_is_agent1=False)
        reset_agents(agent1, agent2)
        
        # Collect results for both games in each round
        agent1_wins += (result1 == 1) + (result2 == 1)
        agent2_wins += (result1 == -1) + (result2 == -1)
        draws += (result1 == 0) + (result2 == 0)
        
    return agent1_wins, agent2_wins, draws

def reset_agents(agent1, agent2):
    agent1.reset()
    agent2.reset()
