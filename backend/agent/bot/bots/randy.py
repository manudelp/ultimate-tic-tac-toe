import random
import numpy as np
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional


def isFull(board):
    ''' Returns True if the board is full, False otherwise '''
    return np.count_nonzero(board == 0) == 0

def isWon(local_board):
    ''' Returns None if the board is not won, 1 if player 1 won, -1 if player -1 won '''
    rows, cols = local_board.shape
    # Check rows
    for i in range(rows):
        r1, r2, r3 = local_board[i, 0], local_board[i, 1], local_board[i, 2]
        if r1 == r2 == r3 and r1 != 0:
            return r1
    # Check columns
    for i in range(cols):
        c1, c2, c3 = local_board[0, i], local_board[1, i], local_board[2, i]
        if c1 == c2 == c3 and c1 != 0:
            return c1
    # Check diagonals
    if local_board[0, 0] == local_board[1, 1] == local_board[2, 2] != 0:
        return local_board[0, 0]
    if local_board[0, 2] == local_board[1, 1] == local_board[2, 0] != 0:
        return local_board[0, 2]
    return None

class RandomAgent:
    def __init__(self):
        self.id = 0
        self.name = "Randy"
        self.icon = "🎲"
        self.description = "Randy is a wild card! He plays like he's throwing darts blindfolded. Don't expect strategy, just chaos and fun!" 
        self.difficulty = 1
        
        # Temporary to not break
        # self.load()

    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def reset(self):
        # print(f"randy been reset, his move number has GONE DOWN TO ZEROOOOO")
        self.moveNumber = 0

    def load(self):
        ''' Loads all the class elements and hashes for the agent to be ready for a game or set of games 
        To be called at most at the start of every game, ideally at the start of every set of games so as to not waste much time '''
        
        print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"Loading {self.name}..." + Style.RESET_ALL)
        
        self.moveNumber = 0
        self.loaded_up = True

    def action(self, board, board_to_play=None):
        board = np.array(board, dtype=int)
        # print(Style.BRIGHT + Fore.MAGENTA + f"{self.name} move number is {self.moveNumber}, the board_to_play he got is {board_to_play},\nthe board he received is \n{board}" + Style.RESET_ALL)

        self.global_row, self.global_col = None, None
        
        # Make Playable Local Boards List
        if board_to_play is None:
            playable_boards = self.get_playable_boards_list(board)
            
            if (len(playable_boards) == 0) or (not playable_boards):
                raise ValueError(Style.BRIGHT + Fore.RED + f"Randy couldn't find a playable board! Global Board is \n{board}" + Style.RESET_ALL)

            i, j = random.choice(playable_boards)
            # print(f"Randy found a playable board, the board is {i, j} and looks like this: {board[i, j]}, will attempt randomMove on it")

            local_row, local_col = self.randomMove(board[i, j])
            self.global_row, self.global_col = i, j
            self.moveNumber += 1
            return self.global_row, self.global_col, local_row, local_col
        else:   
            self.global_row, self.global_col = board_to_play
            local_board = board[self.global_row, self.global_col]
            if not isPlayable(local_board):
                raise ValueError(Style.BRIGHT + Fore.RED + f"Randy Board to play is not playable! Board is \n{local_board}\nIs Board Full? {isFull(local_board)}\nIs Board Won? {isWon(local_board)}" + Style.RESET_ALL)

        if self.global_row is None or self.global_col is None:
            raise ValueError(f"global_row or global_col is None! Board to play was {board_to_play}")

        local_board = board[self.global_row, self.global_col]
        # print(f"I randy will attempt randomMove on the local_board: {self.global_row, self.global_col}")
        c, d = self.randomMove(local_board)
        self.moveNumber += 1
        return self.global_row, self.global_col, c, d

    def randomMove(self, board):
        if isFull(board):
            raise ValueError(f"The board is full while board is {board}")
        empty_cells = np.flatnonzero(board == 0)
        if empty_cells.size == 0:
            raise ValueError(f"The board is full... it shouldn't even be, even with a jsx fail, I already checked\n Board is {board}")
        chosen_index = random.choice(empty_cells)
        return np.unravel_index(chosen_index, board.shape)
    
    def get_playable_boards_list(self, board):
        playables = []
        for i in range(3):
            for j in range(3):
                if isPlayable(board[i, j]):
                    playables.append((i, j))
        return playables

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
        if r1 == r2 == r3 and r1 != 0 and r1 != 2:
            return r1
    
    # Check columns
    for i in range(cols):
        c1, c2, c3 = subboard[0, i], subboard[1, i], subboard[2, i]
        if c1 == c2 == c3 and c1 != 0 and c1 != 2:
            return c1
    
    # Check Diagonals Descendent
    dd1, dd2, dd3 = subboard[0, 0], subboard[1, 1], subboard[2, 2]
    if dd1 == dd2 == dd3 and dd1 != 0 and dd1 != 2:
        return dd1
    
    # Check Diagonals Ascendent
    da1, da2, da3 = subboard[0, 2], subboard[1, 1], subboard[2, 0]
    if da1 == da2 == da3 and da1 != 0 and da1 != 2:
        return da1
    
    return 0
