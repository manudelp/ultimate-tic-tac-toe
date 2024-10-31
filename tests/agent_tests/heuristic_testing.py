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

class MonkeyStrategy:

    def moveQuality(self, board_copy, r, c, r_l, c_l, player):
        ''' Given a copy of the board, and the 4 coordinates of a move, determines its quality value 
        (r, c) indicates the global board coordinates of the local board to play in
        (r_l, c_l) indicates the local board coordinates of the move to make '''

        previous_balance = self.boardBalance(board_copy)
        board_copy[r, c][r_l, c_l] = player
        new_balance = self.boardBalance(board_copy)
        board_copy[r, c][r_l, c_l] = 0

        return new_balance - previous_balance

    def balance_strat(self, board, board_to_play=None):
        ''' Returns the best move based on the sum of local board balances '''
        bestMove = None
        boardCopia = board.copy()
        maxQual = float('-inf')

        if board_to_play is not None:
            r, c = board_to_play
            if isPlayable(boardCopia[r, c]):
                for r_l in range(3):
                    for c_l in range(3):
                        if canPlay(boardCopia[r, c], r_l, c_l):
                            currentQual = self.moveQuality(boardCopia, r, c, r_l, c_l, player=1)
                            if currentQual > maxQual:
                                maxQual = currentQual
                                bestMove = (r, c, r_l, c_l)
        else: 
            for r in range(3):
                for c in range(3):
                    if isPlayable(boardCopia[r, c]):
                        for r_l in range(3):
                            for c_l in range(3):
                                if canPlay(boardCopia[r, c], r_l, c_l):
                                    currentQual = self.moveQuality(boardCopia, r, c, r_l, c_l, player=1)
                                    if currentQual > maxQual:
                                        maxQual = currentQual
                                        bestMove = (r, c, r_l, c_l)
        
        if bestMove is not None:
            boardCopia[bestMove[0], bestMove[1]][bestMove[2], bestMove[3]] = 1
            print(f"MonkeyStrategy: Best Move is {bestMove}, and has a quality of {maxQual}")
            print(f"The Balance with this move is {self.boardBalance(boardCopia)}, compared to the previous balance of {self.boardBalance(board)}")
            return bestMove
        return None



    def lineEval(self, line, player=1, diag=False):
        ''' 
        Returns the heuristic value of the given row or column in the subboard 
        If 2 empty and 1 player, returns ±0.2
        If 1 empty and 2 player, returns ±0.6
        If 3 player (board is Won), returns ±1, which then defines ±6 for Local Board Eval
        '''
        empties = np.count_nonzero(line == 0)

        if empties == 3: # row is empty, no score
            return 0
        
        player_count = np.count_nonzero(line == player)
        
        if empties == 2:
            if player_count == 1:
                return 0.2
            else:
                return -0.2
        
        elif empties == 1:
            if player_count == 2:
                return 0.6
            elif player_count == 0:
                return -0.6
            else:
                return 0
        
        else:
            if player_count == 3:
                return 1
            else:
                return -1

    def localBoardEval(self, localBoard):
        ''' 
        Evaluates the local board and returns an evaluation score for it 
        For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
        FOr Won Boards, Balance is ± 6.4
        '''
        rows, cols = localBoard.shape

        # precomputed boards logic

        score = 0

        # Rows & Columns
        for i in range(rows):

            # Rows
            row = localBoard[i]
            row_eval = self.lineEval(row)

            # If the Local Board is Won, cut and return ±10
            if abs(row_eval) == 1:
                return 6.4 * row_eval
            score += row_eval

            # Columns
            col = localBoard[:, i]
            col_eval = self.lineEval(col)

            # If the Local Board is Won, cut and return ±10
            if abs(col_eval) == 1:
                return 6.4 * col_eval
            score += col_eval

        # Diagonals
        diagTB = np.array((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]),dtype=int)
        diagBT = np.array((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]),dtype=int)

        diagTB_eval = self.lineEval(diagTB)
        # If the Local Board is Won, cut and return ±10
        if abs(diagTB_eval) == 1:
            return 10 * diagTB_eval
        score += diagTB_eval

        diagBT_eval = self.lineEval(diagBT)
        # If the Local Board is Won, cut and return ±10
        if abs(diagBT_eval) == 1:
            return 10 * diagBT_eval
        score += diagBT_eval

        return score

    def boardBalance(self, board):
        ''' Returns the heuristic value of the board '''
        rows, cols, *_ = board.shape
        balance = 0

        # Auxiliar For Now!
        for r in range(rows):
            for c in range(cols):
                localBoard = board[r, c]
                balance += self.localBoardEval(localBoard)
        
        return balance

strat = MonkeyStrategy()
the_move = strat.balance_strat(board, board_to_play=(1, 1))

print("juanchi \n")