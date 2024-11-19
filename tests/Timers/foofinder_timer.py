import numpy as np
import timeit
import time

# Setup: Create a large random array and precompute all indices
board = np.random.randint(-1, 2, size=(3, 3, 3, 3))  # Large array with 0s and 1s

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

def boardToTuple(board):
    # TIMEIT APPROVED ✅
    if not isinstance(board, np.ndarray):
        raise ValueError("Board being turned to Tuple is not a numpy array!")
    return tuple(map(tuple, board))

def boardToHash(board):
    # TIMEIT APPROVED ✅
    ''' Returns the board as bytes for hashing '''
    return board.tobytes()

class FooFinderAgent:
    def __init__(self):
        # Class Elements
        self.name = "Foo Finder 👑"
        self.moveNumber = 0
        self.abortedTimes = 0
        self.foo_pieces = 0
        self.rival_pieces = 0
        self.finishedBoards = []
        self.nonFinishedBoards = []
        self.modelFinishedBoards = []
        self.modelNonFinishedBoards = []
        self.wonBoards = {}
        self.modelWonBoards = {}
        self.board_array = None
        self.board_tuple = None
        self.time_limit = 8 # Seconds

        # Initiate Hashes
        self.hash_winning_boards = {}
        self.hash_eval_boards = {}
        self.hash_draw_boards = {}
        self.hash_move_boards = {}

        # Load both winning boards and evaluated boards during initialization
        # self.load_winning_boards('backend/agents/hashes/hash_winning_boards.txt')
        # self.load_evaluated_boards('backend/agents/hashes/hash_evaluated_boards.txt')
        # self.load_drawn_boards('backend/agents/hashes/hash_draw_boards.txt')
        # self.load_move_boards('backend/agents/hashes/hash_move_boards.txt')

    def reset(self):
        self.moveNumber = 0
        self.abortedTimes = 0
        self.foo_pieces = 0
        self.rival_pieces = 0
        self.boardToPlay = None
        self.lastOpponentMove = None
        self.finishedBoards = []
        self.nonFinishedBoards = []
        self.modelFinishedBoards = []
        self.modelNonFinishedBoards = []
        self.wonBoards = {}
        self.modelWonBoards = {}
        self.board_array = None
        self.board_tuple = None
        self.hash_winning_boards = {}
        self.hash_eval_boards = {}
        self.hash_draw_boards = {}
        self.hash_move_boards = {}

    def __str__(self):
        return self.name

    def action(self, board, board_to_play=None):
        '''
        Gets called in the game to determine the Agent Action
        All calls of agent functions & utilities root to this function

        Args:
            board_input (np_array): Current state of the board, in a 4d numpy array of dimension 3x3x3x3

            board_to_play (tuple, optional): Coordinates of the board the agent has to play in, based on opponent last move. 
            Defaults to None (if any local board can be chosen).

        Returns:
            Tuple: Coordinates of the move to be played in the global board, of size 4
        '''

        # Time Start
        self.start_time = time.time()

        # Smart-Board Transformations
        self.board_array = board.copy()
        self.board_tuple = boardToTuple(board)
        self.board_bytes = boardToHash(board)

        # Board Info Class Elements
        self.updateFinishedBoards(board)
        self.updateWonBoards(board)
        
        self.modelNonFinishedBoards = self.nonFinishedBoards.copy()
        self.modelFinishedBoards = self.finishedBoards.copy()
        self.modelWonBoards = self.wonBoards.copy()

        self.foo_pieces = np.count_nonzero(board == 1)
        self.rival_pieces = np.count_nonzero(board == -1)

        # Ensure it's 3x3
        rows, cols, subrows, subcols = board.shape
        if rows != 3 or cols != 3 or subrows != 3 or subcols != 3:
            raise ValueError("Invalid Board Shape: El tablero no esta siendo un 3x3x3x3")

    def isPlayable(self, board):
        return (isWon(board) is None) and (np.count_nonzero(board==0) > 0)

    def updateFinishedBoards(self, board):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once per action)
        """Updates class elements of finished and non-finished boards."""
        rows, cols, *_ = board.shape

        for i in range(rows):
            for j in range(cols):
                subboard = board[i, j]
                if self.isPlayable(subboard):
                    # Add to nonFinishedBoards if it's playable and not already present
                    if not any(np.array_equal(subboard, existing_board) for existing_board in self.nonFinishedBoards):
                        self.nonFinishedBoards.append(subboard)
                else:
                    # Add to finishedBoards if it's not playable and not already present
                    if not any(np.array_equal(subboard, existing_board) for existing_board in self.finishedBoards):
                        self.finishedBoards.append(subboard)

    def updateModelFinishedBoards(self, board):
        # NEEDS TIME IMPROVEMENT 🚨 (apply hashing)
        ''' Updates class elements of modelFinished and modelNonFinished boards '''
        b00, b01, b10, b11, b20, b21, b02, b12, b22 = board[0, 0], board[0, 1], board[1, 0], board[1, 1], board[2, 0], board[2, 1], board[0, 2], board[1, 2], board[2, 2]
        
        if self.isPlayable(b00):
            if not any(np.array_equal(b00, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b00)
        else:
            if not any(np.array_equal(b00, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b00)
        
        if self.isPlayable(b01):
            if not any(np.array_equal(b01, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b01)
        else:
            if not any(np.array_equal(b01, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b01)

        if self.isPlayable(b02):
            if not any(np.array_equal(b02, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b02)
        else:
            if not any(np.array_equal(b02, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b02)

        if self.isPlayable(b10):
            if not any(np.array_equal(b10, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b10)
        else:
            if not any(np.array_equal(b10, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b10)

        if self.isPlayable(b11):
            if not any(np.array_equal(b11, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b11)
        else:
            if not any(np.array_equal(b11, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b11)

        if self.isPlayable(b12):
            if not any(np.array_equal(b12, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b12)
        else:
            if not any(np.array_equal(b12, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b12)

        if self.isPlayable(b20):
            if not any(np.array_equal(b20, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b20)
        else:
            if not any(np.array_equal(b20, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b20)

        if self.isPlayable(b21):
            if not any(np.array_equal(b21, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b21)
        else:
            if not any(np.array_equal(b21, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b21)

        if self.isPlayable(b22):
            if not any(np.array_equal(b22, existing_board) for existing_board in self.modelNonFinishedBoards):
                self.modelNonFinishedBoards.append(b22)
        else:
            if not any(np.array_equal(b22, existing_board) for existing_board in self.modelFinishedBoards):
                self.modelFinishedBoards.append(b22)

    def addFinishedBoard(self, board):
        # TIMEIT APPROVED ✅
        ''' Changes the Board location in the modelBoards lists, adding it to Finished, and removing it from Non-Finished '''
        self.modelFinishedBoards.append(board)
        self.modelNonFinishedBoards.remove(board)
    
    def addNonFinishedBoard(self, board):
        # TIMEIT APPROVED ✅
        ''' Changes the Board location in the modelBoards lists, adding it to Non-Finished, and removing it from Finished '''
        self.modelNonFinishedBoards.append(board)
        self.modelFinishedBoards.remove(board)

    def updateWonBoards(self, board):
        # TIMEIT ACCEPTED ☑️ not relevant enough to be time-improved, it's just called once per action
        ''' Updates the WonBoards class dictionary '''
        b00, b01, b10, b11, b20, b21, b02, b12, b22 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[2, 0]), isWon(board[2, 1]), isWon(board[0, 2]), isWon(board[1, 2]), isWon(board[2, 2])
        
        if b00 is not None:
            self.wonBoards[(0, 0)] = b00
        if b01 is not None:
            self.wonBoards[(0, 1)] = b01
        if b02 is not None:
            self.wonBoards[(0, 2)] = b02
        if b10 is not None:
            self.wonBoards[(1, 0)] = b10
        if b11 is not None:
            self.wonBoards[(1, 1)] = b11
        if b12 is not None:
            self.wonBoards[(1, 2)] = b12
        if b20 is not None:
            self.wonBoards[(2, 0)] = b20
        if b21 is not None:
            self.wonBoards[(2, 1)] = b21
        if b22 is not None:
            self.wonBoards[(2, 2)] = b22

    def updateModelWonBoards(self, board):
        # NEEDS TIME IMPROVEMENT 🚨 (apply hashing)
        ''' Updates the WonBoardsModel class dictionary '''
        b00, b01, b10, b11, b20, b21, b02, b12, b22 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[2, 0]), isWon(board[2, 1]), isWon(board[0, 2]), isWon(board[1, 2]), isWon(board[2, 2])

        if b00 is not None:
            self.wonBoardsModel[(0, 0)] = b00
        if b01 is not None:
            self.wonBoardsModel[(0, 1)] = b01
        if b02 is not None:
            self.wonBoardsModel[(0, 2)] = b02
        if b10 is not None:
            self.wonBoardsModel[(1, 0)] = b10
        if b11 is not None:
            self.wonBoardsModel[(1, 1)] = b11
        if b12 is not None:
            self.wonBoardsModel[(1, 2)] = b12
        if b20 is not None:
            self.wonBoardsModel[(2, 0)] = b20
        if b21 is not None:
            self.wonBoardsModel[(2, 1)] = b21
        if b22 is not None:
            self.wonBoardsModel[(2, 2)] = b22

t0 = time.time()
agent = FooFinderAgent()

iters = 2

for i in range(iters):
    agent.action(board)

print(f"{iters} actions time: {time.time() - t0}")


