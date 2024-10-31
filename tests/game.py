'''
This is just for testing the game in a local file board con updates de jugadas escritas linea por linea 
Para ver que anden bien los agentes nomas, https://youtu.be/8RtOgIgDrvk?si=xlR1YV_9obo2DmeE
'''

import numpy as np

from ..backend.agents.foofinder import FooFighterAgent
from ..backend.agents.bot.randy import RandomAgent
from ..backend.agents.bot.monkey import MonkeyAgent
from ..backend.agents.bot.greedy import GreedyAgent
from ..backend.agents.bot.straightArrow import StraightArrowAgent

# Create an empty superboard: a 3x3 grid of 3x3 boards, initialized to 0
board = np.zeros((3, 3, 3, 3), dtype=int)  # Shape is (3, 3, 3, 3)

np.random.seed(435)

def boardPrinter(board):
    for i in range(board.shape[0]):  # Iterate over rows of subboards
        for x in range(3):  # Each subboard has 3 rows
            row_output = ""
            for j in range(board.shape[1]):  # Iterate over columns of subboards
                row_output += np.array2string(board[i, j][x], separator=' ') + "   "  # Print rows of each subboard
            print(row_output)  # Print the row of the current level of subboards
        if i != 2:
            print()  # Print an empty line to separate each set of subboard rows

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

# Example 3x3 grid of 3x3 boards
board = np.zeros((3, 3, 3, 3), dtype=int)

# Create Agent Instances
foofighter = FooFighterAgent()
randy = RandomAgent()
monkey = MonkeyAgent()
greedy = GreedyAgent()
straightArrow = StraightArrowAgent()

# Refactor code
def thisOrRnd(board, c_p, d_p, a: int, b: int):
    aux = 0
    while board[c_p, d_p][a, b] != 0:
        a, b = np.random.randint(3), np.random.randint(3)
        aux+=1
        if aux > 1000:
            boardPrinter(board)
            raise Exception(f"I'm stuck! At board {c_p, d_p}")
    return a, b

def myMove(board, moveX, moveY, board_to_play, move_num):
    if board_to_play is None:
        raise ValueError("I cant choose my own boards!!!")
    else:
        print(f"I, Myself, should play in the {board_to_play} board")

    a_m, b_m = board_to_play
    c_m, d_m = moveX, moveY

    print(f"My move number {move_num} is {a_m, b_m, c_m, d_m} \n")
    board[a_m, b_m][c_m, d_m] = -1
    return c_m, d_m

def randyMove(board, board_to_play, move_num):
    if board_to_play is None:
        print(f"I, Randy, should play in any board")
    else:
        print(f"I, Randy, should play in the {board_to_play} board")

    a_r, b_r, c_r, d_r = randy.action(board, board_to_play)
    print(f"Randy's move number {move_num} is {a_r, b_r, c_r, d_r} \n")
    board[a_r, b_r][c_r, d_r] = 1
    return c_r, d_r

# Play!


# region Random

# Random Move 1
c_r, d_r = randyMove(board, board_to_play=None, move_num=1)

# My Move 1
a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=1)

# Random Move 2
c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=2)

# My Move 2
a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=2)

# Random Move 3
c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=3)

# My Move 3
a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=3)

# Random Move 4
c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=4)

# My Move 4
a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=4)

# Random Move 5
c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=5)

# My Move 5
a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=5)

# Random Move 6
c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=6)

# My Move 6
a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=6)

# Simulate 30 more moves for each
# for i in range(7, 37):
#     # Random Move
#     c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=i)

#     # My Move
#     a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
#     c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=i)

# endregion


# region Greedy

# Greedy Move 1

# endregion


# Print Final Board
print(board)
# boardPrinter(board)
# fancyBoardPrinter(board)

print(f"\nThe board has a total amount of {np.sum(board == 1)} ones and {np.sum(board == -1)} minus ones")