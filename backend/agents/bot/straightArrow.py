import numpy as np
import random
import ast
import os
from colorama import init, Style, Fore

"""
If it can make a subboard win, it plays it. 
# (not done yet) If it can block a subboard win, it blocks it
Otherwise plays randy
"""

class StraightArrowAgent:
    def __init__(self):
        self.id = "Straighty"
        self.icon = "🏹"
        self.moveNumber = 0
        self.hash_winnable_boards_by_one = {}
        self.hash_winnable_boards_by_minus_one = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        winnable_by_one_file = os.path.join(root_dir, 'agents', 'hashes', 'hash_winnable_boards_by_one.txt')
        winnable_by_minus_one_file = os.path.join(root_dir, 'agents', 'hashes', 'hash_winnable_boards_by_minus_one.txt')
        
        self.load_winnable_boards_one(winnable_by_one_file)
        self.load_winnable_boards_minus_one(winnable_by_minus_one_file)
    
    def __str__(self):
        self.str = f"{self.id}{self.icon}"
        return self.str

    def reset(self):
        # print("Resetting StraightArrowAgent")
        self.moveNumber = 0

    def action(self, super_board, board_to_play=None):
        super_board = np.array(super_board, dtype=int)
        rows, cols, *_ = super_board.shape
        # print(Style.BRIGHT + Fore.MAGENTA + f"{self.id} move number is {self.moveNumber}, the board_to_play he got is {board_to_play},\nthe board he received is \n{super_board}" + Style.RESET_ALL)

        over_boards = []
        for i in range(rows):
            for j in range(cols):
                if isOver(super_board[i, j]):
                    over_boards.append((i, j))

        # print(Style.BRIGHT + f"STRAIGHTY LISTS THE OVERBOARDS BEFORE PLANNING HIS MOVE:, THEY ARE AS FOLLOWS: {over_boards}" + Style.RESET_ALL)

        # First Move Go Center
        if np.count_nonzero(super_board) == 0:
            if self.moveNumber != 0:
                raise ValueError("No one has played, but moveNumber is not 0")
            self.moveNumber += 1
            return 1, 1, 1, 1

        if board_to_play is None:
            
            # Greedy Action! 
            
            # First Check Global Winner
            global_results = self.globalBoardResulter(super_board)
            global_winner = self.get_winnableByOne(global_results)
            if global_winner:
                for i in range(rows):
                    for j in range(cols):
                        if (i, j) in global_winner:
                            local_winnable = self.get_winnableByOne(super_board[i, j])
                            if isPlayable(super_board[i, j]) and local_winnable:
                                # print(f"Straighty found a GLOBAL BOARD WIN, in the board {i, j}, looks like this:\n {super_board[i, j]}")
                                local_row, local_col = safeSetExtractor(super_board, local_winnable)
                                self.moveNumber += 1
                                return i, j, local_row, local_col
                        
            # Otherwise Check Wins
            for i in range(rows):
                for j in range(cols):
                    if isPlayable(super_board[i, j]):
                        local_winner = self.get_winnableByOne(super_board[i, j])
                        if local_winner:
                            # print(f"Straighty found a local board to win, in the board {i, j}, looks like this:\n {super_board[i, j]}")
                            local_row, local_col = safeSetExtractor(super_board, local_winner)
                            self.moveNumber += 1
                            return i, j, local_row, local_col
            
            # Otherwise, Check Blocks
            for i in range(rows):
                for j in range(cols):
                    if isPlayable(super_board[i, j]):
                        local_blocker = self.get_winnableByMinusOne(super_board[i, j])
                        if local_blocker:
                            # print(f"Straighty found a local board to block, in the board {i, j}, looks like this:\n {super_board[i, j]}")
                            local_row, local_col = safeSetExtractor(super_board, local_blocker)
                            self.moveNumber += 1
                            return i, j, local_row, local_col

            # Otherwise, Center Move
            if isPlayable(super_board[1, 1]):
                # print("Straighty could play center, center looks like this:\n ", super_board[1, 1])
                row, col = 1, 1
                local_row, local_col = self.randomMove(super_board[row, col])
                self.moveNumber += 1
                return row, col, local_row, local_col

            # Otherwise, Random Move
            for i in range(rows):
                for j in range(cols):
                    if isPlayable(super_board[i, j]):
                        # print(f"Straighty found a random playable board, the board is {i, j} and looks like this:\n {super_board[i, j]}, will attempt randomMove on it")
                        local_row, local_col = self.randomMove(super_board[i, j])
                        self.moveNumber += 1
                        return i, j, local_row, local_col
            
            raise ValueError(Style.BRIGHT + Fore.RED + f"Straighty couldn't find a playable board! Global Board is \n{super_board}" + Style.RESET_ALL)
            
        else:
            a, b = board_to_play
            subboard = super_board[a, b]
            if not isPlayable(subboard):
                raise ValueError(Style.BRIGHT + Fore.RED + f"Straighty Board to play is not playable! Board is \n{subboard}" + Style.RESET_ALL)

        # Greedy Action
        local_winner = self.get_winnableByOne(subboard)
        local_blocker = self.get_winnableByMinusOne(subboard)
        
        # print(f"When btp is {board_to_play}, Local winner is {local_winner}, local blocker is {local_blocker}")
 
        # Win
        if local_winner:
            # print("Straighty can win the given local board!")
            local_row, local_col = safeSetExtractor(super_board, local_winner)
        # Block
        elif local_blocker:
            # print("Straighty can block the given local board!")
            local_row, local_col = safeSetExtractor(super_board, local_blocker)
        # Straight Arrow
        elif canPlay(subboard, a, b):
            local_row, local_col = a, b
        # Random
        else:
            local_row, local_col = self.randomMove(subboard)
            
        self.moveNumber += 1
        return a, b, local_row, local_col

    def randomMove(self, board):
        empty_cells = np.flatnonzero(board == 0)
        chosen_index = random.choice(empty_cells)
        return np.unravel_index(chosen_index, board.shape)

    def globalBoardResulter(self, super_board):
        ''' Turns the global board into a 3x3 board with its results '''
        board = np.zeros((3, 3), dtype=int)
        board[0, 0] = isWon(super_board[0, 0])
        board[0, 1] = isWon(super_board[0, 1])
        board[0, 2] = isWon(super_board[0, 2])
        board[1, 0] = isWon(super_board[1, 0])
        board[1, 1] = isWon(super_board[1, 1])
        board[1, 2] = isWon(super_board[1, 2])
        board[2, 0] = isWon(super_board[2, 0])
        board[2, 1] = isWon(super_board[2, 1])
        board[2, 2] = isWon(super_board[2, 2])
        return board

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

    def get_winnableByOne(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_one.get(board_key, set())

    def get_winnableByMinusOne(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_minus_one.get(board_key, set())

def canPlay(subboard, row, col):
    ''' Returns True if the cell is empty, False otherwise '''
    return subboard[row, col] == 0

def isFull(subboard):
    ''' Returns True if the board is full, False otherwise '''
    return np.all(subboard != 0)

def isPlayable(subboard):
    ''' Returns True if the board is not full and not won, False otherwise '''
    return not isFull(subboard) and (isWon(subboard) == 0)

def isOver(subboard):
    ''' Returns True if the board is full or won, False otherwise '''
    return isFull(subboard) or (isWon(subboard) != 0)

def isWon(subboard):
    ''' Returns 0 if the board is not won, 1 if player 1 won, -1 if player -1 won '''
    rows, cols = subboard.shape

    # Check rows
    for i in range(rows):
        r1, r2, r3 = subboard[i, 0], subboard[i, 1], subboard[i, 2]
        if r1 == r2 == r3 and r1 != 0:
            return r1
    
    # Check columns
    for i in range(cols):
        c1, c2, c3 = subboard[0, i], subboard[1, i], subboard[2, i]
        if c1 == c2 == c3 and c1 != 0:
            return c1
    
    # Check Diagonals Descendent
    dd1, dd2, dd3 = subboard[0, 0], subboard[1, 1], subboard[2, 2]
    if dd1 == dd2 == dd3 and dd1 != 0:
        return dd1
    
    # Check Diagonals Ascendent
    da1, da2, da3 = subboard[0, 2], subboard[1, 1], subboard[2, 0]
    if da1 == da2 == da3 and da1 != 0:
        return da1
    
    return 0

def safeSetExtractor(board, set):
    ''' If there is a move from the set that doesn't lead to an over-subboard, returns it '''
    for move in set:
        if not isOver(board[move]):
            return move
    return set.pop()  # If all moves lead to an over-subboard, return any


# board_ex = np.zeros((3, 3, 3, 3), dtype=int)
# agent = StraightArrowAgent()

# move = agent.action(board_ex, board_to_play=None)