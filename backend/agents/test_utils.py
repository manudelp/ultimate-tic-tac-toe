import numpy as np
import os
import time
from typing import Tuple
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

from others.taylor import TaylorAgent
from bots.greedy import GreedyAgent

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
hash_winning_boards = {}
hash_over_boards = {}
hash_blizzard_over_boards = {}
hash_blizzard_winning_boards = {}

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
                hash_winning_boards[bytes.fromhex(board_hex)] = int(winner)
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

def load_blizzard_over_boards(file_path):
    # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
    ''' Loads the over boards from a file and stores them in a dictionary 
    Each board's state is stored as a key (using its byte representation)
    '''
    try:
        with open(file_path, 'r') as file:
            for line in file:
                board_hex = line.strip()
                hash_blizzard_over_boards[bytes.fromhex(board_hex)] = True
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Over boards will not be loaded.")

def load_blizzard_winning_boards(file_path):
    # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
    ''' Loads the winning boards from a file and stores them in a dictionary 
    Each board's state is stored as a key (using its byte representation)
    '''
    try:
        with open(file_path, 'r') as file:
            for line in file:
                board_hex, winner = line.strip().split(':')
                hash_blizzard_winning_boards[bytes.fromhex(board_hex)] = int(winner)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

# Local Board Functions
def get_winner(board, gamemode="default"):
    # TIMEIT APPROVED ✅
    """
    Retrieve the winner of a board from the preloaded dictionary of winning boards.
    Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
    """
    if board.shape != (3, 3):
        raise ValueError("The board must be a 2d array with shape (3, 3).")
    board_key = board.tobytes()
    
    if gamemode == "default":
        return hash_winning_boards.get(board_key, 0)
    elif gamemode == "blizzard":
        return hash_blizzard_winning_boards.get(board_key, 0)

def get_over_hash(board) -> bool:
    # TIMEIT APPROVED ✅
    ''' Returns whether the board is over'''
    board_key = board.tobytes()
    return hash_over_boards.get(board_key, False)

def get_over_blizzard_hash(board) -> bool:
    # TIMEIT APPROVED ✅
    ''' Returns whether the board is over'''
    board_key = board.tobytes()
    return hash_blizzard_over_boards.get(board_key, False)

def get_isOpen(board, gamemode="default") -> bool:
    # TIMEIT APPROVED ✅
    ''' Returns whether the board is open'''
    if gamemode == "default":
        return not get_over_hash(board)
    elif gamemode == "blizzard":
        return not get_over_blizzard_hash(board)

def get_isOpenBlizzard(board) -> bool:
    # TIMEIT APPROVED ✅
    ''' Returns whether the board is open'''
    return not get_over_blizzard_hash(board)

def is_board_open(board, r, c, gamemode="default"):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is open, False otherwise '''
    if gamemode == 'default':
        return get_isOpen(board[r, c])
    elif gamemode == 'blizzard':
        return get_isOpenBlizzard(board[r, c])
    else:
        raise ValueError("Invalid gamemode. Please choose 'default' or 'blizzard'.")

def get_isFull(board):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is over, False otherwise 
    Since it is always called after checking for a win, it is taken as being a draw '''
    return (np.count_nonzero(board == 0) == 0)

# Global Board Functions
def get_board_results(board, gamemode="default"):
    ''' Creates a 3x3 representation of the 3x3x3x3 board, with the results of the local boars '''
    if board.shape != (3, 3, 3, 3):
        raise ValueError("The board must be a 4d array with shape (3, 3, 3, 3).")
    
    board_results = np.zeros((3, 3), dtype=int)

    board_results[0, 0], board_results[0, 1], board_results[0, 2] = get_winner(board[0, 0], gamemode), get_winner(board[0, 1], gamemode), get_winner(board[0, 2], gamemode)
    board_results[1, 0], board_results[1, 1], board_results[1, 2] = get_winner(board[1, 0], gamemode), get_winner(board[1, 1], gamemode), get_winner(board[1, 2], gamemode)
    board_results[2, 0], board_results[2, 1], board_results[2, 2] = get_winner(board[2, 0], gamemode), get_winner(board[2, 1], gamemode), get_winner(board[2, 2], gamemode)

    return board_results

def is_game_over(board, gamemode="default"):
    # TIMEIT APPROVED ✅
    ''' Returns True if the global board is over, False otherwise '''
    not_over_locals = []
    if gamemode == 'default':
        for i in range(3):
            for j in range(3):
                if not get_over_hash(board[i, j]):
                    not_over_locals.append((i, j))
    elif gamemode == 'blizzard':
        for i in range(3):
            for j in range(3):
                if not get_over_blizzard_hash(board[i, j]):
                    not_over_locals.append((i, j))
    if len(not_over_locals) == 0:
        return True
    return False

def get_globalWinner(board, gamemode):
    # TIMEIT APPROVED ✅
    ''' Returns the winner of the global board '''
    board_results = get_board_results(board, gamemode)
    return get_winner(board_results)

def reset_agents(agent1, agent2):
    agent1.reset()
    agent2.reset()

# Hash Loading
won_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_winning_boards.txt')
over_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_over_boards.txt')
blizzard_over_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_blizzard_over_boards.txt')
blizzard_winning_boards_hash_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'hashes', 'hash_blizzard_winning_boards.txt')

load_winning_boards(won_boards_hash_path)
load_over_boards(over_boards_hash_path)
load_blizzard_over_boards(blizzard_over_boards_hash_path)
load_blizzard_winning_boards(blizzard_winning_boards_hash_path)

# Game Simulation Functions
def simulate_blizzard(board: np.ndarray, blizzards: int) -> None:
    ''' Given a 3x3x3x3 board, fills n random cells with a number 2 '''
    if board.shape != (3, 3, 3, 3):
        raise ValueError("The board must be a 4d array with shape (3, 3, 3, 3).")
    
    # Get all the empty cells
    if type(blizzards) != int:
        raise ValueError(f"Blizzards Simulation is being called but blizzards constant is not an integer. Blizzards is: {blizzards}")
    
    empty_cells = np.argwhere(board == 0)
    np.random.shuffle(empty_cells)
    for i in range(blizzards):
        row, col, r, c = empty_cells[i]
        board[row, col, r, c] = 2

def play_single_game(agent1, agent2, first_player_is_agent1: bool, gamemode="default", blizzards=None) -> Tuple[int, dict]:
    """Simulates a single game between two agents, records the average move time per agent, 
    and returns the winner and average move times for each agent."""
    board = np.zeros((3, 3, 3, 3), dtype=int)

    if gamemode == 'blizzard':
        simulate_blizzard(board, blizzards)
    elif gamemode != 'default':
        raise ValueError("Invalid gamemode. Please choose 'default' or 'blizzard'.")

    current_agent = agent1 if first_player_is_agent1 else agent2
    opponent_agent = agent2 if first_player_is_agent1 else agent1
    board_to_play = None
    turn = 1

    move_times = {agent1: [], agent2: []}  # To store individual move times

    while True:
        agent_marker = 1 if current_agent == agent1 else -1
        current_board = board if agent_marker == 1 else -1 * board
        # print(f"Current board is {current_board}")

        # Turn all -2 elements in the board to 2
        current_board[current_board == -2] = 2

        # Measure time for the current agent to make a move
        start_time = time.time()
        move = current_agent.action(current_board, board_to_play)
        move_time = (time.time() - start_time) * 1000  # Time in milliseconds
        move_times[current_agent].append(move_time)

        global_row, global_col, local_row, local_col = move
        board[global_row, global_col, local_row, local_col] = agent_marker

        winner = get_globalWinner(board, gamemode)
        if winner != 0 or is_game_over(board, gamemode):
            break

        board_to_play = (local_row, local_col) if is_board_open(board, local_row, local_col, gamemode) else None
        
        current_agent, opponent_agent = opponent_agent, current_agent
        turn += 1

    # Calculate average move times for each agent
    avg_move_times = {agent: sum(times) / len(times) if times else 0 for agent, times in move_times.items()}
    total_amount_of_moves_ag1 = len(move_times[agent1])
    total_amount_of_moves_ag2 = len(move_times[agent2])
    return winner, avg_move_times, total_amount_of_moves_ag1, total_amount_of_moves_ag2

def play_multiple_games(agent1, agent2, rounds, gamemode="default", blizzards=None) -> Tuple[int, int, int, float, float]:    
    agent1_wins, agent2_wins, draws = 0, 0, 0
    total_move_times = {agent1: [], agent2: []}

    for round_num in range(rounds):
        # First game where agent1 goes first
        result1, avg_move_times1, moves_amount_ag1, moves_amount_ag2 = play_single_game(agent1, agent2, first_player_is_agent1=True, gamemode=gamemode, blizzards=blizzards)
        reset_agents(agent1, agent2)
        avg_times_agent1 = avg_move_times1[agent1] / moves_amount_ag1
        avg_times_agent2 = avg_move_times1[agent2] / moves_amount_ag2
        total_move_times[agent1].append(avg_times_agent1)
        total_move_times[agent2].append(avg_times_agent2)

        # Second game where agent2 goes first
        result2, avg_move_times2, moves_amount_ag1, moves_amount_ag2 = play_single_game(agent1, agent2, first_player_is_agent1=False, gamemode=gamemode, blizzards=blizzards)
        reset_agents(agent1, agent2)
        avg_times_agent1 = avg_move_times2[agent1] / moves_amount_ag1
        avg_times_agent2 = avg_move_times2[agent2] / moves_amount_ag2
        total_move_times[agent1].append(avg_times_agent1)
        total_move_times[agent2].append(avg_times_agent2)

        agent1_wins += (result1 == 1) + (result2 == 1)
        agent2_wins += (result1 == -1) + (result2 == -1)
        draws += (result1 == 0) + (result2 == 0)

    # Compute overall average move times across all games
    avg_move_times = {
        agent1: sum(total_move_times[agent1]) / len(total_move_times[agent1]) if total_move_times[agent1] else 0,
        agent2: sum(total_move_times[agent2]) / len(total_move_times[agent2]) if total_move_times[agent2] else 0,
    }
    
    avg_agent1_times = avg_move_times[agent1]
    avg_agent2_times = avg_move_times[agent2]
    
    return agent1_wins, agent2_wins, draws, avg_agent1_times, avg_agent2_times
