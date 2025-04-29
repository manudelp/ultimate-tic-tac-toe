import numpy as np
import random
import os
import time
from typing import Union, Tuple
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

"""
depth = iterative_deepening
Board Balance = Sum of Local Board Balances
AB-Pruning Minimax? = True

"""

class HashmasterAgent:
    def __init__(self):
        self.name = "Hashmaster"
        self.icon = "📖"
        self.moveNumber = 0
        # self.depth = 6
        self.time_limit = 20 # in seconds
        self.total_minimax_time = 0
        self.minimax_plays = 0
        self.hash_over_boards = {}
        self.hash_eval_boards = {}
        self.hash_boards_information = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Construct the absolute paths to the files
        alpha_numeric_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_AlphaNumeric_boards.txt')

        # Load the boards using the absolute paths
        self.load_AlphaNumeric_boards(alpha_numeric_boards_path)

    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def reset(self):
        if self.moveNumber == 0 and self.minimax_plays == 0 and self.total_minimax_time == 0:
            print(f"First Game, pointless Reset for {self.name}")
            # return
        # if self.minimax_plays == 0:
            # raise ValueError(Style.BRIGHT + Fore.RED + "Reset has been called, it's not the first game but minimax_plays is 0..." + Style.RESET_ALL)
        # average_minimax_time = self.total_minimax_time / self.minimax_plays
        # print(Style.BRIGHT + Fore.MAGENTA + f"\n{self.name} played Minimax {self.minimax_plays} times with an average time of {average_minimax_time:.4f} seconds" + Style.RESET_ALL)
        self.moveNumber = 0
        self.minimax_plays = 0
        self.total_minimax_time = 0

    def action(self, board, board_to_play=None):
        self.start_time = time.time()
        print(f"{self.name} begins action, move number to play: {self.moveNumber}")

        board = np.array(board, dtype=int)
        rows, cols, *_ = board.shape
        global_board_copy = board.copy()

        self.updateOverBoards(board)
        self.updatePlayableBoards(board)

        self.model_over_boards_set = self.over_boards_set.copy()
        self.model_playable_boards_set = self.playable_boards_set.copy()

        # Play Center if first move
        if isEmpty(board):
            self.moveNumber += 1
            return 1, 1, 1, 1

        # Minimax

        if board_to_play is None:
            moves_to_try = self.generate_global_moves(board)

            t_before_order = time.time()
            # TODO: Order Moves in action, test if Phase 1 time gets better or worse
            # unordered_moves = self.generate_global_moves(board)
            # moves_to_try = self.order_moves(board, unordered_moves)
            print(f"Ordering moves for Monkey when btp was None took {time.time() - t_before_order:.4f} seconds")

            # Call Iterative Deepening
            best_move = self.iterative_deepening(board, board_to_play, moves_to_try)

            if best_move is None:
                raise ValueError("Iterative Deepening Failed! Board to play was None!")
            
            global_row, global_col, local_row, local_col = best_move

        else:
            global_row, global_col = board_to_play
            moves_to_try = self.generate_local_moves(board[global_row, global_col])

            t_before_order = time.time()
            # TODO: Order moves in Action, test if Phase 1 time gets better or worse
            # unordered_moves = self.generate_local_moves(board[global_row, global_col])
            # moves_to_try = self.order_moves(board[global_row, global_col], unordered_moves)
            print(f"Ordering moves for Monkey when btp was not None took {time.time() - t_before_order:.4f} seconds")

            # Call Iterative Deepening
            best_move = self.iterative_deepening(board, board_to_play, moves_to_try)

            if best_move is None:
                raise ValueError("Iterative Deepening Failed! Board to play was not None!")
            
            local_row, local_col = best_move

        if global_row is None or global_col is None or local_row is None or local_col is None:
            raise ValueError("Best Move was None! This is being printed at the end of action, after running the minimax...")

        self.moveNumber += 1
        minimax_time = time.time() - self.start_time
        print(Style.BRIGHT + Fore.CYAN + f"{self.name} took {minimax_time:.4f} seconds to play alpha beta with depth {self.depth_global}, btp was {board_to_play}" + Style.RESET_ALL)
        self.minimax_plays += 1
        self.total_minimax_time += minimax_time
        return global_row, global_col, local_row, local_col

    def load_AlphaNumeric_boards(self, path):
        with open(path, 'r') as f:
            for line in f:
                board, value = line.strip().split(':')
                self.hash_eval_boards[board] = int(value)


def canPlay(board, i, j):
    return board[i, j] == 0

def isEmpty(board):
    return np.count_nonzero(board) == 0

def isFull(board):
    ''' Returns True if the board is full, False otherwise '''
    return np.count_nonzero(board == 0) == 0

def isPlayable(subboard):
    ''' Returns True if the board is not full and not won, False otherwise '''
    return not isFull(subboard) and (isWon(subboard) is None)

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
    
    return 0

def checkBoardWinner(board):
    # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
    ''' Analyzes whether the global board has been won, by a player connecting 3 Won Local Boards 
    Returns 1 if Player 1 has won, -1 if Player -1 has won, None if no one has won '''
    
    # Row 0
    b_00, b_01, b_02 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[0, 2])
    if b_00 == b_01 == b_02 != 0:
        return b_00
    
    # Row 1
    b_10, b_11, b_12 = isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[1, 2])
    if b_10 == b_11 == b_12 != 0:
        return b_10
    
    b_20 = isWon(board[2, 0])
    # Save unncessary calcs, by using what we alreasy can

    # Column 0
    if b_00 == b_10 == b_20 != 0:
        return b_00
    
    # Diagonal BT
    if b_20 == b_11 == b_02 != 0:
        return b_20

    b_21 = isWon(board[2, 1]) 
    # again, save time

    # Check Column 1
    if b_01 == b_11 == b_21 != 0:
        return b_01

    b_22 = isWon(board[2, 2])
    # Row 2
    if b_20 == b_21 == b_22 != 0:
        return b_20

    # Column 2
    if b_02 == b_12 == b_22 != 0:
        return b_02
    
    # Diagonal TB
    if b_00 == b_11 == b_22 != 0:
        return b_00
    
    return 0

def playerHasWon(board, player):
    return player == checkBoardWinner(board)

def isWinnable(subboard, player):
    ''' If the player can win in the next move, returns a Tuple with the subboard coordinates for the win
    Returns None otherwise '''
    rows, cols = subboard.shape
    board = subboard.copy()

    for i in range(rows):
        for j in range(cols):
            if board[i, j] == 0:
                board[i, j] = player
                if isWon(board) == player:
                    return (i, j)
                board[i, j] = 0
    return None
