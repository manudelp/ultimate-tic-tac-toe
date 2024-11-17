# The True Timer
import numpy as np
import time
import timeit
# from collections import defaultdict
# # Create a defaultdict with default value of None
# moves = defaultdict(lambda: None)

# region board generate
board_won_example1 = np.zeros((3, 3, 3, 3), dtype=int)
board_won_example2 = np.zeros((3, 3, 3, 3), dtype=int)
board_not_won_example1 = np.zeros((3, 3, 3, 3), dtype=int)
board_not_won_example2 = np.zeros((3, 3, 3, 3), dtype=int)
board_not_won_example3 = np.zeros((3, 3, 3, 3), dtype=int)

local_board_won_by_1 = np.array([
    [1, 1, 1],
    [-1, -1, 0],
    [0, 0, 0]
])

local_board_won_by_minus1 = np.array([
    [1, 1, -1],
    [1, -1, -1],
    [-1, 0, 1]
])

local_board_not_won = np.array([
    [1, 1, -1],
    [-1, -1, 1],
    [0, 0, 0]
])

local_board_not_won2 = np.array([
    [0, 1, 0],
    [0, 0, 0],
    [0, 0, 0]
])

local_board_not_won3 = np.array([
    [1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1]
])

# Set Won Boards
board_won_example1[0, 0] = local_board_won_by_1
board_won_example1[1, 1] = local_board_won_by_1
board_won_example1[2, 2] = local_board_won_by_1

board_won_example2[0, 0] = local_board_won_by_1
board_won_example2[0, 1] = local_board_not_won3
board_won_example2[0, 2] = local_board_won_by_1
board_won_example2[1, 0] = local_board_won_by_minus1
board_won_example2[1, 1] = local_board_won_by_minus1
board_won_example2[1, 2] = local_board_won_by_minus1
board_won_example2[2, 0] = local_board_not_won
board_won_example2[2, 1] = local_board_won_by_1
board_won_example2[2, 2] = local_board_not_won2

# Set Non-Won Boards
board_not_won_example1[0, 0] = local_board_won_by_1
board_not_won_example1[0, 1] = local_board_won_by_minus1
board_not_won_example1[0, 2] = local_board_not_won
board_not_won_example1[1, 0] = local_board_not_won2
board_not_won_example1[1, 1] = local_board_not_won3
board_not_won_example1[2, 2] = local_board_won_by_1

board_not_won_example2[0, 0] = local_board_won_by_1
board_not_won_example2[0, 1] = local_board_won_by_minus1
board_not_won_example2[0, 2] = local_board_won_by_minus1
board_not_won_example2[1, 0] = local_board_won_by_minus1
board_not_won_example2[1, 1] = local_board_won_by_1
board_not_won_example2[1, 2] = local_board_won_by_1
board_not_won_example2[2, 0] = local_board_won_by_1
board_not_won_example2[2, 1] = local_board_won_by_minus1
board_not_won_example2[2, 2] = local_board_won_by_minus1

b1w = board_won_example1
b2w = board_won_example2
b1nw = board_not_won_example1
b2nw = board_not_won_example2
b3nw = board_not_won_example3

lb1w = local_board_won_by_1
lb1nw = local_board_not_won
lb2nw = local_board_not_won2
lb3nw = local_board_not_won3
lbm1w = local_board_won_by_minus1
# endregion

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

def checkBoardWin(board):
    # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
    ''' Analyzes whether the global board has been won, by a player connecting 3 Won Local Boards 
    Returns 1 if Player 1 has won, -1 if Player -1 has won, None if no one has won '''
    
    # Row 0
    b_00, b_01, b_02 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[0, 2])
    if b_00 == b_01 == b_02 != None:
        return b_00
    
    # Row 1
    b_10, b_11, b_12 = isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[1, 2])
    if b_10 == b_11 == b_12 != None:
        return b_10
    
    b_20 = isWon(board[2, 0])
    # Save unncessary calcs, by using what we alreasy can

    # Column 0
    if b_00 == b_10 == b_20 != None:
        return b_00
    
    # Diagonal BT
    if b_20 == b_11 == b_02 != None:
        return b_20

    b_21 = isWon(board[2, 1]) 
    # again, save time

    # Check Column 1
    if b_01 == b_11 == b_21 != None:
        return b_01

    b_22 = isWon(board[2, 2])
    # Row 2
    if b_20 == b_21 == b_22 != None:
        return b_20

    # Column 2
    if b_02 == b_12 == b_22 != None:
        return b_02
    
    # Diagonal TB
    if b_00 == b_11 == b_22 != None:
        return b_00
    
    return 0

class foo_agent():
    def __init__(self):
            # Initiate Hashes
        self.hash_winning_boards = {}
        self.model_global_board_results = np.zeros((3, 3), dtype=int)

        # Load both winning boards and evaluated boards during initialization
        self.load_winning_boards('backend/agents/hashes/hash_winning_boards.txt')

        # 

    def updateModelGlobalResults(self, board):
        ''' Updates the model global results board '''
        self.model_global_board_results[0, 0] = self.get_isWon(board[0, 0])
        self.model_global_board_results[0, 1] = self.get_isWon(board[0, 1])
        self.model_global_board_results[0, 2] = self.get_isWon(board[0, 2])
        self.model_global_board_results[1, 0] = self.get_isWon(board[1, 0])
        self.model_global_board_results[1, 1] = self.get_isWon(board[1, 1])
        self.model_global_board_results[1, 2] = self.get_isWon(board[1, 2])
        self.model_global_board_results[2, 0] = self.get_isWon(board[2, 0])
        self.model_global_board_results[2, 1] = self.get_isWon(board[2, 1])
        self.model_global_board_results[2, 2] = self.get_isWon(board[2, 2])

    def getGlobalWinner(self, board):
        # TIMEIT APPROVED ✅
        ''' Returns the winner of the global board, if any '''
        results = np.array([[self.get_isWon(board[0, 0]), self.get_isWon(board[0, 1]), self.get_isWon(board[0, 2])],
                            [self.get_isWon(board[1, 0]), self.get_isWon(board[1, 1]), self.get_isWon(board[1, 2])],
                            [self.get_isWon(board[2, 0]), self.get_isWon(board[2, 1]), self.get_isWon(board[2, 2])]])
        
        return self.get_isWon(results)

    def getGlobalWinner_v2(self, board):
        results = np.ndarray((3, 3), dtype=int)
        results[0, 0] = self.get_isWon(board[0, 0])
        results[0, 1] = self.get_isWon(board[0, 1])
        results[0, 2] = self.get_isWon(board[0, 2])
        results[1, 0] = self.get_isWon(board[1, 0])
        results[1, 1] = self.get_isWon(board[1, 1])
        results[1, 2] = self.get_isWon(board[1, 2])
        results[2, 0] = self.get_isWon(board[2, 0])
        results[2, 1] = self.get_isWon(board[2, 1])
        results[2, 2] = self.get_isWon(board[2, 2])

        return self.get_isWon(results)

    def checkBoardWinner(self, board):
        # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
        ''' Analyzes whether the global board has been won, by a player connecting 3 Won Local Boards 
        Returns 1 if Player 1 has won, -1 if Player -1 has won, None if no one has won '''
        
        # Row 0
        b_00, b_01, b_02 = self.get_isWon(board[0, 0]), self.get_isWon(board[0, 1]), self.get_isWon(board[0, 2])
        if b_00 == b_01 == b_02 != 0:
            return b_00
        
        # Row 1
        b_10, b_11, b_12 = self.get_isWon(board[1, 0]), self.get_isWon(board[1, 1]), self.get_isWon(board[1, 2])
        if b_10 == b_11 == b_12 != 0:
            return b_10
        
        b_20 = self.get_isWon(board[2, 0])
        # Save unncessary calcs, by using what we alreasy can

        # Column 0
        if b_00 == b_10 == b_20 != 0:
            return b_00
        
        # Diagonal BT
        if b_20 == b_11 == b_02 != 0:
            return b_20

        b_21 = self.get_isWon(board[2, 1]) 
        # again, save time

        # Check Column 1
        if b_01 == b_11 == b_21 != 0:
            return b_01

        b_22 = self.get_isWon(board[2, 2])
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

    def get_isWon(self, board):
        # TIMEIT APPROVED ✅
        """
        Retrieve the winner of a board from the preloaded dictionary of winning boards.
        Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
        """
        board_key = board.tobytes()
        return self.hash_winning_boards.get(board_key, 0)

    def load_winning_boards(self, file_path):
        # TIMEIT APPROVED ✅
        """
        Load the winning boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with the winner (1 or -1) as its value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, winner = line.strip().split(':')
                    self.hash_winning_boards[bytes.fromhex(board_hex)] = int(winner)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

agent = foo_agent()
agent.updateModelGlobalResults(b1w)

def test_getGlobalWinner():
    winnerB1 = agent.getGlobalWinner(b1w)
    winnerB2 = agent.getGlobalWinner(b2w)
    winnerB1nw = agent.getGlobalWinner(b1nw)
    winnerB2nw = agent.getGlobalWinner(b2nw)
    winnerB3nw = agent.getGlobalWinner(b3nw)

    assert winnerB1 == 1
    assert winnerB2 == -1
    assert winnerB1nw == 0
    assert winnerB2nw == 0
    assert winnerB3nw == 0

    print("getGlobalWinner PASSED")

def test_checkBoardWinner():
    winnerB1 = agent.checkBoardWinner(b1w)
    winnerB2 = agent.checkBoardWinner(b2w)
    winnerB1nw = agent.checkBoardWinner(b1nw)
    winnerB2nw = agent.checkBoardWinner(b2nw)
    winnerB3nw = agent.checkBoardWinner(b3nw)

    assert winnerB1 == 1
    assert winnerB2 == -1
    assert winnerB1nw == 0
    assert winnerB2nw == 0
    assert winnerB3nw == 0

    print("checkBoardWinner PASSED")

# Run tests
# test_getGlobalWinner()
# test_checkBoardWinner() 

boards_list = [b1w, b2w, b1nw, b2nw, b3nw]

iters = 1_000_000
time_getGlobal_v2 = 0
time_checkBoard = 0
time_resultsHash = 0
total_iters = iters * len(boards_list)

for i, board in enumerate(boards_list):
    agent.updateModelGlobalResults(board)

    time_getGlobal_v2_aux = timeit.timeit(lambda: agent.getGlobalWinner_v2(board), number=iters)
    time_checkBoard_aux = timeit.timeit(lambda: agent.checkBoardWinner(board), number=iters)
    time_resultsHash_aux = timeit.timeit(lambda: agent.get_isWon(agent.model_global_board_results), number=iters)

    if agent.getGlobalWinner(board) != agent.checkBoardWinner(board):
        raise ValueError(f"Error at {i}! getGlobal and checkBoard are different")

    if agent.get_isWon(agent.model_global_board_results) != agent.getGlobalWinner(board):
        raise ValueError(f"Error at {i}! results_hash_win and getGlobalWinner are different")
    
    if agent.getGlobalWinner(board) != agent.getGlobalWinner_v2(board):
        raise ValueError(f"Error at {i}! getGlobalWinner and getGlobalWinner_v2 are different")

    if agent.get_isWon(agent.model_global_board_results) != agent.checkBoardWinner(board):
        raise ValueError(f"Error at {i}! results_hash_win and checkBoardWinner are different")

    # print(f"traditional at {i} is: {time_traditional_aux}")
    # print(f"getGlobalWinner at {i} is: {time_getGlobal_aux}")
    # print(f"checkBoardWinner at {i} is: {time_checkBoard_aux}")
    # print(f"results_hash_win at {i} is: {time_resultsHash_aux}")

    time_getGlobal_v2 += time_getGlobal_v2_aux
    time_checkBoard += time_checkBoard_aux
    time_resultsHash += time_resultsHash_aux

print(f"All Tests Passed Successfully for all Functions! \n")

print(f"Time Results after {total_iters} iterations")

print(f"Total Time for getGlobalWinner_v2: {time_getGlobal_v2} seconds")
print(f"Total Time for checkBoardWinner: {time_checkBoard} seconds")
print(f"Total Time for results_hash_win: {time_resultsHash} seconds")
