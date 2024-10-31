import random
import numpy as np


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
        self.id = "Randy🎲"
        self.hash_over_boards = {}
        self.load_over_boards('backend/agents/hashes/hash_over_boards.txt')

    def __str__(self):
        return self.id

    def action(self, board, board_to_play=None):
        board = np.array(board, dtype=int)

        self.global_row, self.global_col = None, None
        
        # Make Playable Local Boards List
        self.playable_boards_list = []
        for i in range(3):
            for j in range(3):
                if self.get_isPlayable(board[i, j]):
                    self.playable_boards_list.append((i, j))

        if board_to_play is None:
            if len(self.playable_boards_list) == 0:
                raise ValueError(f"There are no playable boards. The board is:\n{board}")
            self.global_row, self.global_col = random.choice(self.playable_boards_list)
        else:   
            self.global_row, self.global_col = board_to_play

        if self.global_row is None or self.global_col is None:
            raise ValueError(f"global_row or global_col is None! Board to play was {board_to_play}")

        local_board = board[self.global_row, self.global_col]
        print(f"I randy will attempt randomMove on the local_board: {self.global_row, self.global_col}")
        c, d = self.randomMove(local_board)
        return self.global_row, self.global_col, c, d

    def randomMove(self, board):
        if isFull(board):
            raise ValueError(f"The board is full while board is {board}")
        empty_cells = np.flatnonzero(board == 0)
        if empty_cells.size == 0:
            raise ValueError(f"The board is full... it shouldn't even be, even with a jsx fail, I already checked\n Board is {board}")
        chosen_index = random.choice(empty_cells)
        return np.unravel_index(chosen_index, board.shape)

    def load_over_boards(self, file_path):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
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

    def get_isOver(self, board):
        # TIMEIT APPROVED ✅
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_over_boards.get(board_key, False)

    def get_isPlayable(self, board):
        # TIMEIT UNSURE 🤔 (yes it would be faster to just call not get_isOver directly 
        # instead of calling get_isPlayable to call it as a mediator, dont know if its relevant enough to check tho)
        ''' Returns True if the board is playable, False otherwise '''
        return not self.get_isOver(board)
