import numpy as np

CENTER_ONLY_BOARD = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
CENTER_ONLY_ENEMY_BOARD = np.array([[0, 0, 0], [0, -1, 0], [0, 0, 0]])

# Auxiliaries
def isFull(board):
    return np.count_nonzero(board == 0) == 0

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

def isWon(board):
    """ Returns True if the board is won by either player, False otherwise """
    return isWonByOne(board) or isWonByMinusOne(board)

def lineEval(line, player=1):
    """ 
    Returns the heuristic value of the given row or column in the subboard.
    """
    empties = line.count(0)
    if empties == 3:
        return 0
    player_count = line.count(player)
    if empties == 2:
        return 0.2 if player_count == 1 else -0.2
    elif empties == 1:
        return 0.6 if player_count == 2 else (-0.6 if player_count == 0 else 0)
    else:
        # print(f"Found a full line at {line}, with {empties} empties")
        if player_count == 3:
            return 1
        elif player_count == 0:
            return -1
        else:
            return 0

def isDraw(board):
    ''' Returns True if the local 3x3 board is either a complete Draw, or secured to be one '''
    return fullDrawn(board) or toBeDrawn(board)

def toBeDrawn(board):
    ''' Returns True if the local 3x3 board is secured to be a Draw '''

    if np.count_nonzero(board == 0) > 1:
        return False
    
    if isWon(board):
        return False
    
    # Check for a possible win in the next move

    # Rows, Cols
    for i in range(3):
        row = (board[i, 0], board[i, 1], board[i, 2])
        col = (board[0, i], board[1, i], board[2, i])
        if detectThreat(row) or detectThreat(col):
            return False
    
    # Diagonals
    diag1 = (board[0, 0], board[1, 1], board[2, 2])
    diag2 = (board[0, 2], board[1, 1], board[2, 0])
    if detectThreat(diag1) or detectThreat(diag2):
        return False
    
    return True

def fullDrawn(board):
    ''' Returns True if the local 3x3 board is a complete Draw '''
    return (isFull(board) and not isWon(board))

def isPlayable(board):
    ''' Returns True if the local 3x3 board is still playable '''
    return not isFull(board) and not isWon(board)

def isOver(board):
    return isFull(board) or isWon(board)

def isLegal(board):
    ''' False if it's won by both players at the same time '''
    return not (isWonByOne(board) and isWonByMinusOne(board))

def isWinnable_next(board, player):
    # If the board is already won, it can't be winnable
    if isWon(board) or isFull(board):
        return False
    
    # Iterate over the 3x3 board to find empty spaces
    for row in range(3):
        for col in range(3):
            if board[row][col] == 0:  # Check for empty spot
                # Simulate placing the player's piece
                board[row][col] = player
                
                # Check if this move results in a win for the player
                if (player == 1 and isWonByOne(board)) or (player == -1 and isWonByMinusOne(board)):
                    # Restore the board and return True since it's winnable
                    board[row][col] = 0
                    return True
                
                # Restore the board to its original state before checking the next position
                board[row][col] = 0
                
    # If no winning move was found, return False
    return False

def isWinnable_next_byOne(board):
    return isWinnable_next(board, 1)

def isWinnable_next_byMinusOne(board):
    return isWinnable_next(board, -1)

def get_winnable_moves(board, player):
    """
    Returns a set of winning moves for the specified player on the given board.
    A winning move is a position (row, col) where placing the player's piece results in a win.
    """
    winning_moves = set()  # Set to store all winning moves for the player
    
    # Check each empty space
    for row in range(3):
        for col in range(3):
            if board[row][col] == 0:  # Empty spot found
                board[row][col] = player  # Simulate player's move
                
                # Check if this move results in a win
                if (player == 1 and isWonByOne(board)) or (player == -1 and isWonByMinusOne(board)):
                    winning_moves.add((row, col))  # Add the move to the set
                
                board[row][col] = 0  # Revert the move

    return winning_moves

def detectThreat(line):
    return line.count(0) == 1 and (line.count(1) == 2 or line.count(-1) == 2)

def localBoardEval(localBoard):
    """ 
    Evaluates the local board and returns an evaluation score for it.
    """
    score = 0
    
    CENTER_ONLY_EVAL = 0.0
    # If board is all 0s and a 1 in the middle, return CENTER_ONLY_EVAL
    if np.count_nonzero(localBoard) == 1:
        if localBoard[1, 1] == 1:
            if np.array_equal(localBoard, CENTER_ONLY_BOARD):
                return CENTER_ONLY_EVAL
            else:
                raise ValueError("Invalid Center Only Board")
        elif localBoard[1, 1] == -1:
            if np.array_equal(localBoard, CENTER_ONLY_ENEMY_BOARD):
                return -CENTER_ONLY_EVAL
            else:
                raise ValueError("Invalid Center Only Enemy Board")
    
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    final_score = round(score, 1)
    return final_score

def localBoardEval_v2(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    '''
    score = 0

    CENTER_ONLY_EVAL = 0.0
    # If board is all 0s and a 1 in the middle, return CENTER_ONLY_EVAL
    if np.count_nonzero(localBoard) == 1:
        if localBoard[1, 1] == 1:
            if np.array_equal(localBoard, CENTER_ONLY_BOARD):
                return CENTER_ONLY_EVAL
            else:
                raise ValueError("Invalid Center Only Board")
        elif localBoard[1, 1] == -1:
            if np.array_equal(localBoard, CENTER_ONLY_ENEMY_BOARD):
                return -CENTER_ONLY_EVAL
            else:
                raise ValueError("Invalid Center Only Enemy Board")

    player1_threat = False
    player2_threat = False
    
    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if detectThreat((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if detectThreat((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if detectThreat((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if detectThreat((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if detectThreat((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if detectThreat((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if detectThreat((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if detectThreat((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    # Check for conflicting threats
    if player1_threat and player2_threat:
        return 0  # Neutralize score if both players can win in one move

    final_score = round(score, 1)
    return final_score

def localBoardEval_v3(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    '''
    score = 0

    CENTER_ONLY_EVAL = 0.0
    # If board is all 0s and a 1 in the middle, return CENTER_ONLY_EVAL
    if np.count_nonzero(localBoard) == 1:
        if localBoard[1, 1] == 1:
            if np.array_equal(localBoard, CENTER_ONLY_BOARD):
                return CENTER_ONLY_EVAL
            else:
                raise ValueError("Invalid Center Only Board")
        elif localBoard[1, 1] == -1:
            if np.array_equal(localBoard, CENTER_ONLY_ENEMY_BOARD):
                return -CENTER_ONLY_EVAL
            else:
                raise ValueError("Invalid Center Only Enemy Board")
            
    player1_threat = False
    player2_threat = False
    
    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if detectThreat((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if detectThreat((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if detectThreat((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if detectThreat((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if detectThreat((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if detectThreat((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if detectThreat((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if detectThreat((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        if score == 0:
            return 0
        
        final_score = score * 0.2
        if final_score > 0:
            ret_scored = final_score + 0.1
        else:
            ret_scored = final_score - 0.1
        return round(ret_scored, 1)

    final_score = round(score, 1)
    return final_score

# Generators
def generate_winning_boards(file_path):
    """ 
    Generate all possible 3x3 Tic-Tac-Toe board states where exactly one player has won
    And save them to winning_boards.txt in the format hex representation of the board : winner. 
    """
    winning_boards = {}
    for state in range(3**9):  # Enumerate all possible board states
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        won_by_one = isWonByOne(board)
        won_by_minus_one = isWonByMinusOne(board)
        
        # Only include boards where exactly one player has won using XOR
        if won_by_one ^ won_by_minus_one:  # XOR condition: one wins and the other doesn't
            board_key = board.tobytes()  # Convert the board to a byte representation
            winner = 1 if won_by_one else -1
            winning_boards[board_key] = winner

    # Save the winning boards to a file for later use
    with open(file_path, 'w') as f:
        for board_key, winner in winning_boards.items():
            f.write(f"{board_key.hex()}:{winner}\n")

# Different Eval Boards (try them!)
def generate_eval_boards(file_path):
    """
    Generate all possible 3x3 Tic-Tac-Toe board states, evaluate them with localBoardEval,
    and save them to evaluated_boards.txt in the format: hex representation of the board : heuristic value.
    """
    evaluated_boards = {}

    for state in range(3**9):
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        board_key = board.tobytes()
        heuristic_value = localBoardEval(board)
        evaluated_boards[board_key] = heuristic_value

    with open(file_path, 'w') as f:
        for board_key, heuristic_value in evaluated_boards.items():
            f.write(f"{board_key.hex()}:{heuristic_value}\n")

def generate_eval_boards_v2(file_path):
    """
    Generate all possible 3x3 Tic-Tac-Toe board states, evaluate them with localBoardEval_v2,
    and save them to evaluated_boards.txt in the format: hex representation of the board : heuristic value.
    """
    evaluated_boards = {}

    for state in range(3**9):
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        board_key = board.tobytes()
        heuristic_value = localBoardEval_v2(board)
        evaluated_boards[board_key] = heuristic_value

    with open(file_path, 'w') as f:
        for board_key, heuristic_value in evaluated_boards.items():
            f.write(f"{board_key.hex()}:{heuristic_value}\n")

def generate_eval_boards_v3(file_path):
    """
    Generate all possible 3x3 Tic-Tac-Toe board states, evaluate them with localBoardEval_v3,
    and save them to evaluated_boards.txt in the format: hex representation of the board : heuristic value.
    """
    evaluated_boards = {}

    for state in range(3**9):
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        board_key = board.tobytes()
        heuristic_value = localBoardEval_v3(board)
        evaluated_boards[board_key] = heuristic_value

    with open(file_path, 'w') as f:
        for board_key, heuristic_value in evaluated_boards.items():
            f.write(f"{board_key.hex()}:{heuristic_value}\n")

def generate_draw_boards(file_path):
    """
    Generate all possible 3x3 Tic-Tac-Toe board states, evaluate if they are a draw or not (with isDraw),
    and save them to draw_boards.txt in the format: hex representation of the board : isDraw (bool).
    """
    draw_boards = {}

    # Generate all possible states with -1, 1, and at most one 0
    for state in range(3**9):  # 3^9 combinations for each cell (-1, 0, 1)
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)

        # Count empty spots (0s), continue only if there's 1 or less empty spot
        empty_count = np.count_nonzero(board == 0)
        if empty_count <= 1:
            board_key = board.tobytes()
            draw_boards[board_key] = isDraw(board)

    with open(file_path, 'w') as f:
        for board_key, is_draw in draw_boards.items():
            f.write(f"{board_key.hex()}:{is_draw}\n")

def generate_over_boards(filename):
    ''' Generates a list of all possible 3x3 boards that are over '''
    over_boards = {}

    for state in range(3**9):
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        if isOver(board):
            over_boards[board.tobytes()] = 0

    with open(filename, 'w') as f:
        for board_key in over_boards.keys():
            f.write(board_key.hex() + '\n')

def generate_move_boards(file_path):
    ''' Generates some global 3x3x3x3 boards and their respective best moves
    Allows for direct pre-computing moves, without even entering other functions'''

    '''
    FIJATE TODAS LAS CONSIDERATIONS DE MEGA HASH EN z_foofinding_notes.txt
    '''
    # TODO! 
    None

def generate_winnable_boards(file_path, player):
    """ 
    Generate all possible 3x3 Tic-Tac-Toe board states that are winnable next move by the given player
    And save them to a file in the format hex representation of the board : set of winning move(s). 
    """
    winnable_boards = {}
    
    for state in range(3**9):  # Enumerate all possible board states
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        
        if isWon(board) or isFull(board):
            continue  # Skip boards that are already won or full
        
        winning_moves = get_winnable_moves(board, player)  # Get the set of winning moves
        
        if winning_moves:  # If there are any winning moves
            board_key = board.tobytes()  # Convert the board to a byte representation
            winnable_boards[board_key] = winning_moves

    # Save the winnable boards to a file for later use
    with open(file_path, 'w') as f:
        for board_key, moves in winnable_boards.items():
            f.write(f"{board_key.hex()}:{moves}\n")

# Run
# generate_winning_boards('backend/agents/hashes/hash_winning_boards.txt')
generate_eval_boards('backend/agents/hashes/hash_evaluated_boards.txt')
generate_eval_boards_v2('backend/agents/hashes/hash_evaluated_boards_v2.txt')
generate_eval_boards_v3('backend/agents/hashes/hash_evaluated_boards_v3.txt')
# generate_draw_boards('backend/agents/hashes/hash_draw_boards.txt')
# generate_over_boards('backend/agents/hashes/hash_over_boards.txt')
# generate_move_boards('backend/agents/hashes/hash_move_boards.txt')
# generate_winnable_boards('backend/agents/hashes/hash_winnable_boards_by_one.txt', 1)
# generate_winnable_boards('backend/agents/hashes/hash_winnable_boards_by_minus_one.txt', -1)
