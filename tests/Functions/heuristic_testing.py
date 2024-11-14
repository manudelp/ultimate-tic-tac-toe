import numpy as np

def canPlay(board, i, j):
    return board[i, j] == 0

def fancyBoardPrinter(board):
    # Output the super board in a 3x3 layout
    for i in range(board.shape[0]):  # Iterate over rows of subboards
        for x in range(3):  # Each subboard has 3 rows
            row_output = ""
            for j in range(board.shape[1]):  # Iterate over columns of subboards
                row_output += " | ".join(map(str, board[i, j][x])) + "    "  # Join the rows of each subboard
            print(row_output)  # Print the row of the current level of subboards
        if i != 2:
            print()  # Print a separator between sets of subboard rows

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

board = np.zeros((3, 3, 3, 3), dtype=int)

# Board Changes
board[1, 1][1, 1] = -1
board[1, 1][0, 2] = -1
board[0, 2][1, 1] = -1
board[0, 2][0, 0] = -1
board[0, 2][2, 2] = -1
board[2, 2][1, 1] = -1
board[1, 1][1, 1] = -1
board[1, 1][0, 0] = -1

fancyBoardPrinter(board)

