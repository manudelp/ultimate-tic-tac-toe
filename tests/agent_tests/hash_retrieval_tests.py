import numpy as np
from colorama import init, Fore, Style
from typing import Any, Union, Tuple
import ast

def isWon(subboard):
    # TIMEIT APPROVED ✅
    ''' Returns None if the board is not won, 1 if player 1 won, -1 if player -1 won '''
    # Row 0
    sb_00, sb_01, sb_02 = subboard[0, 0], subboard[0, 1], subboard[0, 2]
    if sb_00 == sb_01 == sb_02 != 0:
        return sb_00
    
    # Row 1
    sb_10, sb_11, sb_12 = subboard[1, 0], subboard[1, 1], subboard[1, 2]
    if sb_10 == sb_11 == sb_12 != 0:
        return sb_10
    
    sb_20 = subboard[2, 0]
    # Save unncessary calcs, by using what we alreasy can

    # Column 1
    if sb_00 == sb_10 == sb_20 != 0:
        return sb_00
    
    # Diagonal BT
    if sb_20 == sb_11 == sb_02 != 0:
        return sb_20
    
    sb_21 = subboard[2, 1]
    # again, save time

    # Check Column 2
    if sb_01 == sb_11 == sb_21 != 0:
        return sb_01
    
    sb_22 = subboard[2, 2]
    # Row 2
    if sb_20 == sb_21 == sb_22 != 0:
        return sb_20
    
    # Column 2
    if sb_02 == sb_12 == sb_22 != 0:
        return sb_02
    
    # Diagonal TB
    if sb_00 == sb_11 == sb_22 != 0:
        return sb_00
    
    return None

def isFullGlobal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns True if the board is full, False otherwise, works only for 9x9 global boards '''
    return (np.count_nonzero(board) == 81)

def lineEval(line, player=1):
    # TIMEIT APPROVED ✅
    """ 
    Returns the heuristic value of the given row or column in the subboard.
    """
    empties = line.count(0)

    if empties == 3:
        return 0
    
    player_count = line.count(player)

    if empties == 2:
        return 0.2 if player_count == 1 else -0.2
    
    elif empties == 1:
        return 0.6 if player_count == 2 else (-0.6 if player_count == 0 else 0)
    
    else:
        # print(f"Found a full line at {line}, with {empties} empties")
        if player_count == 3:
            return 1
        elif player_count == 0:
            return -1
        else:
            return 0

def detectThreat(line):
    return line.count(0) == 1 and (line.count(1) == 2 or line.count(-1) == 2)

def localBoardEval(localBoard):
    """ 
    Evaluates the local board and returns an evaluation score for it.
    """
    score = 0
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    return round(score, 1)

def localBoardEval_v2(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    Returns 0 if both have winning threat
    '''
    score = 0
    player1_threat = False
    player2_threat = False
    
    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if detectThreat((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if detectThreat((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if detectThreat((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if detectThreat((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if detectThreat((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if detectThreat((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if detectThreat((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if detectThreat((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    # Check for conflicting threats
    if player1_threat and player2_threat:
        return 0  # Neutralize score if both players can win in one move

    return round(score, 1)

def localBoardEval_v3(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    Returns a toned down balance if both have winning threat
    '''
    score = 0
    player1_threat = False
    player2_threat = False
    
    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if detectThreat((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if detectThreat((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if detectThreat((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if detectThreat((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if detectThreat((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if detectThreat((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if detectThreat((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if detectThreat((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        if score == 0:
            return 0
        
        final_score = score * 0.2
        if final_score > 0:
            return round((final_score + 0.1), 1)
        else:
            return round((final_score - 0.1), 1)

    return round(score, 1)

def isFull(board):
    return np.count_nonzero(board == 0) == 0

def isPlayable(board):
    ''' Returns True if the local 3x3 board is still playable '''
    return not isFull(board) and not isWon(board)

def isOver(board):
    return isFull(board) or isWon(board)

class RetrievalAgent:
    def __init__(self):
        # Initialize the dictionaries before loading data
        self.hash_won_boards = {}
        self.hash_eval_boards = {}
        self.hash_eval_v2_boards = {}
        self.hash_eval_v3_boards = {}
        self.hash_draw_boards = {}
        self.hash_over_boards = {}
        self.hash_winnable_boards_by_one = {}
        self.hash_winnable_boards_by_minus_one = {}
        self.hash_HyphenNumeric_boards = {}

        # Load both winning boards and evaluated boards during initialization
        self.load_winning_boards('backend/agents/hashes/hash_winning_boards.txt')
        self.load_evaluated_boards('backend/agents/hashes/hash_evaluated_boards.txt')
        self.load_evaluated_v2_boards('backend/agents/hashes/hash_evaluated_boards_v2.txt')
        self.load_evaluated_v3_boards('backend/agents/hashes/hash_evaluated_boards_v3.txt')
        self.load_drawn_boards('backend/agents/hashes/hash_draw_boards.txt')
        # self.load_move_boards('backend/agents/hashes/hash_move_boards.txt')
        self.load_over_boards('backend/agents/hashes/hash_over_boards.txt')
        self.load_winnable_boards_one('backend/agents/hashes/hash_winnable_boards_by_one.txt')
        self.load_winnable_boards_minus_one('backend/agents/hashes/hash_winnable_boards_by_minus_one.txt')
        self.load_HyphenNumeric_boards('backend/agents/hashes/hash_HyphenNumeric_boards.txt')


    def load_winning_boards(self, file_path):
        """
        Load the winning boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with the winner (1 or -1) as its value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, winner = line.strip().split(':')
                    self.hash_won_boards[bytes.fromhex(board_hex)] = int(winner)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

    def load_evaluated_boards(self, file_path):
        """
        Load the evaluated boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with its heuristic value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, heuristic_value = line.strip().split(':')
                    self.hash_eval_boards[bytes.fromhex(board_hex)] = float(heuristic_value)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_evaluated_v2_boards(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, heuristic_value = line.strip().split(':')
                    self.hash_eval_v2_boards[bytes.fromhex(board_hex)] = float(heuristic_value)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_evaluated_v3_boards(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, heuristic_value = line.strip().split(':')
                    self.hash_eval_v3_boards[bytes.fromhex(board_hex)] = float(heuristic_value)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_drawn_boards(self, file_path):
        """
        Load the drawn boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with a boolean value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, is_draw = line.strip().split(':')
                    self.hash_draw_boards[bytes.fromhex(board_hex)] = (is_draw == 'True')
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Drawn boards will not be loaded.")

    def load_over_boards(self, file_path):
        ''' Loads the over boards from a file and stores them in a dictionary 
        Each board's state is stored as a key (using its byte representation)
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex = line.strip()
                    self.hash_over_boards[bytes.fromhex(board_hex)] = True
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Over boards will not be loaded.")        

    def load_winnable_boards_one(self, file_path):
        ''' 
        Loads the winnable boards from a file and stores them in a dictionary. 
        Each board's state is stored as a key (using its byte representation).
        They are stored as board : winning_moves,
        where winning_moves is a set of tuples with the moves to win.
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, moves = line.strip().split(':')
                    moves = ast.literal_eval(moves)  # Safely evaluate the set of tuples
                    self.hash_winnable_boards_by_one[bytes.fromhex(board_hex)] = set(moves)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winnable boards will not be loaded.")

    def load_winnable_boards_minus_one(self, file_path):
        ''' 
        Loads the winnable boards from a file and stores them in a dictionary. 
        Each board's state is stored as a key (using its byte representation).
        They are stored as board : winning_moves,
        where winning_moves is a set of tuples with the moves to win.
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, moves = line.strip().split(':')
                    moves = ast.literal_eval(moves)  # Safely evaluate the set of tuples
                    self.hash_winnable_boards_by_minus_one[bytes.fromhex(board_hex)] = set(moves)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winnable boards will not be loaded.")


    def get_winner_hash(self, board):
        """
        Retrieve the winner of a board from the preloaded dictionary of winning boards.
        Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
        """
        board_key = board.tobytes()
        return self.hash_won_boards.get(board_key, 0)

    def get_eval_hash(self, board):
        """
        Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards.
        If the board is not in the dictionary, return None (or handle it as needed).
        """
        board_key = board.tobytes()
        local_eval = self.hash_eval_boards.get(board_key, None)
        if local_eval is None:
            raise ValueError(f"Board {board} not found in evaluated boards.")
        return local_eval

    def get_eval_v2_hash(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        local_eval_v2 = self.hash_eval_v2_boards.get(board_key, None)
        if local_eval_v2 is None:
            raise ValueError(f"Board {board} not found in evaluated V2 boards.")
        return local_eval_v2
    
    def get_eval_v3_hash(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        local_eval_v3 = self.hash_eval_v3_boards.get(board_key, None)
        if local_eval_v3 is None:
            raise ValueError(f"Board {board} not found in evaluated V3 boards.")
        return local_eval_v3

    def get_draw_hash(self, board):
        """
        Retrieve the draw status of a board from the preloaded dictionary of drawn boards.
        Returns True if the board is a draw, False otherwise.
        """
        board_key = board.tobytes()
        return self.hash_draw_boards.get(board_key, False)

    def get_over_hash(self, board):
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_over_boards.get(board_key, False)
    
    def get_playable_hash(self, board):
        ''' Returns True if the board is playable, False otherwise '''
        return not self.get_over_hash(board)

    def get_winnable_by_one_hash(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_one.get(board_key, set())

    def get_winnable_by_minus_one_hash(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_minus_one.get(board_key, set())
    
    def get_HyphenNumeric_hash(self, board, board_to_play):
        ''' Returns the best move for the given HyphenNumeric board '''
        key = self.get_HyphenNumeric_key(board, board_to_play)
        return self.hash_HyphenNumeric_boards.get(key, None)

    def get_HyphenNumeric_key(self, board: np.array, board_to_play: Union[Tuple[int, int], None]):
        ''' Returns the key for the HyphenNumeric boards dictionary '''
        # Split board representation into two frozensets for Player 1 and Player -1 moves
        player1_set, player_minus1_set = self.board_to_HyphenNumeric_sets(board)
        return ((frozenset(player1_set), frozenset(player_minus1_set)), board_to_play)

    def board_to_HyphenNumeric_sets(self, board: np.array):
        ''' Convert the board to two sets of tuples representing player positions '''
        player1_pieces = set()
        player_minus1_pieces = set()

        for global_row in range(board.shape[0]):
            for global_col in range(board.shape[1]):
                for local_row in range(board.shape[2]):
                    for local_col in range(board.shape[3]):
                        piece = board[global_row, global_col, local_row, local_col]
                        if piece != 0:  # Only record positions with a placed piece
                            position = (global_row, global_col, local_row, local_col)
                            if piece == 1:
                                player1_pieces.add(position)
                            elif piece == -1:
                                player_minus1_pieces.add(position)

        return player1_pieces, player_minus1_pieces

    def parse_HyphenNumeric_board(self, board_str):
        ''' Convert the HyphenNumeric board string into a list of player positions '''
        # Split the board state by '__' to separate each move
        moves = board_str.split('__')
        
        # Initialize player piece sets
        player_1_positions = set()
        player_neg_1_positions = set()
        
        # Process each move and assign to correct player based on position
        for idx, move in enumerate(moves):
            positions = tuple(map(int, move.split('_')))  # Convert the underscore-separated numbers into a tuple
            if idx % 2 == 0:
                player_1_positions.add(positions)  # Even positions are Player 1
            else:
                player_neg_1_positions.add(positions)  # Odd positions are Player -1

        # Return the two sets as a tuple
        return (frozenset(player_1_positions), frozenset(player_neg_1_positions))

    def load_HyphenNumeric_boards(self, file):
        ''' 
        Loads the boards from a file and stores them in a dictionary.
        Each board state is stored as a key (a tuple with the board's HyphenNumeric representation and the board_to_play).
        The value is the best move in (global_row, global_col, local_row, local_col) format.
        '''
        with open(file, 'r') as f:
            for line in f:
                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith('#'):
                    continue

                try:
                    # Step 1: Split the line by ":"
                    key_part, move_str = line.split(" : ")

                    # Step 2: Split the key_part by ", " to separate board_state and board_to_play
                    board_part, play_part = key_part.split(", ")
                    
                    # Parse the board state
                    board_state = self.parse_HyphenNumeric_board(board_part.strip())
                    
                    # Parse board_to_play as a tuple of integers
                    board_to_play = tuple(map(int, play_part.split('_')))  # Convert "0_1" into (0, 1)
                    
                    # Parse best_move as a tuple of integers
                    best_move = tuple(map(int, move_str.strip().split('_')))  # Convert "0_1_0_2" into (0, 1, 0, 2)

                    # Store the key-value pair in the dictionary
                    self.hash_HyphenNumeric_boards[(board_state, board_to_play)] = best_move

                except Exception as e:
                    print(f"Error parsing line: {line} - Error: {e}")


# Example usage:
agent = RetrievalAgent()

# Test boards setup
board_1 = np.array([[1, 1, 1],
                    [0, -1, -1],
                    [0, 0, -1]])  # Player 1 wins on the top row

board_2 = np.array([[0, -1, 1],
                    [0, 1, -1],
                    [1, 0, -1]])  # Player 1 wins on the diagonal

board_3 = np.array([[-1, -1, 0],
                    [1, 1, 1],
                    [0, -1, 0]])  # Player 1 wins on the middle row

board_4 = np.array([[0, -1, 1],
                    [-1, -1, 1],
                    [1, -1, 0]])  # Player -1 wins on the middle column

board_5 = np.array([[-1, 1, 0],
                    [1, -1, 0],
                    [1, 0, -1]])  # Player -1 wins on the diagonal

board_6 = np.array([[-1, -1, -1],
                    [1, 1, 0],
                    [0, 1, 0]])  # Player -1 wins on the top row

board_7 = np.array([[1, -1, -1],
                    [1, -1, -1],
                    [0, 1, 1]])  # No winner yet

board_8 = np.array([[1, -1, 1],
                    [1, -1, -1],
                    [-1, 1, 1]])  # Draw (no more moves possible)

board_9 = np.array([[1, 1, 0],
                    [-1, -1, 0],
                    [0, 0, 0]])  # Not a win yet, but close

board_10 = np.array([[0, 0, 0],
                     [1, 1, 0],
                     [-1, -1, 0]])  # Another close board without a winner

board_11 = np.array([[1, -1, 1],
                    [-1, -1, 1],
                    [0, 1, -1]])  # Secured Draw (will always be Draw)

board_12 = np.array([[-1, 0, 1],
                    [1, -1, -1],
                    [-1, 1, 1]]) # Secured Draw (will always be Draw)

# For Winnable Tests Only!
board_13 = np.array([[1, 0, 1],
                    [1, 0, 0],
                    [0, 1, 1]]) # winnable by 1 in (0, 1), (1, 1), (1, 2), (2, 0)

board_14 = np.array([[0, 0, 0],
                    [-1, -1, 0],
                    [-1, -1, 0]]) # winnable by -1 in (0, 0), (0, 1), (0, 2), (1, 2), (2, 2)

board_15 = np.array([[-1, -1, 0],
                    [-1, 0, 1],
                    [0, 1, 1]]) # winnable by 1 in (0, 2), (2, 0) || winnable by -1 in (0, 2), (2, 0)

super_board_1 = np.zeros((3, 3, 3, 3), dtype=int)
super_board_1[0, 0, 0, 0] = 1
super_board_1[1, 2, 1, 1] = -1
super_board_1[0, 1, 1, 2] = 1
super_board_1[1, 1, 1, 1] = -1

# super_board_1_key = agent.board_to_HyphenNumeric_sets(super_board_1)
# print(f"Super Board 1 Key: {super_board_1_key}")

# print(Style.BRIGHT + Fore.YELLOW + f"\nThe HyphenNumeric Hash currently looks like this:\n{agent.hash_HyphenNumeric_boards}\n" + Style.RESET_ALL)



b1_eval, b1_eval_v2, b1_eval_v3 = localBoardEval(board_1), localBoardEval_v2(board_1), localBoardEval_v3(board_1)
b2_eval, b2_eval_v2, b2_eval_v3 = localBoardEval(board_2), localBoardEval_v2(board_2), localBoardEval_v3(board_2)
b3_eval, b3_eval_v2, b3_eval_v3 = localBoardEval(board_3), localBoardEval_v2(board_3), localBoardEval_v3(board_3)
b4_eval, b4_eval_v2, b4_eval_v3 = localBoardEval(board_4), localBoardEval_v2(board_4), localBoardEval_v3(board_4)
b5_eval, b5_eval_v2, b5_eval_v3 = localBoardEval(board_5), localBoardEval_v2(board_5), localBoardEval_v3(board_5)
b6_eval, b6_eval_v2, b6_eval_v3 = localBoardEval(board_6), localBoardEval_v2(board_6), localBoardEval_v3(board_6)
b7_eval, b7_eval_v2, b7_eval_v3 = localBoardEval(board_7), localBoardEval_v2(board_7), localBoardEval_v3(board_7)
b8_eval, b8_eval_v2, b8_eval_v3 = localBoardEval(board_8), localBoardEval_v2(board_8), localBoardEval_v3(board_8)
b9_eval, b9_eval_v2, b9_eval_v3 = localBoardEval(board_9), localBoardEval_v2(board_9), localBoardEval_v3(board_9)
b10_eval, b10_eval_v2, b10_eval_v3 = localBoardEval(board_10), localBoardEval_v2(board_10), localBoardEval_v3(board_10)
b11_eval, b11_eval_v2, b11_eval_v3 = localBoardEval(board_11), localBoardEval_v2(board_11), localBoardEval_v3(board_11)
b12_eval, b12_eval_v2, b12_eval_v3 = localBoardEval(board_12), localBoardEval_v2(board_12), localBoardEval_v3(board_12)

# region Eval Prints
# V1 Evals
# print(f"Eval Version 1 for Board 1 is {b1_eval}")
# print(f"Eval Version 1 for Board 2 is {b2_eval}")
# print(f"Eval Version 1 for Board 3 is {b3_eval}")
# print(f"Eval Version 1 for Board 4 is {b4_eval}")
# print(f"Eval Version 1 for Board 5 is {b5_eval}")
# print(f"Eval Version 1 for Board 6 is {b6_eval}")
# print(f"Eval Version 1 for Board 7 is {b7_eval}")
# print(f"Eval Version 1 for Board 8 is {b8_eval}")
# print(f"Eval Version 1 for Board 9 is {b9_eval}")
# print(f"Eval Version 1 for Board 10 is {b10_eval}")
# print(f"Eval Version 1 for Board 11 is {b11_eval}")
# print(f"Eval Version 1 for Board 12 is {b12_eval}")

# V2 Evals
# print(f"Eval Version 2 for Board 1 is {b1_eval_v2}")
# print(f"Eval Version 2 for Board 2 is {b2_eval_v2}")
# print(f"Eval Version 2 for Board 3 is {b3_eval_v2}")
# print(f"Eval Version 2 for Board 4 is {b4_eval_v2}")
# print(f"Eval Version 2 for Board 5 is {b5_eval_v2}")
# print(f"Eval Version 2 for Board 6 is {b6_eval_v2}")
# print(f"Eval Version 2 for Board 7 is {b7_eval_v2}")
# print(f"Eval Version 2 for Board 8 is {b8_eval_v2}")
# print(f"Eval Version 2 for Board 9 is {b9_eval_v2}")
# print(f"Eval Version 2 for Board 10 is {b10_eval_v2}")
# print(f"Eval Version 2 for Board 11 is {b11_eval_v2}")
# print(f"Eval Version 2 for Board 12 is {b12_eval_v2}")

# V3 Evals
# print(f"Eval Version 3 for Board 1 is {b1_eval_v3}")
# print(f"Eval Version 3 for Board 2 is {b2_eval_v3}")
# print(f"Eval Version 3 for Board 3 is {b3_eval_v3}")
# print(f"Eval Version 3 for Board 4 is {b4_eval_v3}")
# print(f"Eval Version 3 for Board 5 is {b5_eval_v3}")
# print(f"Eval Version 3 for Board 6 is {b6_eval_v3}")
# print(f"Eval Version 3 for Board 7 is {b7_eval_v3}")
# print(f"Eval Version 3 for Board 8 is {b8_eval_v3}")
# print(f"Eval Version 3 for Board 9 is {b9_eval_v3}")
# print(f"Eval Version 3 for Board 10 is {b10_eval_v3}")
# print(f"Eval Version 3 for Board 11 is {b11_eval_v3}")
# print(f"Eval Version 3 for Board 12 is {b12_eval_v3}")
# endregion

# Define Tests
def run_won_tests(agent):
    # Boards won by player 1
    assert agent.get_winner_hash(board_1) == 1, "Test Failed: Player 1 should have won board_1"
    assert agent.get_winner_hash(board_2) == 1, "Test Failed: Player 1 should have won board_2"
    assert agent.get_winner_hash(board_3) == 1, "Test Failed: Player 1 should have won board_3"
    assert agent.get_winner_hash(board_4) == -1, "Test Failed: Player -1 should have won board_4"
    assert agent.get_winner_hash(board_5) == -1, "Test Failed: Player -1 should have won board_5"
    assert agent.get_winner_hash(board_6) == -1, "Test Failed: Player -1 should have won board_6"
    assert agent.get_winner_hash(board_7) == 0, "Test Failed: Board 7 should not have a winner"
    assert agent.get_winner_hash(board_8) == 0, "Test Failed: Board 8 should not have a winner"
    assert agent.get_winner_hash(board_9) == 0, "Test Failed: Board 9 should not have a winner"
    assert agent.get_winner_hash(board_10) == 0, "Test Failed: Board 10 should not have a winner"
    assert agent.get_winner_hash(board_11) == 0, "Test Failed: Board 11 should not have a winner"
    assert agent.get_winner_hash(board_12) == 0, "Test Failed: Board 12 should not have a winner"

    print("All Won-Board tests passed successfully!")

def run_eval_tests_v1(agent):
    assert agent.get_eval_hash(board_1) == b1_eval, "Test Failed: Board 1 evaluation does not match"
    assert agent.get_eval_hash(board_2) == b2_eval, "Test Failed: Board 2 evaluation does not match"
    assert agent.get_eval_hash(board_3) == b3_eval, "Test Failed: Board 3 evaluation does not match"
    assert agent.get_eval_hash(board_4) == b4_eval, "Test Failed: Board 4 evaluation does not match"
    assert agent.get_eval_hash(board_5) == b5_eval, "Test Failed: Board 5 evaluation does not match"
    assert agent.get_eval_hash(board_6) == b6_eval, "Test Failed: Board 6 evaluation does not match"
    assert agent.get_eval_hash(board_7) == b7_eval, "Test Failed: Board 7 evaluation does not match"
    assert agent.get_eval_hash(board_8) == b8_eval, "Test Failed: Board 8 evaluation does not match"
    assert agent.get_eval_hash(board_9) == b9_eval, "Test Failed: Board 9 evaluation does not match"
    assert agent.get_eval_hash(board_10) == b10_eval, "Test Failed: Board 10 evaluation does not match"
    assert agent.get_eval_hash(board_11) == b11_eval, "Test Failed: Board 11 evaluation does not match"
    assert agent.get_eval_hash(board_12) == b12_eval, "Test Failed: Board 12 evaluation does not match"

    print("All Eval V1 tests passed successfully!")

def run_eval_tests_v2(agent):
    assert agent.get_eval_v2_hash(board_1) == b1_eval_v2, "Test Failed: Board 1 evaluation does not match"
    assert agent.get_eval_v2_hash(board_2) == b2_eval_v2, "Test Failed: Board 2 evaluation does not match"
    assert agent.get_eval_v2_hash(board_3) == b3_eval_v2, "Test Failed: Board 3 evaluation does not match"
    assert agent.get_eval_v2_hash(board_4) == b4_eval_v2, "Test Failed: Board 4 evaluation does not match"
    assert agent.get_eval_v2_hash(board_5) == b5_eval_v2, "Test Failed: Board 5 evaluation does not match"
    assert agent.get_eval_v2_hash(board_6) == b6_eval_v2, "Test Failed: Board 6 evaluation does not match"
    assert agent.get_eval_v2_hash(board_7) == b7_eval_v2, "Test Failed: Board 7 evaluation does not match"
    assert agent.get_eval_v2_hash(board_8) == b8_eval_v2, "Test Failed: Board 8 evaluation does not match"
    assert agent.get_eval_v2_hash(board_9) == b9_eval_v2, "Test Failed: Board 9 evaluation does not match"
    assert agent.get_eval_v2_hash(board_10) == b10_eval_v2, "Test Failed: Board 10 evaluation does not match"
    assert agent.get_eval_v2_hash(board_11) == b11_eval_v2, "Test Failed: Board 11 evaluation does not match"
    assert agent.get_eval_v2_hash(board_12) == b12_eval_v2, "Test Failed: Board 12 evaluation does not match"

    print("All Eval V2 tests passed successfully!")

def run_eval_tests_v3(agent):
    assert agent.get_eval_v3_hash(board_1) == b1_eval_v3, "Test Failed: Board 1 evaluation does not match"
    assert agent.get_eval_v3_hash(board_2) == b2_eval_v3, "Test Failed: Board 2 evaluation does not match"
    assert agent.get_eval_v3_hash(board_3) == b3_eval_v3, "Test Failed: Board 3 evaluation does not match"
    assert agent.get_eval_v3_hash(board_4) == b4_eval_v3, "Test Failed: Board 4 evaluation does not match"
    assert agent.get_eval_v3_hash(board_5) == b5_eval_v3, "Test Failed: Board 5 evaluation does not match"
    assert agent.get_eval_v3_hash(board_6) == b6_eval_v3, "Test Failed: Board 6 evaluation does not match"
    assert agent.get_eval_v3_hash(board_7) == b7_eval_v3, "Test Failed: Board 7 evaluation does not match"
    assert agent.get_eval_v3_hash(board_8) == b8_eval_v3, "Test Failed: Board 8 evaluation does not match"
    assert agent.get_eval_v3_hash(board_9) == b9_eval_v3, "Test Failed: Board 9 evaluation does not match"
    assert agent.get_eval_v3_hash(board_10) == b10_eval_v3, "Test Failed: Board 10 evaluation does not match"
    assert agent.get_eval_v3_hash(board_11) == b11_eval_v3, "Test Failed: Board 11 evaluation does not match"
    assert agent.get_eval_v3_hash(board_12) == b12_eval_v3, "Test Failed: Board 12 evaluation does not match"

    print("All Eval V3 tests passed successfully!")

def run_draw_tests(agent):
    assert agent.get_draw_hash(board_1) == False, "Test Failed: Board 1 should not be a draw"
    assert agent.get_draw_hash(board_2) == False, "Test Failed: Board 2 should not be a draw"
    assert agent.get_draw_hash(board_3) == False, "Test Failed: Board 3 should not be a draw"
    assert agent.get_draw_hash(board_4) == False, "Test Failed: Board 4 should not be a draw"
    assert agent.get_draw_hash(board_5) == False, "Test Failed: Board 5 should not be a draw"
    assert agent.get_draw_hash(board_6) == False, "Test Failed: Board 6 should not be a draw"
    assert agent.get_draw_hash(board_7) == False, "Test Failed: Board 7 should not be a draw"
    assert agent.get_draw_hash(board_8) == True, "Test Failed: Board 8 should be a draw"
    assert agent.get_draw_hash(board_9) == False, "Test Failed: Board 9 should not be a draw"
    assert agent.get_draw_hash(board_10) == False, "Test Failed: Board 10 should not be a draw"
    assert agent.get_draw_hash(board_11) == True, "Test Failed: Board 11 should be a draw"
    assert agent.get_draw_hash(board_12) == True, "Test Failed: Board 12 should be a draw"

    print("All Draw-Board tests passed successfully!")

def run_over_tests(agent):
    assert agent.get_over_hash(board_1) == True, "Test Failed: Board 1 should be over"
    assert agent.get_over_hash(board_2) == True, "Test Failed: Board 2 should be over"
    assert agent.get_over_hash(board_3) == True, "Test Failed: Board 3 should be over"
    assert agent.get_over_hash(board_4) == True, "Test Failed: Board 4 should be over"
    assert agent.get_over_hash(board_5) == True, "Test Failed: Board 5 should be over"
    assert agent.get_over_hash(board_6) == True, "Test Failed: Board 6 should be over"
    assert agent.get_over_hash(board_7) == False, "Test Failed: Board 7 should not be over"
    assert agent.get_over_hash(board_8) == True, "Test Failed: Board 8 should be over"
    assert agent.get_over_hash(board_9) == False, "Test Failed: Board 9 should not be over"
    assert agent.get_over_hash(board_10) == False, "Test Failed: Board 10 should not be over"
    assert agent.get_over_hash(board_11) == False, "Test Failed: Board 11 should not be over"
    assert agent.get_over_hash(board_12) == False, "Test Failed: Board 12 should not be over"
    print("All Over-Board tests passed successfully!")

def run_playable_tests(agent):
    assert agent.get_playable_hash(board_1) == isPlayable(board_1) == False, "Test Failed: Board 1 should not be playable"
    assert agent.get_playable_hash(board_2) == isPlayable(board_2) == False, "Test Failed: Board 2 should not be playable"
    assert agent.get_playable_hash(board_3) == isPlayable(board_3) == False, "Test Failed: Board 3 should not be playable"
    assert agent.get_playable_hash(board_4) == isPlayable(board_4) == False, "Test Failed: Board 4 should not be playable"
    assert agent.get_playable_hash(board_5) == isPlayable(board_5) == False, "Test Failed: Board 5 should not be playable"
    assert agent.get_playable_hash(board_6) == isPlayable(board_6) == False, "Test Failed: Board 6 should not be playable"
    assert agent.get_playable_hash(board_7) == isPlayable(board_7) == True, "Test Failed: Board 7 should be playable"
    assert agent.get_playable_hash(board_8) == isPlayable(board_8) == False, "Test Failed: Board 8 should not be playable"
    assert agent.get_playable_hash(board_9) == isPlayable(board_9) == True, "Test Failed: Board 9 should be playable"
    assert agent.get_playable_hash(board_10) == isPlayable(board_10) == True, "Test Failed: Board 10 should be playable"
    assert agent.get_playable_hash(board_11) == isPlayable(board_11) == True, "Test Failed: Board 11 should be playable"
    assert agent.get_playable_hash(board_12) == isPlayable(board_12) == True, "Test Failed: Board 12 should be playable"
    print("All Playable-Board tests passed successfully!")

def run_eval_commonsense_tests(agent):
    assert agent.get_eval_hash(board_1) == 6.4, "Test Failed: Board 1 should have a score of 6.4 since its won"
    assert agent.get_eval_hash(board_2) == 6.4, "Test Failed: Board 2 should have a score of 6.4 since its won"
    assert agent.get_eval_hash(board_3) == 6.4, "Test Failed: Board 3 should have a score of 6.4 since its won"
    assert agent.get_eval_hash(board_4) == -6.4, "Test Failed: Board 4 should have a score of -6.4 since its won"
    assert agent.get_eval_hash(board_5) == -6.4, "Test Failed: Board 5 should have a score of -6.4 since its won"
    assert agent.get_eval_hash(board_6) == -6.4, "Test Failed: Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_eval_hash(board_7)) < 1, "Test Failed: Board 7 should have a low absolute score"
    assert agent.get_eval_hash(board_7) >= 0, "Test Failed: Board 7 should not have a negative score"
    assert abs(agent.get_eval_hash(board_8)) < 1, "Test Failed: Board 8 should have a score of 0"
    assert agent.get_eval_hash(board_9) <= 0, "Test Failed: Board 9 should not have a positive score"
    assert abs(agent.get_eval_hash(board_9)) < 1, "Test Failed: Board 7 should have a low absolute score"
    assert agent.get_eval_hash(board_10) == -1 * agent.get_eval_hash(board_9), "Test Failed: Board 10 score should be inverse of Board 9"
    assert agent.get_eval_hash(board_11) == 0, "Test Failed: Board 11 should have a score of 0"
    assert agent.get_eval_hash(board_12) == 0, "Test Failed: Board 12 should have a score of 0"

    print("All Eval Common-Sense tests passed successfully!")

def run_eval_v2_commonsense_tests(agent):
    assert agent.get_eval_v2_hash(board_1) == 6.4, "Test Failed: Board 1 should have a score of 6.4 since its won"
    assert agent.get_eval_v2_hash(board_2) == 6.4, "Test Failed: Board 2 should have a score of 6.4 since its won"
    assert agent.get_eval_v2_hash(board_3) == 6.4, "Test Failed: Board 3 should have a score of 6.4 since its won"
    assert agent.get_eval_v2_hash(board_4) == -6.4, "Test Failed: Board 4 should have a score of -6.4 since its won"
    assert agent.get_eval_v2_hash(board_5) == -6.4, "Test Failed: Board 5 should have a score of -6.4 since its won"
    assert agent.get_eval_v2_hash(board_6) == -6.4, "Test Failed: Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_eval_v2_hash(board_7)) < 1, "Test Failed: Board 7 should have a low absolute score"
    assert agent.get_eval_v2_hash(board_7) >= 0, "Test Failed: Board 7 should not have a negative score"
    assert abs(agent.get_eval_v2_hash(board_8)) < 1, "Test Failed: Board 8 should have a score of 0"
    assert agent.get_eval_v2_hash(board_9) <= 0, "Test Failed: Board 9 should not have a positive score"
    assert abs(agent.get_eval_v2_hash(board_9)) < 1, "Test Failed: Board 7 should have a low absolute score"
    assert agent.get_eval_v2_hash(board_10) == -1 * agent.get_eval_v2_hash(board_9), "Test Failed: Board 10 score should be inverse of Board 9"
    assert agent.get_eval_v2_hash(board_11) == 0, "Test Failed: Board 11 should have a score of 0"
    assert agent.get_eval_v2_hash(board_12) == 0, "Test Failed: Board 12 should have a score of 0"

    print("All Eval V2 Common-Sense tests passed successfully!")

def run_eval_v3_commonsense_tests(agent):
    assert agent.get_eval_v3_hash(board_1) == 6.4, "Test Failed: Board 1 should have a score of 6.4 since its won"
    assert agent.get_eval_v3_hash(board_2) == 6.4, "Test Failed: Board 2 should have a score of 6.4 since its won"
    assert agent.get_eval_v3_hash(board_3) == 6.4, "Test Failed: Board 3 should have a score of 6.4 since its won"
    assert agent.get_eval_v3_hash(board_4) == -6.4, "Test Failed: Board 4 should have a score of -6.4 since its won"
    assert agent.get_eval_v3_hash(board_5) == -6.4, "Test Failed: Board 5 should have a score of -6.4 since its won"
    assert agent.get_eval_v3_hash(board_6) == -6.4, "Test Failed: Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_eval_v3_hash(board_7)) < 1, "Test Failed: Board 7 should have a low absolute score"
    assert agent.get_eval_v3_hash(board_7) >= 0, "Test Failed: Board 7 should not have a negative score"
    assert abs(agent.get_eval_v3_hash(board_8)) < 1, "Test Failed: Board 8 should have a score of 0"
    assert agent.get_eval_v3_hash(board_9) <= 0, "Test Failed: Board 9 should not have a positive score"
    assert abs(agent.get_eval_v3_hash(board_9)) < 1, "Test Failed: Board 7 should have a low absolute score"
    assert agent.get_eval_v3_hash(board_10) == -1 * agent.get_eval_v3_hash(board_9), "Test Failed: Board 10 score should be inverse of Board 9"
    assert agent.get_eval_v3_hash(board_11) == 0, "Test Failed: Board 11 should have a score of 0"
    assert agent.get_eval_v3_hash(board_12) == 0, "Test Failed: Board 12 should have a score of 0"

    print("All Eval V3 Common-Sense tests passed successfully!")

def run_winnable_tests_one(agent):
    # Boards winnable by player 1
    assert agent.get_winnable_by_one_hash(board_1) == set(), "Test Failed: Board 1 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_2) == set(), "Test Failed: Board 2 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_3) == set(), "Test Failed: Board 3 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_4) == set(), "Test Failed: Board 4 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_5) == set(), "Test Failed: Board 5 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_6) == set(), "Test Failed: Board 6 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_7) == {(2, 0)}, "Test Failed: Board 7 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_8) == set(), "Test Failed: Board 8 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_9) == {(0, 2)}, "Test Failed: Board 9 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_10) == {(1, 2)}, "Test Failed: Board 10 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_11) == set(), "Test Failed: Board 11 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_12) == set(), "Test Failed: Board 12 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_13) == {(0, 1), (1, 1), (1, 2), (2, 0)}, "Test Failed: Board 13 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_14) == set(), "Test Failed: Board 14 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_15) == {(0, 2), (2, 0)}, "Test Failed: Board 15 should be winnable by player 1"

    print("All Winnable-By-One tests passed successfully!")

def run_winnable_tests_minus_one(agent):
    # Boards winnable by player -1
    assert agent.get_winnable_by_minus_one_hash(board_1) == set(), "Test Failed: Board 1 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_2) == set(), "Test Failed: Board 2 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_3) == set(), "Test Failed: Board 3 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_4) == set(), "Test Failed: Board 4 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_5) == set(), "Test Failed: Board 5 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_6) == set(), "Test Failed: Board 6 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_7) == {(2, 0)}, "Test Failed: Board 7 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_8) == set(), "Test Failed: Board 8 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_9) == {(1, 2)}, "Test Failed: Board 9 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_10) == {(2, 2)}, "Test Failed: Board 10 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_11) == set(), "Test Failed: Board 11 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_12) == set(), "Test Failed: Board 12 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_13) == set(), "Test Failed: Board 13 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_14) == {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)}, "Test Failed: Board 14 should be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_15) == {(0, 2), (2, 0)}, "Test Failed: Board 15 should be winnable by player -1"

    print("All Winnable-By-Minus-One tests passed successfully!")

def run_HyphenNumeric_tests(agent):
    assert agent.get_HyphenNumeric_hash(super_board_1, (0, 1)) == (0, 1, 0, 2), "Test Failed: Super Board 1 should have a best move of (0, 1, 0, 2)"

# Run the Tests!
run_won_tests(agent)
run_eval_tests_v1(agent)
run_eval_tests_v2(agent)
run_eval_tests_v3(agent)
run_draw_tests(agent)
run_over_tests(agent)
run_playable_tests(agent)
run_eval_commonsense_tests(agent)
run_eval_v2_commonsense_tests(agent)
run_eval_v3_commonsense_tests(agent)
run_winnable_tests_one(agent)
run_winnable_tests_minus_one(agent)
run_HyphenNumeric_tests(agent)

print("")
print(Style.BRIGHT + Fore.GREEN + "All tests passed successfully! 😄" + Style.RESET_ALL)