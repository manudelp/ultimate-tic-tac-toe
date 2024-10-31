import numpy as np
import random

"""
If it can make a subboard win, it plays it. 
# (not done yet) If it can block a subboard win, it blocks it
Otherwise plays randy
"""

def canPlay(subboard, row, col):
    ''' Returns True if the cell is empty, False otherwise '''
    return subboard[row, col] == 0

def isFull(subboard):
    ''' Returns True if the board is full, False otherwise '''
    return np.all(subboard != 0)

def isWon(subboard):
    ''' Returns None if the board is not won, 1 if player 1 won, -1 if player -1 won '''
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
    # Check diagonals
    if subboard[0, 0] == subboard[1, 1] == subboard[2, 2] != 0:
        return subboard[0, 0]
    if subboard[0, 2] == subboard[1, 1] == subboard[2, 0] != 0:
        return subboard[0, 2]
    return None

def isPlayable(subboard):
    ''' Returns True if the board is not full and not won, False otherwise '''
    return not isFull(subboard) and (isWon(subboard) is None)

def isWon(subboard):
    ''' Returns None if the board is not won, 1 if player 1 won, -1 if player -1 won '''
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
    
    return None

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

class StraightArrowAgent:
    def __init__(self):
        self.id = "Straighty 🏹"
        self.moveNumber = 0
    
    def __str__(self):
        return self.id

    def reset(self):
        self.moveNumber = 0

    def action(self, super_board, board_to_play=None):
        super_board = np.array(super_board, dtype=int)
        rows, cols, *_ = super_board.shape
        print(f"Move number is {self.moveNumber}")

        # First Move Go Center
        if np.count_nonzero(super_board) == 0:
            if self.moveNumber != 0:
                raise ValueError("No one has played, but moveNumber is not 0")
            self.moveNumber += 1
            return 1, 1, 1, 1

        if board_to_play is None:
    
            
            # # Old Greedy Selection before Hash
            # for i in range(rows):
            #     for j in range(cols):

            #         canWin = isWinnable(super_board[i, j], 1)
            #         if isPlayable(super_board[i, j]) and (canWin is not None):
            #             self.moveNumber += 1
            #             return i, j, canWin[0], canWin[1]
                    
            #         enemyWin = isWinnable(super_board[i, j], -1)
            #         if isPlayable(super_board[i, j]) and (enemyWin is not None):
            #             self.moveNumber += 1
            #             return i, j, enemyWin[0], enemyWin[1]

            # If Failed, return to Randy Selection
            a_aux, b_aux = random.randint(0, 2), random.randint(0, 2)
            aux = 0
            while not isPlayable(super_board[a_aux, b_aux]):
                a_aux, b_aux = random.randint(0, 2), random.randint(0, 2)
                aux += 1
                if aux > 1000:
                    for i in range(15):
                        print(f"STRAIGHTY RANDOM GEN FAIL! Here's Local Board example: {random.randint(0, 2), random.randint(0, 2)}")
                    raise ValueError(f"Straighty ya itero *1000* VECES buscando board to play, y no encontro ninguno, arriba deje 15 ejemplos \n While Board is {super_board}")
            a, b = a_aux, b_aux
            
        else:   
            a, b = board_to_play
        subboard = super_board[a, b]

        # # Old Greedy Action before Hash
        # myWin = isWinnable(subboard, 1)
        # enemyWin = isWinnable(subboard, -1)

        # if myWin is not None:
        #     self.moveNumber += 1
        #     return a, b, myWin[0], myWin[1]
        # if enemyWin is not None:
        #     self.moveNumber += 1
        #     return a, b, enemyWin[0], enemyWin[1]

        # else, tries straighty action
        if canPlay(subboard, a, b):
            self.moveNumber += 1
            return a, b, a, b

        # Else, Does Randy Action
        c, d = self.randomMove(subboard)
        self.moveNumber += 1
        return a, b, c, d

    def randomMove(self, board):
        empty_cells = np.flatnonzero(board == 0)
        chosen_index = random.choice(empty_cells)
        return np.unravel_index(chosen_index, board.shape)


