'''
This is just for testing the game in a local file board con updates de jugadas escritas linea por linea 
Para ver que anden bien los agentes nomas, https://youtu.be/8RtOgIgDrvk?si=xlR1YV_9obo2DmeE
'''

import numpy as np



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

def isWon(subboard):
    # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
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

def isFull(board):
    return np.count_nonzero(board == 0) == 0

def isPlayable(board):
    ''' Returns True if the local 3x3 board is still playable '''
    return not isFull(board) and not isWon(board)

def isWonByPlayer(board, player):
    """ Returns True if the specified player has won the board, otherwise False. """
    return (
        (board[0, 0] == board[0, 1] == board[0, 2] == player) or  # Row 1
        (board[1, 0] == board[1, 1] == board[1, 2] == player) or  # Row 2
        (board[2, 0] == board[2, 1] == board[2, 2] == player) or  # Row 3
        (board[0, 0] == board[1, 0] == board[2, 0] == player) or  # Column 1
        (board[0, 1] == board[1, 1] == board[2, 1] == player) or  # Column 2
        (board[0, 2] == board[1, 2] == board[2, 2] == player) or  # Column 3
        (board[0, 0] == board[1, 1] == board[2, 2] == player) or  # Diagonal Top-Left to Bottom-Right
        (board[0, 2] == board[1, 1] == board[2, 0] == player)     # Diagonal Top-Right to Bottom-Left
    )

def isWonByOne(board):
    """ Returns True if player 1 has won the board, False otherwise """
    return isWonByPlayer(board, player=1)

def isWonByMinusOne(board):
    """ Returns True if player -1 has won the board, False otherwise """
    return isWonByPlayer(board, player=-1)

def isLegal(board):
    return not (isWonByOne(board) and isWonByMinusOne(board))


# from agent_tests.hash_retrieval_tests import RetrievalAgent
# agent = RetrievalAgent()
# print("\n")

# Play!

# # region Random

# # Random Move 1
# c_r, d_r = randyMove(board, board_to_play=None, move_num=1)

# # My Move 1
# a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=1)

# # Random Move 2
# c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=2)

# # My Move 2
# a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=2)

# # Random Move 3
# c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=3)

# # My Move 3
# a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=3)

# # Random Move 4
# c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=4)

# # My Move 4
# a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=4)

# # Random Move 5
# c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=5)

# # My Move 5
# a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=5)

# # Random Move 6
# c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=6)

# # My Move 6
# a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=6)

# # Simulate 30 more moves for each
# # for i in range(7, 37):
# #     # Random Move
# #     c_r, d_r = randyMove(board, board_to_play=(c_m, d_m), move_num=i)

# #     # My Move
# #     a, b = thisOrRnd(board, c_r, d_r, a=1, b=1)
# #     c_m, d_m = myMove(board, moveX=a, moveY=b, board_to_play=(c_r, d_r), move_num=i)

# # endregion

# # Print Final Board
# print(board)
# # boardPrinter(board)
# # fancyBoardPrinter(board)

# print(f"\nThe board has a total amount of {np.sum(board == 1)} ones and {np.sum(board == -1)} minus ones")

# for s in range(300_000_000):
#     if s % 10_000_000 == 0:
#         print(f"Currently at Seed {s}...")
    
#     np.random.seed(s)
#     board = np.random.randint(-1, 2, (3, 3, 3, 3))
    
#     still_playable_list = []
#     playable_tiles = 0
#     found_illegal = False  # Flag to track if an illegal board is found
    
#     for r in range(3):
#         for c in range(3):
#             # if isIllegal(board[r, c]):
#             #     found_illegal = True
#             #     break  # Exit the inner loop
#             if agent.get_playable_hash(board[r, c]):
#                 still_playable_list.append((r, c))
#                 playable_tiles += np.count_nonzero(board[r, c] == 0)
        
#         if found_illegal:
#             break  # Exit the outer loop if an illegal board was found
    
#     if found_illegal:
#         # print(f"Seed {s} has an illegal configuration. Skipping...\n")
#         continue  # Skip to the next seed if any part of the board was illegal
    
#     if playable_tiles > 49:
#         print(f"While Seed is {s}, playables list is {still_playable_list}, playable tiles are {playable_tiles}")
#         # fancyBoardPrinter(board)
#     # print("\n")

# Seed 23843005, playables list is [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)], playable tiles are 53

np.random.seed(23843005)

board = np.random.randint(-1, 2, (3, 3, 3, 3))

fancyBoardPrinter(board)