import numpy as np
import random
import ast
import os
from colorama import init, Style, Fore

"""
If it can make a subboard win, it plays it. 
# (not done yet) If it can block a subboard win, it blocks it
Otherwise plays randy
"""

class GreedyAgent:
    def __init__(self):
        self.id = 1
        self.name = "Greedy"
        self.icon = "🤑"
        self.description = "Greedy is an agent that doesn't think much about the future, he just plays whatever looks best at first glance."
        self.difficulty = 2
        self.loaded_up = False
        
        # Temporary to not break
        # self.load()
    
    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def reset(self):
        # print("Resetting GreedyAgent")
        self.moveNumber = 0

    def load(self):
        ''' Loads all the class elements and hashes for the agent to be ready for a game or set of games 
        To be called at most at the start of every game, ideally at the start of every set of games so as to not waste much time '''

        print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"Loading {self.name}..." + Style.RESET_ALL)
        # Move Number
        self.moveNumber = 0
        
        # hashes
        self.hash_winnable_boards_by_one = {}
        self.hash_winnable_boards_by_minus_one = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        winnable_by_one_file = os.path.join(root_dir, 'agents', 'hashes', 'hash_winnable_boards_by_one.txt')
        winnable_by_minus_one_file = os.path.join(root_dir, 'agents', 'hashes', 'hash_winnable_boards_by_minus_one.txt')
        
        self.load_winnable_boards_one(winnable_by_one_file)
        self.load_winnable_boards_minus_one(winnable_by_minus_one_file)
        
        # Register Load
        self.loaded_up = True

    def action(self, super_board, board_to_play=None):
        super_board = np.array(super_board, dtype=int)
        rows, cols, *_ = super_board.shape
        # print(Style.BRIGHT + Fore.MAGENTA + f"{self.name} move number is {self.moveNumber}, the board_to_play he got is {board_to_play},\nthe board he received is \n{super_board}" + Style.RESET_ALL)

        over_boards = []
        for i in range(rows):
            for j in range(cols):
                if isOver(super_board[i, j]):
                    over_boards.append((i, j))

        # print(Style.BRIGHT + f"Greedy LISTS THE OVERBOARDS BEFORE PLANNING HIS MOVE:, THEY ARE AS FOLLOWS: {over_boards}" + Style.RESET_ALL)

        # First Move Go Center
        if np.count_nonzero(super_board) == 0:
            if self.moveNumber != 0:
                raise ValueError("No one has played, but moveNumber is not 0")
            self.moveNumber += 1
            return 1, 1, 1, 1

        if board_to_play is None:
            
            # Greedy Action! 
            
            # First Check Global Winner
            global_results = self.globalBoardResulter(super_board)
            global_winner = self.get_winnableByOne(global_results)
            if global_winner:
                for i in range(rows):
                    for j in range(cols):
                        if (i, j) in global_winner:
                            local_winnable = self.get_winnableByOne(super_board[i, j])
                            if isPlayable(super_board[i, j]) and local_winnable:
                                # print(f"Greedy found a GLOBAL BOARD WIN, in the board {i, j}, looks like this:\n {super_board[i, j]}")
                                local_row, local_col = safeSetExtractor(super_board, local_winnable)
                                self.moveNumber += 1
                                return i, j, local_row, local_col
                        
            # Otherwise Check Wins
            for i in range(rows):
                for j in range(cols):
                    if isPlayable(super_board[i, j]):
                        local_winner = self.get_winnableByOne(super_board[i, j])
                        if local_winner:
                            # print(f"Greedy found a local board to win, in the board {i, j}, looks like this:\n {super_board[i, j]}")
                            local_row, local_col = safeSetExtractor(super_board, local_winner)
                            self.moveNumber += 1
                            return i, j, local_row, local_col
            
            # Otherwise, Check Blocks
            for i in range(rows):
                for j in range(cols):
                    if isPlayable(super_board[i, j]):
                        local_blocker = self.get_winnableByMinusOne(super_board[i, j])
                        if local_blocker:
                            # print(f"Greedy found a local board to block, in the board {i, j}, looks like this:\n {super_board[i, j]}")
                            local_row, local_col = safeSetExtractor(super_board, local_blocker)
                            self.moveNumber += 1
                            return i, j, local_row, local_col

            # Otherwise, Center Move
            if isPlayable(super_board[1, 1]):
                # print("Greedy could play center, center looks like this:\n ", super_board[1, 1])
                row, col = 1, 1
                local_row, local_col = self.randomMove(super_board[row, col])
                self.moveNumber += 1
                return row, col, local_row, local_col

            # Otherwise, Random Move
            for i in range(rows):
                for j in range(cols):
                    if isPlayable(super_board[i, j]):
                        # print(f"Greedy found a random playable board, the board is {i, j} and looks like this:\n {super_board[i, j]}, will attempt randomMove on it")
                        local_row, local_col = self.randomMove(super_board[i, j])
                        self.moveNumber += 1
                        return i, j, local_row, local_col
            
            raise ValueError(Style.BRIGHT + Fore.RED + f"Greedy couldn't find a playable board! Global Board is \n{super_board}" + Style.RESET_ALL)
            
        else:
            a, b = board_to_play
            subboard = super_board[a, b]
            if not isPlayable(subboard):
                raise ValueError(Style.BRIGHT + Fore.RED + f"Greedy Board to play is not playable! Board is \n{subboard}" + Style.RESET_ALL)

        # Greedy Action
        local_winner = self.get_winnableByOne(subboard)
        local_blocker = self.get_winnableByMinusOne(subboard)
        
        # print(f"When btp is {board_to_play}, Local winner is {local_winner}, local blocker is {local_blocker}")
 
        # Win
        if local_winner:
            # print("Greedy can win the given local board!")
            local_row, local_col = safeSetExtractor(super_board, local_winner)
        # Block
        elif local_blocker:
            # print("Greedy can block the given local board!")
            local_row, local_col = safeSetExtractor(super_board, local_blocker)
        # Straight Arrow
        elif canPlay(subboard, a, b):
            local_row, local_col = a, b
        # Random
        else:
            local_row, local_col = self.randomMove(subboard)
            
        self.moveNumber += 1
        return a, b, local_row, local_col

    def randomMove(self, board):
        empty_cells = np.flatnonzero(board == 0)
        chosen_index = random.choice(empty_cells)
        return np.unravel_index(chosen_index, board.shape)

    def globalBoardResulter(self, super_board):
        ''' Turns the global board into a 3x3 board with its results '''
        board = np.zeros((3, 3), dtype=int)
        board[0, 0] = isWon(super_board[0, 0])
        board[0, 1] = isWon(super_board[0, 1])
        board[0, 2] = isWon(super_board[0, 2])
        board[1, 0] = isWon(super_board[1, 0])
        board[1, 1] = isWon(super_board[1, 1])
        board[1, 2] = isWon(super_board[1, 2])
        board[2, 0] = isWon(super_board[2, 0])
        board[2, 1] = isWon(super_board[2, 1])
        board[2, 2] = isWon(super_board[2, 2])
        return board

    def load_winnable_boards_one(self, file_path):
        ''' 
        Loads the winnable boards from a file and stores them in a dictionary. 
        Each board's state is stored as a key (using its byte representation).
        They are stored as board : winning_moves,
        where winning_moves is a set of tuples with the moves to win.
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, moves = line.strip().split(':')
                    moves = ast.literal_eval(moves)  # Safely evaluate the set of tuples
                    self.hash_winnable_boards_by_one[bytes.fromhex(board_hex)] = set(moves)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winnable boards will not be loaded.")

    def load_winnable_boards_minus_one(self, file_path):
        ''' 
        Loads the winnable boards from a file and stores them in a dictionary. 
        Each board's state is stored as a key (using its byte representation).
        They are stored as board : winning_moves,
        where winning_moves is a set of tuples with the moves to win.
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, moves = line.strip().split(':')
                    moves = ast.literal_eval(moves)  # Safely evaluate the set of tuples
                    self.hash_winnable_boards_by_minus_one[bytes.fromhex(board_hex)] = set(moves)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winnable boards will not be loaded.")

    def get_winnableByOne(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_one.get(board_key, set())

    def get_winnableByMinusOne(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_minus_one.get(board_key, set())

def canPlay(subboard, row, col):
    ''' Returns True if the cell is empty, False otherwise '''
    return subboard[row, col] == 0

def isFull(subboard):
    ''' Returns True if the board is full, False otherwise '''
    return np.count_nonzero(subboard==0) == 0

def isPlayable(subboard):
    ''' Returns True if the board is not full and not won, False otherwise '''
    return (not isFull(subboard)) and (isWon(subboard) == 0)

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

def safeSetExtractor(board, set):
    ''' If there is a move from the set that doesn't lead to an over-subboard, returns it '''
    for move in set:
        if not isOver(board[move]):
            return move
    return set.pop()  # If all moves lead to an over-subboard, return any

# Evaluation
CENTER_ONLY_BOARD = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
CENTER_ONLY_ENEMY_BOARD = np.array([[0, 0, 0], [0, -1, 0], [0, 0, 0]])
CENTER_ONLY_EVAL = 0.421

def detectSingle(line):
    if line.count(0) == 2 and (line.count(1) == 1 or line.count(-1) == 1):
        if line.count(2) > 0:
            raise ValueError("Invalid Line with Blocked Tiles")
        return True
    else:
        return False

def detectDouble(line):
    if (line.count(0) == 1 and (line.count(1) == 2 or line.count(-1) == 2)):
        if line.count(2) > 0:
            raise ValueError("Invalid Line with Blocked Tiles")
        return True
    else:
        return False

def lineEval(line, player=1, single_eval=0.20, double_eval=0.60):
    # Keep testing single_eval and dobule_eval
    """ 
    Returns the heuristic value of the given row or column in the subboard.
    """
    empties = line.count(0)
    
    if empties == 3:
        return 0
    player_count = line.count(player)
    if empties == 2:
        return single_eval if player_count == 1 else (-1 * single_eval)
    elif empties == 1:
        return double_eval if player_count == 2 else ((-1 * double_eval) if player_count == 0 else 0)
    else:
        # print(f"Found a full line at {line}, with {empties} empties")
        if player_count == 3:
            return 1
        elif player_count == 0:
            return -1
        else:
            return 0

def local_evaluation(local_board):
    ''' Copiar la de arriba, pero hacer que si hay una tile ya contada por una doble, 
    que no se repita ever, ni en dobles ni en singles del mismp player 
    Ponerle un 2 no sirve porque le sacas los conteos al rival en sus 
    posibles amenazas con esa Tile desde otras lineas '''

    center_only_eval = 0.35
    center_need_reducer = 0.92
    # If board is all 0s and a 1 in the middle, return center only eval
    non_empties = np.count_nonzero(local_board)
    empties = 9 - non_empties
    if non_empties == 1:
        if local_board[1, 1] == 1:
            if np.array_equal(local_board, CENTER_ONLY_BOARD):
                return center_only_eval
            else:
                raise ValueError("Invalid Center Only Board")
        elif local_board[1, 1] == -1:
            if np.array_equal(local_board, CENTER_ONLY_ENEMY_BOARD):
                return -center_only_eval
            else:
                raise ValueError("Invalid Center Only Enemy Board")

    score = 0
    single_eval = 0.14
    double_eval = 0.60
    winning_eval = 3.6
    player1_threat, player2_threat = False, False
    p1_threat_spaces, p2_threat_spaces = set(), set()
    s_r1, s_r2, s_r3, s_c1, s_c2, s_c3, s_d1, s_d2 = False, False, False, False, False, False, False, False


    # Row1
    row1 = (local_board[0, 0], local_board[0, 1], local_board[0, 2])
    row1_indeces = [(0, 0), (0, 1), (0, 2)]
    row1_eval = lineEval((row1), single_eval=single_eval, double_eval=double_eval)
    
    if abs(row1_eval) == 1:
        return winning_eval * row1_eval
    
    if detectDouble(row1):
        if abs(row1_eval) != double_eval:
            raise ValueError(f"Invalid! Detected Double but Eval was {row1_eval}")

        if row1_eval > 0:
            player1_threat = True
            p1_threat_tile = row1_indeces[row1.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row1, board was {local_board}")
                score += (row1_eval * center_need_reducer)
            else:
                score += row1_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row1_eval < 0:
            player2_threat = True
            p2_threat_tile = row1_indeces[row1.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row1, board was {local_board}")
                score += (row1_eval * center_need_reducer)
            else:
                score += row1_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row1}")
    
    elif detectSingle(row1):
        if abs(row1_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {row1_eval}")
        s_r1 = True

    elif row1_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {row1_eval}")
    
    else:
        score += row1_eval


    # Row 2
    row2 = (local_board[1, 0], local_board[1, 1], local_board[1, 2])
    row2_indeces = [(1, 0), (1, 1), (1, 2)]
    row2_eval = lineEval((row2), single_eval=single_eval, double_eval=double_eval)
    
    if abs(row2_eval) == 1:
        return winning_eval * row2_eval
    
    if detectDouble((row2)):
        if row2_eval > 0:
            player1_threat = True
            p1_threat_tile = row2_indeces[row2.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                score += (row2_eval * center_need_reducer)
            else:
                score += row2_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row2_eval < 0:
            player2_threat = True
            p2_threat_tile = row2_indeces[row2.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                score += (row2_eval * center_need_reducer)
            else:
                score += row2_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row2}")
    
    elif detectSingle(row2):
        if abs(row2_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {row2_eval}")
        s_r2 = True

    elif row2_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {row2_eval}")

    else:
        score += row2_eval


    # Row 3
    row3 = (local_board[2, 0], local_board[2, 1], local_board[2, 2])
    row3_indeces = [(2, 0), (2, 1), (2, 2)]
    row3_eval = lineEval((row3), single_eval=single_eval, double_eval=double_eval)
    
    if abs(row3_eval) == 1:
        return winning_eval * row3_eval
    
    if detectDouble((row3)):
        if row3_eval > 0:
            player1_threat = True
            p1_threat_tile = row3_indeces[row3.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row3, board was {local_board}")
                score += (row3_eval * center_need_reducer)
            else:
                score += row3_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row3_eval < 0:
            player2_threat = True
            p2_threat_tile = row3_indeces[row3.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row3, board was {local_board}")
                score += (row3_eval * center_need_reducer)
            else:
                score += row3_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row3}")
    
    elif detectSingle(row3):
        if abs(row3_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {row3_eval}")
        s_r3 = True
    
    elif row3_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {row3_eval}")

    else:
        score += row3_eval


    # Column 1
    col1 = (local_board[0, 0], local_board[1, 0], local_board[2, 0])
    col1_indeces = [(0, 0), (1, 0), (2, 0)]
    col1_eval = lineEval((col1), single_eval=single_eval, double_eval=double_eval)

    if abs(col1_eval) == 1:
        return winning_eval * col1_eval

    if detectDouble((col1)):
        if col1_eval > 0:
            player1_threat = True
            p1_threat_tile = col1_indeces[col1.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col1, board was {local_board}")
                score += (col1_eval * center_need_reducer)
            else:
                score += col1_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col1_eval < 0:
            player2_threat = True
            p2_threat_tile = col1_indeces[col1.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col1, board was {local_board}")
                score += (col1_eval * center_need_reducer)
            else:
                score += col1_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col1}")
    
    elif detectSingle(col1):
        if abs(col1_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {col1_eval}")
        s_c1 = True

    elif col1_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {col1_eval}")

    else:
        score += col1_eval


    # Column 2
    col2 = (local_board[0, 1], local_board[1, 1], local_board[2, 1])
    col2_indeces = [(0, 1), (1, 1), (2, 1)]
    col2_eval = lineEval((col2), single_eval=single_eval, double_eval=double_eval)
    
    if abs(col2_eval) == 1:
        return winning_eval * col2_eval
    
    if detectDouble((col2)):
        if col2_eval > 0:
            player1_threat = True
            p1_threat_tile = col2_indeces[col2.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                score += (col2_eval * center_need_reducer)
            else:
                score += col2_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col2_eval < 0:
            player2_threat = True
            p2_threat_tile = col2_indeces[col2.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                score += (col2_eval * center_need_reducer)
            else:
                score += col2_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col2}")
        
    elif detectSingle(col2):
        if abs(col2_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {col2_eval}")
        s_c2 = True

    elif col2_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {col2_eval}")
    
    else:
        score += col2_eval


    # Column 3
    col3 = (local_board[0, 2], local_board[1, 2], local_board[2, 2])
    col3_indeces = [(0, 2), (1, 2), (2, 2)]
    col3_eval = lineEval((col3), single_eval=single_eval, double_eval=double_eval)

    if abs(col3_eval) == 1:
        return winning_eval * col3_eval

    if detectDouble((col3)):
        if col3_eval > 0:
            player1_threat = True
            p1_threat_tile = col3_indeces[col3.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col3, board was {local_board}")
                score += (col3_eval * center_need_reducer)
            else:
                score += col3_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col3_eval < 0:
            player2_threat = True
            p2_threat_tile = col3_indeces[col3.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col3, board was {local_board}")
                score += (col3_eval * center_need_reducer)
            else:
                score += col3_eval
                p2_threat_spaces.add(p2_threat_tile)
                
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col3}")
    
    elif detectSingle(col3):
        if abs(col3_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {col3_eval}")
        s_c3 = True

    elif col3_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {col3_eval}")
    
    else:
        score += col3_eval


    # Diagonal Top-Bottom
    diagTB = (local_board[0, 0], local_board[1, 1], local_board[2, 2])
    diagTB_indeces = [(0, 0), (1, 1), (2, 2)]
    diagTB_eval = lineEval((diagTB), single_eval=single_eval, double_eval=double_eval)
    
    if abs(diagTB_eval) == 1:
        return winning_eval * diagTB_eval
    
    if detectDouble((diagTB)):
        if diagTB_eval > 0:
            player1_threat = True
            p1_threat_tile = diagTB_indeces[diagTB.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                score += (diagTB_eval * center_need_reducer)
            else:
                score += diagTB_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif diagTB_eval < 0:
            player2_threat = True
            p2_threat_tile = diagTB_indeces[diagTB.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                score += (diagTB_eval * center_need_reducer)
            else:
                score += diagTB_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {diagTB}")
    
    elif detectSingle(diagTB):
        if abs(diagTB_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {diagTB_eval}")
        s_d1 = True

    elif diagTB_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {diagTB_eval}")
    
    else:
        score += diagTB_eval


    # Diagonal Bottom-Top
    diagBT = (local_board[2, 0], local_board[1, 1], local_board[0, 2])
    diagBT_indeces = [(2, 0), (1, 1), (0, 2)]
    diagBT_eval = lineEval((diagBT), single_eval=single_eval, double_eval=double_eval)
    
    if abs(diagBT_eval) == 1:
        return winning_eval * diagBT_eval
    
    if detectDouble((diagBT)):
        if diagBT_eval > 0:
            player1_threat = True
            p1_threat_tile = diagBT_indeces[diagBT.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            elif p1_threat_tile == (1, 1):
                score += (diagBT_eval * center_need_reducer)
            else:
                score += diagBT_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif diagBT_eval < 0:
            player2_threat = True
            p2_threat_tile = diagBT_indeces[diagBT.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            elif p2_threat_tile == (1, 1):
                score += (diagBT_eval * center_need_reducer)
            else:
                score += diagBT_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {diagBT}")
    
    elif detectSingle(diagBT):
        if abs(diagBT_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {diagBT_eval}")
        s_d2 = True

    elif diagBT_eval != 0:
        raise ValueError(f"Found Non-Zero Eval when wasnt Single nor Double, eval: {diagBT_eval}")
    
    else:
        score += diagBT_eval



    # Single Checks now that the lists are completed
    if detectSingle(row1):
        if not s_r1:
            raise ValueError(f"Single Detected R1 but not in Single List, eval: {row1_eval}")
        open_A = row1_indeces[row1.index(0)]
        open_B = row1_indeces[row1.index(0, row1.index(0) + 1)]

        if row1_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row1, board was {local_board}")
                score += (row1_eval * center_need_reducer)
            else:
                score += row1_eval
        
        elif row1_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row1, board was {local_board}")
                score += (row1_eval * center_need_reducer)
            else:
                score += row1_eval

    if detectSingle(row2):
        if not s_r2:
            raise ValueError(f"Single Detected R2 but not in Single List, eval: {row2_eval}")
        open_A = row2_indeces[row2.index(0)]
        open_B = row2_indeces[row2.index(0, row2.index(0) + 1)]

        if row2_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (row2_eval * center_need_reducer)
            else:
                score += row2_eval
        
        elif row2_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (row2_eval * center_need_reducer)
            else:
                score += row2_eval

    if detectSingle(row3):
        if not s_r3:
            raise ValueError(f"Single Detected R3 but not in Single List, eval: {row3_eval}")
        open_A = row3_indeces[row3.index(0)]
        open_B = row3_indeces[row3.index(0, row3.index(0) + 1)]

        if row3_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row3, board was {local_board}")
                score += (row3_eval * center_need_reducer)
            else:
                score += row3_eval

        elif row3_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Row3, board was {local_board}")
                score += (row3_eval * center_need_reducer)
            else:
                score += row3_eval

    if detectSingle(col1):
        if not s_c1:
            raise ValueError(f"Single Detected C1 but not in Single List, eval: {col1_eval}")
        open_A = col1_indeces[col1.index(0)]
        open_B = col1_indeces[col1.index(0, col1.index(0) + 1)]

        if col1_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col1, board was {local_board}")
                score += (col1_eval * center_need_reducer)
            else:
                score += col1_eval
        
        elif col1_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col1, board was {local_board}")
                score += (col1_eval * center_need_reducer)
            else:
                score += col1_eval

    if detectSingle(col2):
        if not s_c2:
            raise ValueError(f"Single Detected C2 but not in Single List, eval: {col2_eval}")
        open_A = col2_indeces[col2.index(0)]
        open_B = col2_indeces[col2.index(0, col2.index(0) + 1)]

        if col2_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (col2_eval * center_need_reducer)
            else:
                score += col2_eval
        
        elif col2_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (col2_eval * center_need_reducer)
            else:
                score += col2_eval

    if detectSingle(col3):
        if not s_c3:
            raise ValueError(f"Single Detected C3 but not in Single List, eval: {col3_eval}")
        open_A = col3_indeces[col3.index(0)]
        open_B = col3_indeces[col3.index(0, col3.index(0) + 1)]

        if col3_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col3, board was {local_board}")
                score += (col3_eval * center_need_reducer)
            else:
                score += col3_eval
        
        elif col3_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                raise ValueError(f"Center Tile Detected in a None-Center Line, Col3, board was {local_board}")
                score += (col3_eval * center_need_reducer)
            else:
                score += col3_eval

    if detectSingle(diagTB):
        if not s_d1:
            raise ValueError(f"Single Detected D1 but not in Single List, eval: {diagTB_eval}")
        open_A = diagTB_indeces[diagTB.index(0)]
        open_B = diagTB_indeces[diagTB.index(0, diagTB.index(0) + 1)]

        if diagTB_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (diagTB_eval * center_need_reducer)
            else:
                score += diagTB_eval
        
        elif diagTB_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (diagTB_eval * center_need_reducer)
            else:
                score += diagTB_eval

    if detectSingle(diagBT):
        if not s_d2:
            raise ValueError(f"Single Detected D2 but not in Single List, eval: {diagBT_eval}")
        open_A = diagBT_indeces[diagBT.index(0)]
        open_B = diagBT_indeces[diagBT.index(0, diagBT.index(0) + 1)]

        if diagBT_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (diagBT_eval * center_need_reducer)
            else:
                score += diagBT_eval
        
        elif diagBT_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            elif open_A == (1, 1) or open_B == (1, 1):
                score += (diagBT_eval * center_need_reducer)
            else:
                score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        if empties == 1:
            return 0
        if empties == 2:
            if len(p1_threat_spaces) == 1 and len(p2_threat_spaces) == 1:
                if score != 0:
                    raise ValueError(f"Conflicting Threats with 2 empties but score != 0, score is {score} when the board is:\n{local_board}")
                return 0
        # else:
        #     final_score = score * 0.75
        #     return round(final_score, 2)

    final_score = round(score, 2)
    return final_score


# board_ex = np.zeros((3, 3, 3, 3), dtype=int)
# agent = GreedyAgent()

# move = agent.action(board_ex, board_to_play=None)