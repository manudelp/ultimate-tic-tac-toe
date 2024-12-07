import numpy as np
import math
from typing import Tuple

CENTER_ONLY_BOARD = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
CENTER_ONLY_ENEMY_BOARD = np.array([[0, 0, 0], [0, -1, 0], [0, 0, 0]])
CENTER_ONLY_EVAL = 0.421

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

def advanced_line_eval(line, player=1):
    ''' Works like lineEval, but also considering tiles with a '2' as being blocked,
    not counting to any player, and blocking any row/column/diagonal from a potential 3-in-line '''
    if line.count(2) > 0:
        return 0
    # TODO: Keep testing single_eval and double_eval
    return lineEval(line, player=player, single_eval=0.15, double_eval=0.60)

def lineIsBlocked(line):
    ''' Returns True if the given line is blocked '''
    return (line.count(2) > 0)

def allLinesBlocked(board):
    ''' Returns True if all rows, columns, and diagonals are blocked '''
    # Rows
    for i in range(3):
        if not lineIsBlocked((board[i, 0], board[i, 1], board[i, 2])):
            return False
        
    # Columns
    for i in range(3):
        if not lineIsBlocked((board[0, i], board[1, i], board[2, i])):
            return False
        
    # Diagonals
    if not lineIsBlocked((board[0, 0], board[1, 1], board[2, 2])):
        return False
    
    if not lineIsBlocked((board[2, 0], board[1, 1], board[0, 2])):
        return False
    
    # No unblocked lines found
    return True

def toBeDrawn(board):
    ''' Returns True if the local 3x3 board is secured to be a Draw '''
    zeros_count = np.count_nonzero(board == 0)
    twos_count = np.count_nonzero(board == 2)

    if (twos_count < 3) and (zeros_count > 1):
        return False

    if isWon(board):
        return False

    if allLinesBlocked(board):
        return True

    if np.count_nonzero(board == 2) > 6:
        return True

    
    # Check for a possible win in the next move

    # Rows, Cols
    for i in range(3):
        row = (board[i, 0], board[i, 1], board[i, 2])
        col = (board[0, i], board[1, i], board[2, i])
        if detectDouble(row) or detectDouble(col):
            return False
    
    # Diagonals
    diag1 = (board[0, 0], board[1, 1], board[2, 2])
    diag2 = (board[0, 2], board[1, 1], board[2, 0])
    if detectDouble(diag1) or detectDouble(diag2):
        return False
    
    return True

def fullDrawn(board):
    ''' Returns True if the local 3x3 board is a complete Draw '''
    return (isFull(board) and not isWon(board))

def isDraw(board):
    ''' Returns True if the local 3x3 board is either a complete Draw, or secured to be one '''
    return fullDrawn(board) or toBeDrawn(board)

def isPlayable(board):
    ''' Returns True if the local 3x3 board is still playable '''
    return not isFull(board) and not isWon(board)

def isOver(board):
    return isFull(board) or isWon(board)

def isWonByBoth(board):
    ''' False if it's won by both players at the same time '''
    return (isWonByOne(board) and isWonByMinusOne(board))

def isWonMoreThanTwiceByPlayer(board, player):
    ''' Returns True if the given player has 3 or more 3-in-line wins on the same board '''
    # TODO: Complete this for the mega hash
    raise ValueError("Not Implemented Yet")

def isWonMoreThanTwice(board):
    return (isWonMoreThanTwiceByPlayer(board, player=1) or isWonMoreThanTwiceByPlayer(board, player=-1))

def isIllegal(board):
    ''' Returns True if the board is won by both players, or won more than twice by either player '''
    return isWonByBoth(board) or isWonMoreThanTwice(board)

def isLegal(board):
    ''' Returns True if the board is neither won by both players, nor won more than twice by either player'''
    return not isIllegal(board)

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

def localBoardEval(localBoard):
    """ 
    Evaluates the local board and returns an evaluation score for it.
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    When both players threat, nothing changes, just keep working as usual
    """
    score = 0
    
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

    final_score = round(score, 2)
    return final_score

def localBoardEval_v2(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    Uses single_line = 0.14 & double_line = 0.60
    '''
    score = 0
    player1_threat = False
    player2_threat = False
    single_eval = 0.14
    double_eval = 0.60

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

    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]), single_eval=single_eval, double_eval=double_eval)
    if detectDouble((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    return round(score, 2)

def localBoardEval_v3(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    When both players threat, tones down
    '''
    score = 0

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
    if detectDouble((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        if row1_eval > 0:
            player1_threat = True
        if row1_eval < 0:
            player2_threat = True
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if detectDouble((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        if row2_eval > 0:
            player1_threat = True
        if row2_eval < 0:
            player2_threat = True
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if detectDouble((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        if row3_eval > 0:
            player1_threat = True
        if row3_eval < 0:
            player2_threat = True
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if detectDouble((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if detectDouble((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if detectDouble((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    if detectDouble((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    if detectDouble((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2])):
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
        return round(ret_scored, 2)

    final_score = round(score, 2)
    return final_score

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
                final_score = score * 0.75
                return round(final_score, 2)
        # else:
        #     final_score = score * 0.75
        #     return round(final_score, 2)

    final_score = round(score, 2)
    return final_score

def results_board_eval(local_board):
    ''' Given a 3x3 board, returns the local eval 
    Unlike the localBoardEval functions, boards for this one can have 4 types of pieces instead of the usual 3
    1s are for player1, -1s are for player2, 0s are empty tiles, and 2s are blocked tiles that don't count for any player
    '''
    score = 0
    victory_eval = 6.4
    player1_threat = False
    player2_threat = False

    # Rows
    row1_eval = advanced_line_eval((local_board[0, 0], local_board[0, 1], local_board[0, 2]))
    if detectDouble((local_board[0, 0], local_board[0, 1], local_board[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * row1_eval
    score += row1_eval

    row2_eval = advanced_line_eval((local_board[1, 0], local_board[1, 1], local_board[1, 2]))
    if detectDouble((local_board[1, 0], local_board[1, 1], local_board[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * row2_eval
    score += row2_eval

    row3_eval = advanced_line_eval((local_board[2, 0], local_board[2, 1], local_board[2, 2]))
    if detectDouble((local_board[2, 0], local_board[2, 1], local_board[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * row3_eval
    score += row3_eval

    # Columns
    col1_eval = advanced_line_eval((local_board[0, 0], local_board[1, 0], local_board[2, 0]))
    if detectDouble((local_board[0, 0], local_board[1, 0], local_board[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * col1_eval
    score += col1_eval

    col2_eval = advanced_line_eval((local_board[0, 1], local_board[1, 1], local_board[2, 1]))
    if detectDouble((local_board[0, 1], local_board[1, 1], local_board[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * col2_eval
    score += col2_eval

    col3_eval = advanced_line_eval((local_board[0, 2], local_board[1, 2], local_board[2, 2]))
    if detectDouble((local_board[0, 2], local_board[1, 2], local_board[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = advanced_line_eval((local_board[0, 0], local_board[1, 1], local_board[2, 2]))
    if detectDouble((local_board[0, 0], local_board[1, 1], local_board[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * diagTB_eval
    score += diagTB_eval

    diagBT_eval = advanced_line_eval((local_board[2, 0], local_board[1, 1], local_board[0, 2]))
    if detectDouble((local_board[2, 0], local_board[1, 1], local_board[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        raise ValueError(f"Found a Victory Line with {row1_eval} in {local_board}")
        return victory_eval * diagBT_eval
    score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        final_score = score * 0.75
        return round(final_score, 2)
    
    final_score = round(score, 2)
    return final_score

def whoWon(subboard):
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
    
    return 0

def get_best_line(line, player):
    if player != 1 and player != -1:
        raise ValueError("Invalid Player Value")

    if line.count(-player) > 0:
        return 0
    
    if line.count(player) == 0:
        return 0
    
    return line.count(player)

def get_best_connection(board, player):
    ''' Returns what the best connection for the given player in the board is
    If it's a single piece open line, returns SINGLE_EVAL, if it's a double piece open line, returns DOUBLE_EVAL'''
    SINGLE_COEF = 2.4
    DOUBLE_COEF = 5

    if player != 1 and player != -1:
        raise ValueError("Invalid Player Value")
    
    # Rows
    row1 = (board[0, 0], board[0, 1], board[0, 2])
    row2 = (board[1, 0], board[1, 1], board[1, 2])
    row3 = (board[2, 0], board[2, 1], board[2, 2])

    row1_connection = get_best_line(row1, player)
    row2_connection = get_best_line(row2, player)
    row3_connection = get_best_line(row3, player)

    # Columns
    col1 = (board[0, 0], board[1, 0], board[2, 0])
    col2 = (board[0, 1], board[1, 1], board[2, 1])
    col3 = (board[0, 2], board[1, 2], board[2, 2])

    col1_connection = get_best_line(col1, player)
    col2_connection = get_best_line(col2, player)
    col3_connection = get_best_line(col3, player)

    # Diagonals
    main_diagonal = (board[0, 0], board[1, 1], board[2, 2])
    anti_diagonal = (board[2, 0], board[1, 1], board[0, 2])
    main_diag_connection = get_best_line(main_diagonal, player)
    anti_diag_connection = get_best_line(anti_diagonal, player)

    best_connection = max(row1_connection, row2_connection, row3_connection, 
                          col1_connection, col2_connection, col3_connection, 
                          main_diag_connection, anti_diag_connection)

    if best_connection == 0:
        return 0

    elif best_connection == 1:
        return SINGLE_COEF
    
    elif best_connection == 2:
        return DOUBLE_COEF
    
    else:
        raise ValueError("Invalid Best Connection Value")

def best_connection_coefficient(board, player):
    if player == 0:
        return 0
    
    best_connection_player = get_best_connection(board, player)
    best_connection_rival = get_best_connection(board, -player)

    if best_connection_rival > best_connection_player:
        raise ValueError("Best Connection was higher for the player who wasn't the positional lead")
    
    return best_connection_player

def get_positional_lead(board: np.ndarray, heuristic_value: float) -> int:
    ''' Returns the positional lead of the board, 3 for player 1, -3 for player2, 0 if equal 
    If heuristic is positive, lead is player1, if negative, lead is player2. Otherwise, lead is 0'''
    if heuristic_value == 0:
        return 0
    elif heuristic_value > 0:
        return 3
    elif heuristic_value < 0:
        return -3
    else:
        raise ValueError(f"Invalid heuristic value: {heuristic_value}")

def get_positional_score(board: np.ndarray, result, positional_lead: int, local_eval, normalizer=4.25) -> float:
    ''' Given the positonal lead, returns the positional score of the board '''
    if result != 0 or positional_lead == 0:
        return 0
    
    lead_player = positional_lead / 3
    if lead_player != 1 and lead_player != -1 and lead_player != 0:
        raise ValueError(f"Invalid positional_lead value: {positional_lead}")
    
    local_eval_factor = ((local_eval ** 2) ** 0.9) / 42
    local_eval_coefficient = math.exp(local_eval_factor)
    best_connection = best_connection_coefficient(board, lead_player)
    
    final_score = lead_player * best_connection * local_eval_coefficient / normalizer
    
    if math.copysign(1, final_score) != lead_player:
        raise ValueError(f"Invalid positional score sign: {final_score} for lead player: {lead_player}")
    
    if (final_score / abs(final_score)) != lead_player:
        raise ValueError(f"Invalid positional score sign: {final_score} for lead player: {lead_player}")
    
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

def generate_winning_results_boards(file_path):
    """ 
    Generate all possible 3x3 Tic-Tac-Toe board states where exactly one player has won
    And save them to winning_boards.txt in the format hex representation of the board : winner. 
    """
    winning_boards = {}
    for state in range(4**9):  # Enumerate all possible board states
        board = np.array([(state // 4**i) % 4 - 1 for i in range(9)]).reshape(3, 3)
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

def generate_blizzard_winning_boards(file_path):
    """ 
    Generate all possible 3x3 Tic-Tac-Toe board states where exactly one player has won
    And save them to winning_boards.txt in the format hex representation of the board : winner. 
    """
    blizzard_winning_boards = {}
    for state in range(4**9):  # Enumerate all possible board states
        board = np.array([(state // 4**i) % 4 - 1 for i in range(9)]).reshape(3, 3)
        won_by_one = isWonByOne(board)
        won_by_minus_one = isWonByMinusOne(board)
        
        # Only include boards where exactly one player has won using XOR
        if won_by_one ^ won_by_minus_one:  # XOR condition: one wins and the other doesn't
            board_key = board.tobytes()  # Convert the board to a byte representation
            winner = 1 if won_by_one else -1
            blizzard_winning_boards[board_key] = winner

    # Save the winning boards to a file for later use
    with open(file_path, 'w') as f:
        for board_key, winner in blizzard_winning_boards.items():
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
        result = int(whoWon(board))
        res_coef = int(heuristic_value/6)
        if result != res_coef:
            raise ValueError(f"Invalid Result Value for {board}, whoWon was {result} and coef was {res_coef}")
        evaluated_boards[board_key] = (heuristic_value, result)

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
        result = int(whoWon(board))
        res_coef = int(heuristic_value/6)
        if result != res_coef:
            raise ValueError(f"Invalid Result Value for {board}, whoWon was {result} and coef was {res_coef}")
        evaluated_boards[board_key] = (heuristic_value, result)

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
        result = int(whoWon(board))
        res_coef = int(heuristic_value/6)
        if result != res_coef:
            raise ValueError(f"Invalid Result Value for {board}, whoWon was {result} and coef was {res_coef}")
        evaluated_boards[board_key] = (heuristic_value, result)

    with open(file_path, 'w') as f:
        for board_key, heuristic_value in evaluated_boards.items():
            f.write(f"{board_key.hex()}:{heuristic_value}\n")

def generate_results_board_eval(file_path):
    """
    Generate all possible 3x3 Tic-Tac-Toe board states (with values 1, -1, 0, 2), 
    evaluate them with local_evaluation, and save them to evaluated_boards.txt 
    in the format: hex representation of the board : heuristic value.
    """
    evaluated_boards = {}

    for state in range(4**9):
        board = np.array([(state // 4**i) % 4 - 1 for i in range(9)]).reshape(3, 3)
        
        # Debugs
        zeros = np.count_nonzero(board == 0)
        ones = np.count_nonzero(board == 1)
        minus_ones = np.count_nonzero(board == -1)
        twos = np.count_nonzero(board == 2)
        
        if zeros + ones + minus_ones + twos != 9:
            raise ValueError("Invalid Board State")
        
        if board.shape != (3, 3):
            raise ValueError("Invalid Board Shape")

        isWonBoard = isWon(board)
        if not isWonBoard:
            board_key = board.tobytes()
            heuristic_value = results_board_eval(board)
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

def generate_draw_results_boards(file_path):
    """
    Generate all possible 3x3 Tic-Tac-Toe board states, evaluate if they are a draw or not (with isDraw),
    and save them to draw_boards.txt in the format: hex representation of the board : isDraw (bool).
    """
    draw_boards = {}

    # Generate all possible states with -1, 1, and at most one 0
    for state in range(4**9):  # 4^9 combinations for each cell (-1, 0, 1)
        board = np.array([(state // 4**i) % 4 - 1 for i in range(9)]).reshape(3, 3)

        # Count empty spots (0s), continue only if there's 1 or less empty spot
        empty_count = np.count_nonzero(board == 0)
        twos_count = np.count_nonzero(board == 2)
        if (empty_count <= 1) or (twos_count >= 3):
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

def generate_blizzard_over_boards(filename):
    ''' Generates a list of all possible 3x3 boards that are over. Considering boards with 4 possible pieces
    Where 1s and -1s are player pieces, 0s are empty, and 2s are blocked '''
    blizzard_over_boards = {}
    
    for state in range(4**9):
        board = np.array([(state // 4**i) % 4 - 1 for i in range(9)]).reshape(3, 3)
        if isOver(board):
            blizzard_over_boards[board.tobytes()] = 0
            
    with open(filename, 'w') as f:
        for board_key in blizzard_over_boards.keys():
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

def generate_legal_boards(file_path):
    ''' Generates a list of all possible 3x3 boards that are legal '''
    # TODO: Implement this appropriately for the mega hash
    # Sorry... no! This gets outdated by the great idea of 
    # only counting drawn boards, won boards by one and won boards by minus one, 1 time each (so, 3 instead of 8590)
    # since all drawn boards mean the same, all won by 1 mean the same, all won by minus one mean the same
    legal_boards = {}

    for state in range(3**9):
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        if isLegal(board):
            legal_boards[board.tobytes()] = 0
            # TODO: Another idea... if you're gonna be using this for the mega hash and the mega hash uses local evals, might as well generate them with local evals
            # so you can just retrieve that from here, instead of first generating them and then retrieving their local evals separately...
            # or else you could just do a plain Set instead of a dictionary, why a dict if you're just gonna hash to 0s? I like the local eval idea tho

    with open(file_path, 'w') as f:
        for board_key in legal_boards.keys():
            f.write(board_key.hex() + '\n')

def generate_local_boards_info(file_path):
    ''' Generates a list of all possible 3x3 boards and their respective relevant information 
    Such information is (evaluation, result, positional_lead, positional_score)'''
    evaluated_boards = {}

    for state in range(3**9):
        board = np.array([(state // 3**i) % 3 - 1 for i in range(9)]).reshape(3, 3)
        board_key = board.tobytes()

        heuristic_value = local_evaluation(board)
        result = 2 if isDraw(board) else int(whoWon(board))
        positional_lead = get_positional_lead(board=board, heuristic_value=heuristic_value)
        positional_score = get_positional_score(board=board, result=result, positional_lead=positional_lead, local_eval=heuristic_value)

        evaluated_boards[board_key] = (heuristic_value, result, positional_lead, positional_score)

    with open(file_path, 'w') as f:
        for board_key, board_information in evaluated_boards.items():
            f.write(f"{board_key.hex()}:{board_information}\n")

# Run
# generate_winning_boards('backend/agents/hashes/hash_winning_boards.txt')
# generate_winning_results_boards('backend/agents/hashes/hash_winning_results_boards.txt')
# generate_eval_boards('backend/agents/hashes/hash_evaluated_boards.txt')
# generate_eval_boards_v2('backend/agents/hashes/hash_evaluated_boards_v2.txt')
# generate_eval_boards_v3('backend/agents/hashes/hash_evaluated_boards_v3.txt')
# generate_local_boards_info('backend/agents/hashes/hash_boards_information.txt')
# generate_results_board_eval('backend/agents/hashes/hash_results_board_eval.txt')
# generate_draw_boards('backend/agents/hashes/hash_draw_boards.txt')
# generate_draw_results_boards('backend/agents/hashes/hash_draw_results_boards.txt')
# generate_over_boards('backend/agents/hashes/hash_over_boards.txt')
# generate_blizzard_over_boards('backend/agents/hashes/hash_blizzard_over_boards.txt')
generate_blizzard_winning_boards('backend/agents/hashes/hash_blizzard_winning_boards.txt')
# generate_move_boards('backend/agents/hashes/hash_move_boards.txt')
# generate_winnable_boards('backend/agents/hashes/hash_winnable_boards_by_one.txt', 1)
# generate_winnable_boards('backend/agents/hashes/hash_winnable_boards_by_minus_one.txt', -1)

results_12 = np.array([[1, 0, -1],
                        [-1, 2, 1],
                        [-1, 1, -1]]) # draw
