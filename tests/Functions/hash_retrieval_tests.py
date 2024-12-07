import numpy as np
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional
from typing import Tuple, List, Union, Dict, Set, Any
import ast
import time

# el goat
EMPTY_BOARD = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
CENTER_ONLY_BOARD = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
CENTER_ONLY_ENEMY_BOARD = np.array([[0, 0, 0], [0, -1, 0], [0, 0, 0]])
CENTER_ONLY_EVAL = 0.35

def isWon(subboard):
    # TIMEIT APPROVED ✅
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

def isFullGlobal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns True if the board is full, False otherwise, works only for 9x9 global boards '''
    return (np.count_nonzero(board) == 81)

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
    """
    score = 0
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

    return round(score, 2)

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
    Returns a toned down balance if both have winning threat
    '''
    score = 0
    player1_threat = False
    player2_threat = False
    
    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if detectDouble((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if detectDouble((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if detectDouble((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
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
            return round((final_score + 0.1), 2)
        else:
            return round((final_score - 0.1), 2)

    return round(score, 2)

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
    player1_threat = False
    player2_threat = False

    # Rows
    row1_eval = advanced_line_eval((local_board[0, 0], local_board[0, 1], local_board[0, 2]))
    if detectDouble((local_board[0, 0], local_board[0, 1], local_board[0, 2])):
        player1_threat |= row1_eval > 0
        player2_threat |= row1_eval < 0
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = advanced_line_eval((local_board[1, 0], local_board[1, 1], local_board[1, 2]))
    if detectDouble((local_board[1, 0], local_board[1, 1], local_board[1, 2])):
        player1_threat |= row2_eval > 0
        player2_threat |= row2_eval < 0
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = advanced_line_eval((local_board[2, 0], local_board[2, 1], local_board[2, 2]))
    if detectDouble((local_board[2, 0], local_board[2, 1], local_board[2, 2])):
        player1_threat |= row3_eval > 0
        player2_threat |= row3_eval < 0
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = advanced_line_eval((local_board[0, 0], local_board[1, 0], local_board[2, 0]))
    if detectDouble((local_board[0, 0], local_board[1, 0], local_board[2, 0])):
        player1_threat |= col1_eval > 0
        player2_threat |= col1_eval < 0
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = advanced_line_eval((local_board[0, 1], local_board[1, 1], local_board[2, 1]))
    if detectDouble((local_board[0, 1], local_board[1, 1], local_board[2, 1])):
        player1_threat |= col2_eval > 0
        player2_threat |= col2_eval < 0
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = advanced_line_eval((local_board[0, 2], local_board[1, 2], local_board[2, 2]))
    if detectDouble((local_board[0, 2], local_board[1, 2], local_board[2, 2])):
        player1_threat |= col3_eval > 0
        player2_threat |= col3_eval < 0
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = advanced_line_eval((local_board[0, 0], local_board[1, 1], local_board[2, 2]))
    if detectDouble((local_board[0, 0], local_board[1, 1], local_board[2, 2])):
        player1_threat |= diagTB_eval > 0
        player2_threat |= diagTB_eval < 0
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = advanced_line_eval((local_board[2, 0], local_board[1, 1], local_board[0, 2]))
    if detectDouble((local_board[2, 0], local_board[1, 1], local_board[0, 2])):
        player1_threat |= diagBT_eval > 0
        player2_threat |= diagBT_eval < 0
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        final_score = score * 0.75
        return round(final_score, 2)
    
    final_score = round(score, 2)
    return final_score

def isFull(board):
    return np.count_nonzero(board == 0) == 0

def isPlayable(board):
    ''' Returns True if the local 3x3 board is still playable '''
    return not isFull(board) and not isWon(board)

def isOver(board):
    return isFull(board) or isWon(board)

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

def hex_to_board(hex_str):
    """
    Convert a hex string back into a 3x3 NumPy array representing a board with values -1, 0, 1, and 2.
    
    Args:
    - hex_str (str): Hexadecimal string representing the board.

    Returns:
    - np.array: 3x3 NumPy array with values -1, 0, 1, and 2.
    """
    # Convert hex string to bytes
    byte_data = bytes.fromhex(hex_str)
    
    # Convert bytes to a flat list of integers
    int_list = list(byte_data)
    
    # Map integers back to board values
    board = np.array([i - 1 for i in int_list]).reshape(3, 3)
    
    return board

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


class RetrievalAgent:
    def __init__(self):
        # Initialize the dictionaries before loading data
        self.hash_winning_boards = {}
        self.hash_eval_boards = {}
        self.hash_eval_v2_boards = {}
        self.hash_eval_v3_boards = {}
        self.hash_boards_information = {}
        self.hash_results_boards = {}
        self.hash_draw_boards = {}
        self.hash_over_boards = {}
        self.hash_winnable_boards_by_one = {}
        self.hash_winnable_boards_by_minus_one = {}
        self.hash_HyphenNumeric_boards = {}
        self.hash_HyphenNumeric_boards_rival = {}
        self.hash_winning_results_boards = {}
        self.hash_draw_results_boards = {}
        
        self.hash_blizzard_over_boards = {}
        self.hash_blizzard_winning_boards = {}
        self.hash_blizzards_eval_boards = {}

        # Load both winning boards and evaluated boards during initialization
        self.load_winning_boards('backend/agents/hashes/hash_winning_boards.txt')
        self.load_winning_results_boards('backend/agents/hashes/hash_winning_results_boards.txt')
        self.load_draw_results_boards('backend/agents/hashes/hash_draw_results_boards.txt')
        self.load_evaluated_boards('backend/agents/hashes/hash_evaluated_boards.txt')
        self.load_evaluated_v2_boards('backend/agents/hashes/hash_evaluated_boards_v2.txt')
        self.load_evaluated_v3_boards('backend/agents/hashes/hash_evaluated_boards_v3.txt')
        self.load_boards_info('backend/agents/hashes/hash_boards_information.txt')
        self.load_results_board_eval('backend/agents/hashes/hash_results_board_eval.txt')
        self.load_drawn_boards('backend/agents/hashes/hash_draw_boards.txt')
        # self.load_move_boards('backend/agents/hashes/hash_move_boards.txt')
        self.load_over_boards('backend/agents/hashes/hash_over_boards.txt')
        self.load_blizzard_over_boards('backend/agents/hashes/hash_blizzard_over_boards.txt')
        self.load_blizzard_winning_boards('backend/agents/hashes/hash_blizzard_winning_boards.txt')
        self.load_winnable_boards_one('backend/agents/hashes/hash_winnable_boards_by_one.txt')
        self.load_winnable_boards_minus_one('backend/agents/hashes/hash_winnable_boards_by_minus_one.txt')
        self.load_HyphenNumeric_boards('backend/agents/hashes/hash_HyphenNumeric_boards.txt')
        self.load_HyphenNumeric_boards_rival('backend/agents/hashes/hash_HyphenNumeric_boards_rival.txt')

    # Winning Loaders
    def load_winning_boards(self, file_path):
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

    def load_winning_results_boards(self, file_path):
        ''' Load the winning boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, winner = line.strip().split(':')
                    self.hash_winning_results_boards[bytes.fromhex(board_hex)] = int(winner)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

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

    # Evaluation Loaders
    def load_evaluated_boards(self, file_path):
        """
        Load the evaluated boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with its heuristic value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result = board_info_tuple
                    self.hash_eval_boards[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_evaluated_v2_boards(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result = board_info_tuple
                    self.hash_eval_v2_boards[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_evaluated_v3_boards(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result = board_info_tuple
                    self.hash_eval_v3_boards[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_boards_info(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result, positional_lead, positional_score = board_info_tuple
                    self.hash_boards_information[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result), int(positional_lead), float(positional_score))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_results_board_eval(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, heuristic_value = line.strip().split(':')
                    self.hash_results_boards[bytes.fromhex(board_hex)] = float(heuristic_value)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    # Draw Loaders
    def load_drawn_boards(self, file_path):
        """
        Load the drawn boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with a boolean value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, is_draw = line.strip().split(':')
                    self.hash_draw_boards[bytes.fromhex(board_hex)] = (is_draw == 'True')
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Drawn boards will not be loaded.")

    def load_draw_results_boards(self, file_path):
        ''' Load the winning boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, is_draw = line.strip().split(':')
                    self.hash_draw_results_boards[bytes.fromhex(board_hex)] = (is_draw == 'True')
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

    # Hyphen Numeric Loaders
    def load_HyphenNumeric_boards(self, file):
        ''' Loads the winnable boards from a file and stores them in a dictionary. 
        Each board state is stored as a key (board representated by 2 frozensets with each player's pieces, and the board_to_play).
        They are stored as (board_state, board_to_play) : best_move (represented by a tuple of ints)
        '''
        with open(file, 'r') as f:
            for line in f:
                self.parse_and_store_board_line(line)
                
    def load_HyphenNumeric_boards_rival(self, file):
        ''' Loads the winnable boards from a file and stores them in a dictionary. 
        Each board state is stored as a key (board representated by 2 frozensets with each player's pieces, and the board_to_play).
        They are stored as (board_state, board_to_play) : best_move (represented by a tuple of ints)
        '''
        with open(file, 'r') as f:
            for line in f:
                self.parse_and_store_board_line(line, rival_start=True)

    # Other Loaders
    def load_over_boards(self, file_path):
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

    def load_blizzard_over_boards(self, file_path):
        ''' Loads the over boards from a file and stores them in a dictionary 
        Each board's state is stored as a key (using its byte representation)
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex = line.strip()
                    self.hash_blizzard_over_boards[bytes.fromhex(board_hex)] = True
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Over boards will not be loaded.")

    def load_blizzard_winning_boards(self, file_path):
        ''' Loads the winning boards from a file and stores them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, winner = line.strip().split(':')
                    self.hash_blizzard_winning_boards[bytes.fromhex(board_hex)] = int(winner)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

    # Winner Getters
    def get_winner_hash(self, board):
        """
        Retrieve the winner of a board from the preloaded dictionary of winning boards.
        Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
        """
        board_key = board.tobytes()
        return self.hash_winning_boards.get(board_key, 0)

    def get_winning_result_hash(self, board):
        ''' Retrieve the winner of a board from the preloaded dictionary of winning boards '''
        board_key = board.tobytes()
        return self.hash_winning_results_boards.get(board_key, 0)

    def get_winnable_by_one_hash(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_one.get(board_key, set())

    def get_winnable_by_minus_one_hash(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_minus_one.get(board_key, set())

    # Eval Getters
    def get_eval_hash(self, board):
        """
        Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards.
        If the board is not in the dictionary, return None (or handle it as needed).
        """
        board_key = board.tobytes()
        local_eval, _ = self.hash_eval_boards.get(board_key, None)
        if local_eval is None:
            raise ValueError(f"Board {board} not found in evaluated eval boards.")
        return local_eval

    def get_eval_v2_hash(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        local_eval_v2, _ = self.hash_eval_v2_boards.get(board_key, None)
        if local_eval_v2 is None:
            raise ValueError(f"Board {board} not found in evaluated V2 boards.")
        return local_eval_v2
    
    def get_eval_v3_hash(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        local_eval_v3, _ = self.hash_eval_v3_boards.get(board_key, None)
        if local_eval_v3 is None:
            raise ValueError(f"Board {board} not found in evaluated V3 boards.")
        return local_eval_v3

    def get_eval_result_v1_hash(self, board):
        ''' Retrieve the result of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        _, result = self.hash_eval_boards.get(board_key, None)
        if result is None:
            raise ValueError(f"Board {board} not found in evaluated boards.")
        return result
    
    def get_eval_result_v2_hash(self, board):
        ''' Retrieve the result of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        _, result = self.hash_eval_v2_boards.get(board_key, None)
        if result is None:
            raise ValueError(f"Board {board} not found in evaluated V2 boards.")
        return result
    
    def get_eval_result_v3_hash(self, board):
        ''' Retrieve the result of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        _, result = self.hash_eval_v3_boards.get(board_key, None)
        if result is None:
            raise ValueError(f"Board {board} not found in evaluated V3 boards.")
        return result

    def get_board_info(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        score, result, positional_lead, positional_score = self.hash_boards_information.get(board_key, None)
        if score is None or result is None or positional_lead is None or positional_score is None:
            raise ValueError(f"Board {board} not found in evaluated global boards. Info was {score}, {result}, {positional_lead}, {positional_score}")
        return score, result, positional_lead, positional_score

    def get_results_board_eval(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        hex_key = board_key.hex()
        results_eval = self.hash_results_boards.get(board_key, None)
        if results_eval is None:
            raise ValueError(f"Board not found in results boards!, its hex key was {hex_key}. The board was\n{board}")
        return results_eval

    # Draw Getters
    def get_draw_hash(self, board):
        """
        Retrieve the draw status of a board from the preloaded dictionary of drawn boards.
        Returns True if the board is a draw, False otherwise.
        """
        board_key = board.tobytes()
        return self.hash_draw_boards.get(board_key, False)

    def get_draw_result_hash(self, board):
        ''' Retrieve the winner of a board from the preloaded dictionary of winning boards '''
        board_key = board.tobytes()
        return self.hash_draw_results_boards.get(board_key, False)

    # Hyphen Numeric Getters
    def get_HyphenNumeric_hash(self, board, board_to_play):
        ''' Returns the best move for the given HyphenNumeric board '''
        key, reverse_symmetry_instructions = self.get_HyphenNumeric_parameters(board, board_to_play)
        best_move_raw = self.hash_HyphenNumeric_boards.get(key, None)
        best_move_processed = self.counter_transform_move(best_move_raw, reverse_symmetry_instructions)
        return best_move_processed

    def get_HyphenNumeric_hash_rival(self, board, board_to_play):
        ''' Returns the best move for the given HyphenNumeric board '''
        key, reverse_symmetry_instructions = self.get_HyphenNumeric_parameters(board, board_to_play, rival_start=True)
        best_move_raw = self.hash_HyphenNumeric_boards_rival.get(key, None)
        best_move_processed = self.counter_transform_move(best_move_raw, reverse_symmetry_instructions)
        return best_move_processed

    # Other Getters
    def get_over_hash(self, board):
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_over_boards.get(board_key, False)

    def get_blizzard_over_hash(self, board):
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_blizzard_over_boards.get(board_key, False)
    
    def get_blizzard_winner_hash(self, board):
        ''' Retrieve the winner of a board from the preloaded dictionary of winning boards '''
        board_key = board.tobytes()
        return self.hash_blizzard_winning_boards.get(board_key, 0)

    def get_playable_hash(self, board):
        ''' Returns True if the board is playable, False otherwise '''
        return not self.get_over_hash(board)

    # Move Hashing Auxiliaries Below!
    # Rotations & Reflections 2D
    def rotate_coordinates_2d(self, coordinates: Union[Tuple[int, int], None], rotation_times: int):
        ''' Rotate the board to play by 90 degrees * times, coordinates must be either 0, 1, 2
        So rotations are done performing the (2 - coordinate) operation for the corresponding axis '''
        if coordinates is None:
            return None
        
        a, b = coordinates
        rotation_times %= 4
        
        if rotation_times == 0:
            # 0° rotation
            return a, b
        
        elif rotation_times == 1:
            # 90° rotation
            return b, 2 - a
        
        elif rotation_times == 2:
            # 180° rotation
            return 2 - a, 2 - b
        
        elif rotation_times == 3:
            # 270° rotation
            return 2 - b, a

        raise ValueError(f"Invalid rotation times: {rotation_times}??")

    def reverse_rotation_2d(self, coordinates, rotation_times):
        ''' Reverse the rotation of the coordinates '''
        if coordinates is None:
            return None
        
        a, b = coordinates
        rotation_times %= 4
        
        if rotation_times == 0:
            # 0° rotation
            return a, b
        
        elif rotation_times == 1:
            # 90° rotation
            return 2 - b, a
        
        elif rotation_times == 2:
            # 180° rotation
            return 2 - a, 2 - b
        
        elif rotation_times == 3:
            # 270° rotation
            return b, 2 - a
        
        raise ValueError(f"Invalid rotation times: {rotation_times}??")

    def reflect_coordinates_2d(self, move, reflection_type):
        # Normalize reflection_type to lowercase to handle different cases
        reflection_type = reflection_type.lower()
        a, b = move
        
        if reflection_type == 'none':
            # No reflection
            return a, b
        elif reflection_type == 'horizontal':
            # Horizontal reflection (across the middle row)
            return 2 - a, b
        elif reflection_type == 'vertical':
            # Vertical reflection (across the middle column)
            return a, 2 - b
        elif reflection_type == 'diagonal':
            # Diagonal reflection (top-left to bottom-right)
            return b, a
        elif reflection_type == 'anti-diagonal':
            # Anti-diagonal reflection (top-right to bottom-left)
            return 2 - b, 2 - a
        else:
            raise ValueError(f"Invalid reflection type: {reflection_type}")

    def reverse_reflection_2d(self, move, reflection_type):
        # Applying the same reflection again undoes it (reflections are self-inverse)
        return self.reflect_coordinates_2d(move, reflection_type)

    # Rotations & Reflections 4D
    def rotate_coordinates_4d(self, coordinates: Union[Tuple[int, int, int, int], None], rotation_times: int):
        if coordinates is None:
            return None
        a, b, c, d = coordinates
        rotation_times %= 4
        
        if rotation_times == 0:
            # No rotation
            return a, b, c, d
        elif rotation_times == 1:
            # 90-degree rotation: rotate first two coordinates (a, b) and last two coordinates (c, d)
            return c, d, a, b
        elif rotation_times == 2:
            # 180-degree rotation: swap (a, b) and (c, d)
            return 2 - a, 2 - b, 2 - c, 2 - d
        elif rotation_times == 3:
            # 270-degree rotation: rotate in the opposite direction (c, d) and (a, b)
            return d, c, b, a
        else:
            raise ValueError(f"Invalid rotation time: {rotation_times}")

    def reverse_rotation_4d(self, move, rotation_times):
        # Reverse the rotation by performing the opposite of the given rotation.
        return self.rotate_coordinates_4d(move, (4 - rotation_times) % 4)

    def reflect_coordinates_4d(self, move, reflection_type):
        reflection_type = reflection_type.lower()
        a, b, c, d = move

        if reflection_type == 'none':
            # No reflection
            return a, b, c, d
        elif reflection_type == 'horizontal':
            # Reflect across the first two coordinates (flip a, b)
            return 2 - a, 2 - b, c, d
        elif reflection_type == 'vertical':
            # Reflect across the last two coordinates (flip c, d)
            return a, b, 2 - c, 2 - d
        elif reflection_type == 'diagonal':
            # Reflect across the plane swapping (a, c) and (b, d)
            return c, d, a, b
        elif reflection_type == 'anti-diagonal':
            # Reflect across the plane swapping (b, d) and (a, c)
            return d, c, b, a
        else:
            raise ValueError(f"Invalid reflection type: {reflection_type}")

    def reverse_reflection_4d(self, move, axis):
        ''' Apply inverse reflection to a move '''
        return self.reflect_coordinates_4d(move, axis)

    # DEPRECATED Board Symmetry Methods
    def rotate_board(self, board, times):
        ''' Rotate the board by 90 degrees * times '''
        for _ in range(times):
            board = np.rot90(board, axes=(2, 3))
        return board

    def reflect_board(self, board, axis):
        ''' Reflects the board along the specified axis '''
        if axis == "none":
            return board
        elif axis == "horizontal":
            return np.flip(board, axis=2)
        elif axis == "vertical":
            return np.flip(board, axis=3)
        elif axis == "diagonal":
            return np.flip(board, axis=(2, 3))
        elif axis == "anti-diagonal":
            return np.flip(board, axis=(1, 2))

    # Hyphen Numeric Hash Processing Functions
    def get_HyphenNumeric_parameters(self, board: np.array, board_to_play: Union[Tuple[int, int], None], rival_start=False):
        ''' 
        Returns the key for the HyphenNumeric dictionary, checking all symmetrical variations
        to match the stored key format, and also outputs reverse transformations.
        '''
        # Rotations
        for rotations in range(4):  # Four rotations
            processed_moves_1 = set()
            processed_moves_2 = set()
            raw_moves_player_1, raw_moves_player_2 = self.board_to_moves_list(board)
            
            # Move Rotation
            for move in raw_moves_player_1:
                if len(move) != 4:
                    raise ValueError(f"Invalid move player 1: {move}")
                rotated_move = self.rotate_coordinates_4d(move, rotations)
                processed_moves_1.add(rotated_move)
                
            for move in raw_moves_player_2:
                if len(move) != 4:
                    raise ValueError(f"Invalid move player -1: {move}")
                rotated_move = self.rotate_coordinates_4d(move, rotations)
                processed_moves_2.add(rotated_move)
            
            # Board to Play
            rotated_board_to_play = self.rotate_coordinates_2d(coordinates=board_to_play, rotation_times=rotations)

            # Reflections
            for reflection in ['none', 'horizontal', 'vertical', 'diagonal', 'anti-diagonal']:
                final_moves_1 = set()
                final_moves_2 = set()
                
                # Move Reflection
                for move in processed_moves_1:
                    if len(move) != 4:
                        raise ValueError(f"Invalid move p1 rotated: {move}")
                    reflected_move = self.reflect_coordinates_4d(move, reflection)
                    final_moves_1.add(reflected_move)
                    
                for move in processed_moves_2:
                    if len(move) != 4:
                        raise ValueError(f"Invalid move p2 rotated: {move}")
                    reflected_move = self.reflect_coordinates_4d(move, reflection)
                    final_moves_2.add(reflected_move)
                
                # Board to Play
                reflected_board_to_play = self.reflect_coordinates_2d(rotated_board_to_play, reflection)
                moves_tuple = (final_moves_1, final_moves_2)
                board_key_player_1, board_key_player_2 = self.list_of_tuples_to_HyphenNumeric_str_frozensets(moves_tuple)
                                
                # Construct the hash key with this version
                key = ((board_key_player_1, board_key_player_2), reflected_board_to_play)
                # print(Fore.LIGHTGREEN_EX + f"\nWhile the transposition table looks as such:\n{self.hash_HyphenNumeric_boards}" + Style.RESET_ALL)
                # print(Fore.LIGHTMAGENTA_EX + f"Attempting the key: \n{key}\nwhere rotation = {rotations} and reflection = {reflection}" + Style.RESET_ALL)

                # Check key in hash
                if not rival_start:
                    if key in self.hash_HyphenNumeric_boards:
                        return key, (rotations, reflection)  
                else:
                    if key in self.hash_HyphenNumeric_boards_rival:
                        return key, (rotations, reflection)
                
        return None, None

    def counter_transform_move(self, move: Tuple[int, int, int, int], transformation: Tuple):
        ''' Reverse the transformation to retrieve the original move coordinates '''
        if not transformation:
            return move
        
        rotations, reflection = transformation
        counter_move = move

        # Apply inverse reflection first
        if reflection:
            counter_move = self.reverse_reflection_4d(counter_move, reflection)

        # Apply inverse rotation
        if rotations:
            counter_move = self.reverse_rotation_4d(counter_move, rotations)

        return counter_move

    def board_to_moves_list(self, board) -> Tuple[Tuple[Tuple[int, int, int, int], ...], Tuple[Tuple[int, int, int, int], ...]]:
        ''' Takes a board, and returns 2 tuples, each with N tuples inside '''
        player1_pieces = []
        player_minus1_pieces = []

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        if board[i, j, k, l] == 1:
                            player1_pieces.append((i, j, k, l))
                        elif board[i, j, k, l] == -1:
                            player_minus1_pieces.append((i, j, k, l))

        return (player1_pieces, player_minus1_pieces)

    def list_of_tuples_to_HyphenNumeric_str_frozensets(self, piece_lists_tuple):
        ''' Convert the list of tuples to the HyphenNumeric format '''
        player_1, player_minus1 = piece_lists_tuple
        player_1_list, player_minus1_list = [], []
        
        for move in player_1:
            i, j, k, l = move
            player_1_list.append(f"{i}_{j}_{k}_{l}")
            
        for move in player_minus1:
            i, j, k, l = move
            player_minus1_list.append(f"{i}_{j}_{k}_{l}")
            
        return (frozenset(player_1_list), frozenset(player_minus1_list))

    def get_quick_board_key(self, board):
        moves1, moves_minus1 = self.board_to_moves_list(board)
        return self.list_of_tuples_to_HyphenNumeric_str_frozensets((moves1, moves_minus1))

    def parse_and_store_board_line(self, line, rival_start=False):
        ''' Parse a line from the file and store the board and its best move '''
        # Get the data
        key_part, move_part = line.strip().split(" : ")
        
        # Board
        board_part, board_to_play_str = key_part.split(", ")
        if rival_start:
            board_key_part = self.parse_board_key_rival(board_part)
        else:
            board_key_part = self.parse_board_key(board_part)

        # Board to play
        if board_to_play_str == 'None':
            board_to_play = None
        else:
            board_to_play = tuple(map(int, board_to_play_str.split("_")))

        # Key is Ready
        full_key = (board_key_part, board_to_play)
        
        # Best Move
        best_move = tuple(map(int, move_part.split("_")))
        
        if rival_start:
            self.hash_HyphenNumeric_boards_rival[full_key] = best_move
        else:
            self.hash_HyphenNumeric_boards[full_key] = best_move

    def parse_board_key(self, board_str):
        ''' Convert the HyphenNumeric string back to a canonical key '''
        pieces = board_str.split("__")
        player1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 == 0)
        player_minus1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 != 0)

        # Build the frozenset for the key
        return frozenset(player1_pieces), frozenset(player_minus1_pieces)

    def parse_board_key_rival(self, board_str):
        ''' Convert the HyphenNumeric string back to a canonical key '''
        pieces = board_str.split("__")
        player1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 != 0)
        player_minus1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 == 0)

        # Build the frozenset for the key
        return frozenset(player1_pieces), frozenset(player_minus1_pieces)


# TESTING CODE BEGINS HERE
board_empty = np.array([[0, 0, 0], 
                        [0, 0, 0], 
                        [0, 0, 0]])
board_center_only = np.array([[0, 0, 0],
                            [0, 1, 0],
                            [0, 0, 0]])
board_center_only_another = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
if not np.array_equal(board_center_only, board_center_only_another):
    raise ValueError("Center only board is not equal to center only another")
board_center_enemy_only = np.array([[0, 0, 0], [0, -1, 0], [0, 0, 0]])

# Example usage:
agent = RetrievalAgent()

# Test boards setup
board_1 = np.array([[1, 1, 1],
                    [0, -1, -1],
                    [0, 0, -1]])  # Player 1 wins on the top row

board_2 = np.array([[0, -1, 1],
                    [0, 1, -1],
                    [1, 0, -1]])  # Player 1 wins on the diagonal

board_2b = np.array([[-1, -1, 1],
                    [-1, 1, -1],
                    [1, -1, -1]])  # Player 1 wins on the diagonal

board_3 = np.array([[-1, -1, 0],
                    [1, 1, 1],
                    [0, -1, 0]])  # Player 1 wins on the middle row

board_4 = np.array([[0, -1, 1],
                    [-1, -1, 1],
                    [1, -1, 0]])  # Player -1 wins on the middle column

board_5 = np.array([[-1, 1, 0],
                    [1, -1, 0],
                    [1, 0, -1]])  # Player -1 wins on the diagonal

board_6 = np.array([[-1, -1, -1],
                    [1, 1, 0],
                    [0, 1, 0]])  # Player -1 wins on the top row

board_7 = np.array([[1, -1, -1],
                    [1, -1, -1],
                    [0, 1, 1]])  # No winner yet

board_8 = np.array([[1, -1, 1],
                    [1, -1, -1],
                    [-1, 1, 1]])  # Draw (no more moves possible)

board_9 = np.array([[1, 1, 0],
                    [-1, -1, 0],
                    [0, 0, 0]])  # Not a win yet, but close, advanced eval is 0.6 - 0.6 - 0.15 = -0.15

board_10 = np.array([[0, 0, 0],
                    [1, 1, 0],
                    [-1, -1, 0]])  # Another close board without a winner, advanced eval is 0.6 + 0.15 - 0.6 = 0.15

board_11 = np.array([[1, -1, 1],
                    [-1, -1, 1],
                    [0, 1, -1]])  # Secured Draw (will always be Draw)

board_12 = np.array([[-1, 0, 1],
                    [1, -1, -1],
                    [-1, 1, 1]]) # Secured Draw (will always be Draw)

board_13 = np.array([[1, 0, 1],
                    [1, 0, 0],
                    [0, 1, 1]]) # winnable by 1 in (0, 1), (1, 1), (1, 2), (2, 0)

board_14 = np.array([[0, 0, 0],
                    [-1, -1, 0],
                    [-1, -1, 0]]) # winnable by -1 in (0, 0), (0, 1), (0, 2), (1, 2), (2, 2)

board_15 = np.array([[-1, -1, 0],
                    [-1, 0, 1],
                    [0, 1, 1]]) # winnable by 1 in (0, 2), (2, 0) || winnable by -1 in (0, 2), (2, 0)

# 16, 17, 18, 19 prepare interesting for board info positional stuff
board_16 = np.array([[-1, 0, 1],
                    [0, 0, -1],
                    [1, -1, 0]]) # 1 is better! (slight)

board_17 = np.array([[0, 0, -1],
                    [0, 1, -1],
                    [-1, -1, 1]]) # 1 is better! (slight)

board_18 = np.array([[1, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]])

board_19 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]])

board_20 = np.array([[1, 1, 0],
                    [0, 0, 0],
                    [-1, 0, 0]]) # Balance = D1 = 0.6

board_21 = np.array([[1, 1, 0],
                    [0, -1, 1],
                    [0, -1, 1]]) # Balane = D1 = 0.6

board_22 = np.array([[1, 1, 0],
                    [0, 0, 0],
                    [0, -1, 0]]) # Balance = D1 + S1 = 0.74

board_23 = np.array([[1, 1, 0],
                    [0, -1, 0],
                    [0, -1, 1]]) # Balance = D1 - S1 = 0.46

board_24 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]])

board_25 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]])

board_26 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]])

board_27 = np.array([[1, 1, 0],
                    [1, 1, 0],
                    [0, 0, 0]]) # highest balance!, should be equal to 29, 5 doubles = 3

board_28 = np.array([[-1, -1, 0],
                    [-1, -1, 0],
                    [0, 0, 0]]) # lowest balance!, should be opposite of 27, 5 doubles = -3

board_29 = np.array([[1, 0, 1],
                    [0, 0, 0],
                    [1, 0, 1]]) # highest balance!, should be equal to 27, 5 doubles = 3

board_30 = np.array([[-1, 0, -1],
                    [0, 0, 0],
                    [-1, 0, -1]]) # lowest balance!, should be opposite of 29, 5 doubles = -3

board_31 = np.array([[1, 0, 1],
                    [1, 0, 1],
                    [0, 0, 0]]) # high but not highest, should be 4 doubles

board_32 = np.array([[-1, 0, -1],
                    [-1, 0, -1],
                    [0, 0, 0]]), # low but not lowest, should be 4 neg doubles

board_33 = np.array([[1, -1, 1],
                    [-1, 0, -1],
                    [1, -1, 1]]) # should be 0

board_34 = np.array([[-1, 1, -1],
                    [1, 0, 1],
                    [-1, 1, -1]]) # should be 0

board_35 = np.array([[0, 0, 0],
                    [1, 0, 0],
                    [0, 0, 0]]) # lower than board18

board_36 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [0, 0, -1]]) # equal to -board18

board_37 = np.array([[0, 1, 0],
                    [1, 0, 0],
                    [0, 0, 0]]) # better than single but lower than 38

board_38 = np.array([[0, 0, 0],
                    [1, 0, 0],
                    [0, 0, 1]]) # kinda low, but higher than 37

board_39 = np.array([[0, 0, 0],
                    [1, 0, 1],
                    [0, 0, 0]]) # double < eval < 2*double, 2 singles but center-need (L1)

board_40 = np.array([[0, -1, 0],
                    [0, 0, 0],
                    [0, -1, 0]]) # == -b39 (L1)

board_41 = np.array([[0, 0, 1],
                    [0, 0, 0],
                    [1, 0, 0]]) # double < eval < 2.5*double, 4 singles but center-need double (L2)

board_42 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [1, 0, 1]]) # double < eval < 2.5*double, 4 singles no center-need double! (L3)

board_43 = np.array([[0, 0, 0],
                    [1, 1, 0],
                    [0, 0, 0]]) # double < eval < 2.5*double, 4 singles got the center! (L4)

board_44 = np.array([[0, 0, 0],
                    [0, 1, 0],
                    [1, 0, 0]]) # double < eval < 2.5*double, 5 singles got the center! (L5)

# board 45 has two doubles but low value
board_45 = np.array([[-1, 1, -1],
                    [0, 0, 0],
                    [0, 1, 1]]) # two doubles

board_46 = np.array([[0, 0, -1],
                    [1, 0, 1],
                    [0, 0, 0]]) # bad double

board_47 = np.array([[0, 1, 0],
                    [1, 0, 0],
                    [0, 0, 1]]) # great singles

# Results Boards (contain 2s)
results_1 = np.array([[2, 1, 1],
                    [2, -1, -1],
                    [2, 2, 2]]) # should be 0

results_2 = np.array([[0, 1, 1],
                    [2, -1, -1],
                    [0, 0, 0]]) # should be 0.45

results_3 = np.array([[0, 0, 0],
                    [0, 2, 0],
                    [0, 0, 0]]) # should be 0

results_4 = np.array([[0, 0, 0],
                    [0, 2, 0],
                    [-1, 0, 1]]) # should be 0

results_5 = np.array([[0, 0, 0],
                    [0, 0, 0],
                    [1, 2, 1]]) # should be 0.15 * 4 = 0.6

results_6 = np.array([[0, -1, 1],
                    [2, 2, 1],
                    [1, 2, 1]]) # winner 1

results_7 = np.array([[1, 1, 2],
                    [-1, -1, -1],
                    [1, 2, 1]]) # winner -1

results_8 = np.array([[2, 2, 2],
                    [2, 2, 2],
                    [2, 2, -1]]) # draw

results_9 = np.array([[1, 1, 2],
                    [2, 2, 1],
                    [1, 2, 1]]) # draw

results_10 = np.array([[2, 2, 2],
                    [2, 2, 2],
                    [2, 2, 0]]) # draw

results_11 = np.array([[1, 0, 1],
                    [-1, 2, -1],
                    [-1, 1, -1]]) # not draw (edge case)

results_12 = np.array([[1, 0, -1],
                    [-1, 2, 1],
                    [-1, 1, -1]]) # draw

results_13 = np.array([[0, 0, 2],
                        [2, 2, 0],
                        [0, 2, 0]]) # draw (all lines blocked)


super_board_1 = np.zeros((3, 3, 3, 3), dtype=int)
super_board_1[0, 0, 0, 0] = 1
super_board_1[0, 0, 1, 2] = -1
super_board_1[1, 2, 1, 1] = 1
super_board_1[1, 1, 2, 0] = -1
btp1 = (2, 0)
bestmove1 = (2, 0, 0, 2)

# Print Moves for all 8 symmetries
# print(Style.BRIGHT + Fore.CYAN)
# print(f"{agent.board_to_moves_list(super_board_1)} is the key for Board 1 Original hyphen numeric")
# print(Style.RESET_ALL)

# Try with 180 Rotation
super_board_2 = np.zeros((3, 3, 3, 3), dtype=int)
super_board_2[2, 2, 2, 2] = 1
super_board_2[2, 2, 1, 0] = -1
super_board_2[1, 0, 1, 1] = 1
super_board_2[1, 1, 0, 2] = -1
btp2 = (0, 2)
bestmove2 = (0, 2, 2, 0)

super_board_center = np.zeros((3, 3, 3, 3), dtype=int)
super_board_center[1, 1, 1, 1] = 1

# print(Style.BRIGHT + Fore.YELLOW + f"\nThe HyphenNumeric Hash currently looks like this:\n{agent.hash_HyphenNumeric_boards}\n" + Style.RESET_ALL)

b1_eval, b1_eval_v2, b1_eval_v3, b1_eval_glob = localBoardEval(board_1), localBoardEval_v2(board_1), localBoardEval_v3(board_1), local_evaluation(board_1)
b2_eval, b2_eval_v2, b2_eval_v3, b2_eval_glob = localBoardEval(board_2), localBoardEval_v2(board_2), localBoardEval_v3(board_2), local_evaluation(board_2)
b3_eval, b3_eval_v2, b3_eval_v3, b3_eval_glob = localBoardEval(board_3), localBoardEval_v2(board_3), localBoardEval_v3(board_3), local_evaluation(board_3)
b4_eval, b4_eval_v2, b4_eval_v3, b4_eval_glob = localBoardEval(board_4), localBoardEval_v2(board_4), localBoardEval_v3(board_4), local_evaluation(board_4)
b5_eval, b5_eval_v2, b5_eval_v3, b5_eval_glob = localBoardEval(board_5), localBoardEval_v2(board_5), localBoardEval_v3(board_5), local_evaluation(board_5)
b6_eval, b6_eval_v2, b6_eval_v3, b6_eval_glob = localBoardEval(board_6), localBoardEval_v2(board_6), localBoardEval_v3(board_6), local_evaluation(board_6)
b7_eval, b7_eval_v2, b7_eval_v3, b7_eval_glob = localBoardEval(board_7), localBoardEval_v2(board_7), localBoardEval_v3(board_7), local_evaluation(board_7)
b8_eval, b8_eval_v2, b8_eval_v3, b8_eval_glob = localBoardEval(board_8), localBoardEval_v2(board_8), localBoardEval_v3(board_8), local_evaluation(board_8)
b9_eval, b9_eval_v2, b9_eval_v3, b9_eval_glob = localBoardEval(board_9), localBoardEval_v2(board_9), localBoardEval_v3(board_9), local_evaluation(board_9)
b10_eval, b10_eval_v2, b10_eval_v3, b10_eval_glob = localBoardEval(board_10), localBoardEval_v2(board_10), localBoardEval_v3(board_10), local_evaluation(board_10)
b11_eval, b11_eval_v2, b11_eval_v3, b11_eval_glob = localBoardEval(board_11), localBoardEval_v2(board_11), localBoardEval_v3(board_11), local_evaluation(board_11)
b12_eval, b12_eval_v2, b12_eval_v3, b12_eval_glob = localBoardEval(board_12), localBoardEval_v2(board_12), localBoardEval_v3(board_12), local_evaluation(board_12)
r1_ev, r2_ev, r3_ev, r4_ev, r5_ev = results_board_eval(results_1), results_board_eval(results_2), results_board_eval(results_3), results_board_eval(results_4), results_board_eval(results_5)

# print("r1 eval is", r1_ev)
# print("r2 eval is", r2_ev)
# print("r3 eval is", r3_ev)
# print("r4 eval is", r4_ev)
# print("r5 eval is", r5_ev)

# region Eval Prints
# V1 Evals
# print(f"Eval Version 1 for Board 1 is {b1_eval}")
# print(f"Eval Version 1 for Board 2 is {b2_eval}")
# print(f"Eval Version 1 for Board 3 is {b3_eval}")
# print(f"Eval Version 1 for Board 4 is {b4_eval}")
# print(f"Eval Version 1 for Board 5 is {b5_eval}")
# print(f"Eval Version 1 for Board 6 is {b6_eval}")
# print(f"Eval Version 1 for Board 7 is {b7_eval}")
# print(f"Eval Version 1 for Board 8 is {b8_eval}")
# print(f"Eval Version 1 for Board 9 is {b9_eval}")
# print(f"Eval Version 1 for Board 10 is {b10_eval}")
# print(f"Eval Version 1 for Board 11 is {b11_eval}")
# print(f"Eval Version 1 for Board 12 is {b12_eval}")

# V2 Evals
# print(f"Eval Version 2 for Board 1 is {b1_eval_v2}")
# print(f"Eval Version 2 for Board 2 is {b2_eval_v2}")
# print(f"Eval Version 2 for Board 3 is {b3_eval_v2}")
# print(f"Eval Version 2 for Board 4 is {b4_eval_v2}")
# print(f"Eval Version 2 for Board 5 is {b5_eval_v2}")
# print(f"Eval Version 2 for Board 6 is {b6_eval_v2}")
# print(f"Eval Version 2 for Board 7 is {b7_eval_v2}")
# print(f"Eval Version 2 for Board 8 is {b8_eval_v2}")
# print(f"Eval Version 2 for Board 9 is {b9_eval_v2}")
# print(f"Eval Version 2 for Board 10 is {b10_eval_v2}")
# print(f"Eval Version 2 for Board 11 is {b11_eval_v2}")
# print(f"Eval Version 2 for Board 12 is {b12_eval_v2}")

# V3 Evals
# print(f"Eval Version 3 for Board 1 is {b1_eval_v3}")
# print(f"Eval Version 3 for Board 2 is {b2_eval_v3}")
# print(f"Eval Version 3 for Board 3 is {b3_eval_v3}")
# print(f"Eval Version 3 for Board 4 is {b4_eval_v3}")
# print(f"Eval Version 3 for Board 5 is {b5_eval_v3}")
# print(f"Eval Version 3 for Board 6 is {b6_eval_v3}")
# print(f"Eval Version 3 for Board 7 is {b7_eval_v3}")
# print(f"Eval Version 3 for Board 8 is {b8_eval_v3}")
# print(f"Eval Version 3 for Board 9 is {b9_eval_v3}")
# print(f"Eval Version 3 for Board 10 is {b10_eval_v3}")
# print(f"Eval Version 3 for Board 11 is {b11_eval_v3}")
# print(f"Eval Version 3 for Board 12 is {b12_eval_v3}")
# endregion
# Define Tests
def run_eval_hash_completion_tests(agent):
    for _ in range(1_000_000):
        random_board = np.random.randint(-1, 2, (3, 3), dtype=int)
        hash_value = agent.get_eval_hash(random_board)
        assert (hash_value is not None), Style.BRIGHT + Fore.RED + f"Test Failed! Hash Value for Board {random_board} is None"
        
    print("All Regular Eval Hash Completion tests passed successfully!")

def run_results_hash_completion_tests(agent):
    for _ in range(1_000_000):
        random_board = np.random.randint(-1, 2, (3, 3), dtype=int)
        hash_value = agent.get_results_board_eval(random_board)
        assert (hash_value is not None), Style.BRIGHT + Fore.RED + f"Test Failed! Hash Value for Board {random_board} is None"
        
    print("All Results Board Eval Hash Completion tests passed successfully!")

def run_blizzard_over_board_tests(agent):
    assert agent.get_blizzard_over_hash(results_1) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_1"
    assert agent.get_blizzard_over_hash(results_2) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for results_2"
    assert agent.get_blizzard_over_hash(results_3) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for results_3"
    assert agent.get_blizzard_over_hash(results_4) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for results_4"
    assert agent.get_blizzard_over_hash(results_5) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for results_5"
    assert agent.get_blizzard_over_hash(results_6) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_6"
    assert agent.get_blizzard_over_hash(results_7) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_7"
    assert agent.get_blizzard_over_hash(results_8) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_8"
    assert agent.get_blizzard_over_hash(results_9) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_9"
    assert agent.get_blizzard_over_hash(results_10) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for results_10"
    assert agent.get_blizzard_over_hash(results_11) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for results_11"
    assert agent.get_blizzard_over_hash(results_12) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_12"
    assert agent.get_blizzard_over_hash(results_13) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for results_13"
    
    assert agent.get_blizzard_over_hash(board_1) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for board_1"
    assert agent.get_blizzard_over_hash(board_2) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for board_2"
    assert agent.get_blizzard_over_hash(board_3) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for board_3"
    assert agent.get_blizzard_over_hash(board_4) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for board_4"
    assert agent.get_blizzard_over_hash(board_5) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for board_5"
    assert agent.get_blizzard_over_hash(board_6) == True, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should be over for board_6"
    assert agent.get_blizzard_over_hash(board_7) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for board_7"
    assert agent.get_blizzard_over_hash(board_13) == False, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not be over for board_8"
    
    print(Style.NORMAL + Fore.LIGHTGREEN_EX + "All Blizzard Over Board tests passed successfully!")

def run_blizzard_winners_tests(agent):
    assert agent.get_blizzard_winner_hash(results_1) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_1"
    assert agent.get_blizzard_winner_hash(results_2) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_2"
    assert agent.get_blizzard_winner_hash(results_3) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_3"
    assert agent.get_blizzard_winner_hash(results_4) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_4"
    assert agent.get_blizzard_winner_hash(results_5) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_5"
    assert agent.get_blizzard_winner_hash(results_6) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for results_6"
    assert agent.get_blizzard_winner_hash(results_7) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for results_7"
    assert agent.get_blizzard_winner_hash(results_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_8"
    assert agent.get_blizzard_winner_hash(results_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_9"
    assert agent.get_blizzard_winner_hash(results_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_10"
    assert agent.get_blizzard_winner_hash(results_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_11"
    assert agent.get_blizzard_winner_hash(results_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_12"
    assert agent.get_blizzard_winner_hash(results_13) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for results_13"

    assert agent.get_blizzard_winner_hash(board_1) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for board_1"
    assert agent.get_blizzard_winner_hash(board_2) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for board_2"
    assert agent.get_blizzard_winner_hash(board_3) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for board_3"
    assert agent.get_blizzard_winner_hash(board_4) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for board_4"
    assert agent.get_blizzard_winner_hash(board_5) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for board_5"
    assert agent.get_blizzard_winner_hash(board_6) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should have a winner for board_6"
    assert agent.get_blizzard_winner_hash(board_7) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for board_7"
    assert agent.get_blizzard_winner_hash(board_13) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Blizzard should not have a winner for board_8"
    
    print(Style.NORMAL + Fore.LIGHTGREEN_EX + "All Blizzard Winner tests passed successfully!")

def run_won_tests(agent):
    # Boards won by player 1
    assert agent.get_winner_hash(board_1) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won board_1"
    assert agent.get_winner_hash(board_2) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won board_2"
    assert agent.get_winner_hash(board_3) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won board_3"
    assert agent.get_winner_hash(board_4) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player -1 should have won board_4"
    assert agent.get_winner_hash(board_5) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player -1 should have won board_5"
    assert agent.get_winner_hash(board_6) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player -1 should have won board_6"
    assert agent.get_winner_hash(board_7) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not have a winner"
    assert agent.get_winner_hash(board_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should not have a winner"
    assert agent.get_winner_hash(board_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not have a winner"
    assert agent.get_winner_hash(board_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should not have a winner"
    assert agent.get_winner_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should not have a winner"
    assert agent.get_winner_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should not have a winner"

    print(Style.NORMAL + Fore.LIGHTGREEN_EX + "All Won-Board tests passed successfully!")

def run_won_results_tests(agent):
    assert agent.get_winning_result_hash(board_1) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won board_1"
    assert agent.get_winning_result_hash(board_2) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won board_2"
    assert agent.get_winning_result_hash(board_3) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won board_3"
    assert agent.get_winning_result_hash(board_4) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player -1 should have won board_4"
    assert agent.get_winning_result_hash(board_5) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player -1 should have won board_5"
    assert agent.get_winning_result_hash(board_6) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player -1 should have won board_6"
    assert agent.get_winning_result_hash(board_7) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not have a winner"
    assert agent.get_winning_result_hash(board_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should not have a winner"
    assert agent.get_winning_result_hash(board_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not have a winner"
    assert agent.get_winning_result_hash(board_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should not have a winner"
    assert agent.get_winning_result_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should not have a winner"
    assert agent.get_winning_result_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should not have a winner"

    assert agent.get_winning_result_hash(results_1) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_1"
    assert agent.get_winning_result_hash(results_2) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_2"
    assert agent.get_winning_result_hash(results_3) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_3"
    assert agent.get_winning_result_hash(results_4) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_4"
    assert agent.get_winning_result_hash(results_5) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_5"
    assert agent.get_winning_result_hash(results_6) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_6"
    assert agent.get_winning_result_hash(results_7) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_7"
    assert agent.get_winning_result_hash(results_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_8"
    assert agent.get_winning_result_hash(results_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_9"
    assert agent.get_winning_result_hash(results_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_10"
    assert agent.get_winning_result_hash(results_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Player 1 should have won results_11"

    print(Style.NORMAL + Fore.LIGHTGREEN_EX + "All Won-Results tests passed successfully!")

def run_eval_tests_v1(agent):
    assert agent.get_eval_hash(board_1) == b1_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    assert agent.get_eval_hash(board_2) == b2_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    assert agent.get_eval_hash(board_3) == b3_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    assert agent.get_eval_hash(board_4) == b4_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    assert agent.get_eval_hash(board_5) == b5_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    assert agent.get_eval_hash(board_6) == b6_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_eval_hash(board_7) == b7_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 evaluation does not match"
    assert agent.get_eval_hash(board_8) == b8_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 evaluation does not match"
    assert agent.get_eval_hash(board_9) == b9_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 evaluation does not match"
    assert agent.get_eval_hash(board_10) == b10_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 evaluation does not match"
    assert agent.get_eval_hash(board_11) == b11_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 evaluation does not match"
    assert agent.get_eval_hash(board_12) == b12_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 evaluation does not match"
    assert agent.get_eval_hash(board_center_only) == 0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Only evaluation does not match"
    assert agent.get_eval_hash(board_center_only_another) == 0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Only Another evaluation does not match"
    assert agent.get_eval_hash(board_center_enemy_only) == -0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Enemy Only evaluation does not match"

    print("All Eval V1 tests passed successfully!")

def run_eval_tests_v2(agent):
    assert agent.get_eval_v2_hash(board_1) == b1_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    assert agent.get_eval_v2_hash(board_2) == b2_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    assert agent.get_eval_v2_hash(board_3) == b3_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    assert agent.get_eval_v2_hash(board_4) == b4_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    assert agent.get_eval_v2_hash(board_5) == b5_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    assert agent.get_eval_v2_hash(board_6) == b6_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_eval_v2_hash(board_7) == b7_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 evaluation does not match"
    assert agent.get_eval_v2_hash(board_8) == b8_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 evaluation does not match"
    assert agent.get_eval_v2_hash(board_9) == b9_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 evaluation does not match"
    assert agent.get_eval_v2_hash(board_10) == b10_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 evaluation does not match"
    assert agent.get_eval_v2_hash(board_11) == b11_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 evaluation does not match"
    assert agent.get_eval_v2_hash(board_12) == b12_eval_v2, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 evaluation does not match"
    assert agent.get_eval_v2_hash(board_center_only) == 0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Only evaluation does not match"
    assert agent.get_eval_v2_hash(board_center_only_another) == 0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Only Another evaluation does not match"
    assert agent.get_eval_v2_hash(board_center_enemy_only) == -0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Enemy Only evaluation does not match"

    print("All Eval V2 tests passed successfully!")

def run_eval_tests_v3(agent):
    assert agent.get_eval_v3_hash(board_1) == b1_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    assert agent.get_eval_v3_hash(board_2) == b2_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    assert agent.get_eval_v3_hash(board_3) == b3_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    assert agent.get_eval_v3_hash(board_4) == b4_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    assert agent.get_eval_v3_hash(board_5) == b5_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    assert agent.get_eval_v3_hash(board_6) == b6_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_eval_v3_hash(board_7) == b7_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 evaluation does not match"
    assert agent.get_eval_v3_hash(board_8) == b8_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 evaluation does not match"
    assert agent.get_eval_v3_hash(board_9) == b9_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 evaluation does not match"
    assert agent.get_eval_v3_hash(board_10) == b10_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 evaluation does not match"
    assert agent.get_eval_v3_hash(board_11) == b11_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 evaluation does not match"
    assert agent.get_eval_v3_hash(board_12) == b12_eval_v3, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 evaluation does not match"
    assert agent.get_eval_v3_hash(board_center_only) == 0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Only evaluation does not match"
    assert agent.get_eval_v3_hash(board_center_only_another) == 0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Only Another evaluation does not match"
    assert agent.get_eval_v3_hash(board_center_enemy_only) == -0.421, Style.BRIGHT + Fore.RED + "Test Failed! Board Center Enemy Only evaluation does not match"

    print("All Eval V3 tests passed successfully!")

def get_eval_result_tests_v1(agent):
    assert agent.get_eval_result_v1_hash(board_1) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_2) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_3) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_4) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_5) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_6) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_7) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 evaluation does not match"
    assert agent.get_eval_result_v1_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 evaluation does not match"

    print("All Eval Result V1 tests passed successfully!")
    
def get_eval_result_tests_v2(agent):
    assert agent.get_eval_result_v2_hash(board_1) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_2) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_3) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_4) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_5) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_6) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_7) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 evaluation does not match"
    assert agent.get_eval_result_v2_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 evaluation does not match"

    print("All Eval Result V2 tests passed successfully!")
    
def get_eval_result_tests_v3(agent):
    assert agent.get_eval_result_v3_hash(board_1) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_2) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_3) == 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_4) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_5) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_6) == -1, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_7) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_8) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_9) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_10) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 evaluation does not match"
    assert agent.get_eval_result_v3_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 evaluation does not match"

    print("All Eval Result V3 tests passed successfully!")

def run_board_info_tests(agent):
    assert agent.get_board_info(board_1)[0] == b1_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 1 evaluation does not match, evaluation was {agent.get_board_info(board_1)[0]}"
    assert agent.get_board_info(board_1)[1] == 1, Style.BRIGHT + Fore.RED + f"Test Failed! Board 1 result does not match, result was {agent.get_board_info(board_1)[1]}"

    assert agent.get_board_info(board_2)[0] == b2_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 2 evaluation does not match, evaluation was {agent.get_board_info(board_2)[0]}"
    assert agent.get_board_info(board_2)[1] == 1, Style.BRIGHT + Fore.RED + f"Test Failed! Board 2 result does not match, result was {agent.get_board_info(board_2)[1]}"

    assert agent.get_board_info(board_3)[0] == b3_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 3 evaluation does not match, evaluation was {agent.get_board_info(board_3)[0]}"
    assert agent.get_board_info(board_3)[1] == 1, Style.BRIGHT + Fore.RED + f"Test Failed! Board 3 result does not match, result was {agent.get_board_info(board_3)[1]}"

    assert agent.get_board_info(board_4)[0] == b4_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 4 evaluation does not match, evaluation was {agent.get_board_info(board_4)[0]}"
    assert agent.get_board_info(board_4)[1] == -1, Style.BRIGHT + Fore.RED + f"Test Failed! Board 4 result does not match, result was {agent.get_board_info(board_4)[1]}"

    assert agent.get_board_info(board_5)[0] == b5_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 5 evaluation does not match, evaluation was {agent.get_board_info(board_5)[0]}"
    assert agent.get_board_info(board_5)[1] == -1, Style.BRIGHT + Fore.RED + f"Test Failed! Board 5 result does not match, result was {agent.get_board_info(board_5)[1]}"

    assert agent.get_board_info(board_6)[0] == b6_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 6 evaluation does not match, evaluation was {agent.get_board_info(board_6)[0]}"
    assert agent.get_board_info(board_6)[1] == -1, Style.BRIGHT + Fore.RED + f"Test Failed! Board 6 result does not match, result was {agent.get_board_info(board_6)[1]}"

    assert agent.get_board_info(board_7)[0] == b7_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 7 evaluation does not match, evaluation was {agent.get_board_info(board_7)[0]}"
    assert agent.get_board_info(board_7)[1] == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 7 result does not match, result was {agent.get_board_info(board_7)[1]}"

    assert agent.get_board_info(board_8)[0] == b8_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 8 evaluation does not match, evaluation was {agent.get_board_info(board_8)[0]}"
    assert agent.get_board_info(board_8)[1] == 2, Style.BRIGHT + Fore.RED + f"Test Failed! Board 8 result does not match, result was {agent.get_board_info(board_8)[1]}"

    assert agent.get_board_info(board_9)[0] == b9_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 9 evaluation does not match, evaluation was {agent.get_board_info(board_9)[0]}"
    assert agent.get_board_info(board_9)[1] == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 7 result does not match, result was {agent.get_board_info(board_9)[1]}"

    assert agent.get_board_info(board_10)[0] == b10_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 10 evaluation does not match, evaluation was {agent.get_board_info(board_10)[0]}"
    assert agent.get_board_info(board_10)[1] == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 10 result does not match, result was {agent.get_board_info(board_10)[1]}"

    assert agent.get_board_info(board_11)[0] == b11_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 11 evaluation does not match, evaluation was {agent.get_board_info(board_11)[0]}"
    assert agent.get_board_info(board_11)[1] == 2, Style.BRIGHT + Fore.RED + f"Test Failed! Board 11 result does not match, result was {agent.get_board_info(board_11)[1]}"

    assert agent.get_board_info(board_12)[0] == b12_eval_glob, Style.BRIGHT + Fore.RED + f"Test Failed! Board 12 evaluation does not match, evaluation was {agent.get_board_info(board_12)[0]}"
    assert agent.get_board_info(board_12)[1] == 2, Style.BRIGHT + Fore.RED + f"Test Failed! Board 12 result does not match, result was {agent.get_board_info(board_12)[1]}"

    assert agent.get_board_info(board_center_only)[0] == CENTER_ONLY_EVAL, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center_Only evaluation does not match, evaluation was {agent.get_board_info(board_center_only)[0]}"
    assert agent.get_board_info(board_center_only)[1] == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center_Only result does not match, result was {agent.get_board_info(board_center_only)[1]}"

    assert agent.get_board_info(board_center_only_another)[0] == CENTER_ONLY_EVAL, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center_Only_Another evaluation does not match, evaluation was {agent.get_board_info(board_center_only_another)[0]}"
    assert agent.get_board_info(board_center_only_another)[1] == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center_Only_Another result does not match, result was {agent.get_board_info(board_center_only_another)[1]}"

    assert agent.get_board_info(board_center_enemy_only)[0] == -CENTER_ONLY_EVAL, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center_Enemy_Only evaluation does not match, evaluation was {agent.get_board_info(board_center_enemy_only)[0]}"
    assert agent.get_board_info(board_center_enemy_only)[1] == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center_Enemy_Only result does not match, result was {agent.get_board_info(board_center_enemy_only)[1]}"

    print("All Board Information tests passed successfully!")

def run_board_info_commonsense_tests(agent):
    single_eval = 0.14
    double_eval = 0.6
    winning_eval = 3.6
    winning_pos_score = 4.5 # creo?

    b1_eval, b1_result, b1_lead, b1_score = agent.get_board_info(board_1)
    b2_eval, b2_result, b2_lead, b2_score = agent.get_board_info(board_2)
    b2b_eval, b2b_result, b2b_lead, b2b_score = agent.get_board_info(board_2b)
    b3_eval, b3_result, b3_lead, b3_score = agent.get_board_info(board_3)
    b4_eval, b4_result, b4_lead, b4_score = agent.get_board_info(board_4)
    b5_eval, b5_result, b5_lead, b5_score = agent.get_board_info(board_5)
    b6_eval, b6_result, b6_lead, b6_score = agent.get_board_info(board_6)
    b7_eval, b7_result, b7_lead, b7_score = agent.get_board_info(board_7)
    b8_eval, b8_result, b8_lead, b8_score = agent.get_board_info(board_8)
    b9_eval, b9_result, b9_lead, b9_score = agent.get_board_info(board_9)
    b10_eval, b10_result, b10_lead, b10_score = agent.get_board_info(board_10)
    b11_eval, b11_result, b11_lead, b11_score = agent.get_board_info(board_11)
    b12_eval, b12_result, b12_lead, b12_score = agent.get_board_info(board_12)
    b13_eval, b13_result, b13_lead, b13_score = agent.get_board_info(board_13)
    b14_eval, b14_result, b14_lead, b14_score = agent.get_board_info(board_14)
    b15_eval, b15_result, b15_lead, b15_score = agent.get_board_info(board_15)
    b16_eval, b16_result, b16_lead, b16_score = agent.get_board_info(board_16)
    b17_eval, b17_result, b17_lead, b17_score = agent.get_board_info(board_17)
    b18_eval, b18_result, b18_lead, b18_score = agent.get_board_info(board_18)
    b19_eval, b19_result, b19_lead, b19_score = agent.get_board_info(board_19)
    b20_eval, b20_result, b20_lead, b20_score = agent.get_board_info(board_20)
    b21_eval, b21_result, b21_lead, b21_score = agent.get_board_info(board_21)
    b22_eval, b22_result, b22_lead, b22_score = agent.get_board_info(board_22)
    b23_eval, b23_result, b23_lead, b23_score = agent.get_board_info(board_23)
    b24_eval, b24_result, b24_lead, b24_score = agent.get_board_info(board_24)
    b25_eval, b25_result, b25_lead, b25_score = agent.get_board_info(board_25)
    b26_eval, b26_result, b26_lead, b26_score = agent.get_board_info(board_26)
    b27_eval, b27_result, b27_lead, b27_score = agent.get_board_info(board_27)
    b28_eval, b28_result, b28_lead, b28_score = agent.get_board_info(board_28)
    b29_eval, b29_result, b29_lead, b29_score = agent.get_board_info(board_29)
    b30_eval, b30_result, b30_lead, b30_score = agent.get_board_info(board_30)
    b31_eval, b31_result, b31_lead, b31_score = agent.get_board_info(board_31)
    b32_eval, b32_result, b32_lead, b32_score = agent.get_board_info(board_32)
    b33_eval, b33_result, b33_lead, b33_score = agent.get_board_info(board_33)
    b34_eval, b34_result, b34_lead, b34_score = agent.get_board_info(board_34)
    b35_eval, b35_result, b35_lead, b35_score = agent.get_board_info(board_35)
    b36_eval, b36_result, b36_lead, b36_score = agent.get_board_info(board_36)
    b37_eval, b37_result, b37_lead, b37_score = agent.get_board_info(board_37)
    b38_eval, b38_result, b38_lead, b38_score = agent.get_board_info(board_38)
    b39_eval, b39_result, b39_lead, b39_score = agent.get_board_info(board_39)
    b40_eval, b40_result, b40_lead, b40_score = agent.get_board_info(board_40)
    b41_eval, b41_result, b41_lead, b41_score = agent.get_board_info(board_41)
    b42_eval, b42_result, b42_lead, b42_score = agent.get_board_info(board_42)
    b43_eval, b43_result, b43_lead, b43_score = agent.get_board_info(board_43)
    b44_eval, b44_result, b44_lead, b44_score = agent.get_board_info(board_44)
    b45_eval, b45_result, b45_lead, b45_score = agent.get_board_info(board_45)
    b46_eval, b46_result, b46_lead, b46_score = agent.get_board_info(board_46)
    b47_eval, b47_result, b47_lead, b47_score = agent.get_board_info(board_47)

    bEMP, bEMP_result, bEMP_lead, bEMP_score = agent.get_board_info(board_empty)
    bCO, bCO_result, bCO_lead, bCO_score = agent.get_board_info(board_center_only)
    bCEO, bCEO_result, bCEO_lead, bCEO_score = agent.get_board_info(board_center_enemy_only)

    non_won_list = (b7_eval, b8_eval, b9_eval, b10_eval, b11_eval, b12_eval, b20_eval, b21_eval, b22_eval, b23_eval, b27_eval, b28_eval, b29_eval, b30_eval)
    max_eval = max(non_won_list)
    min_eval = min(non_won_list)

    # Evaluations!
    assert b1_eval == winning_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 1 should have been won by 1, but eval was {b1_eval}"
    assert b2_eval == winning_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 2 should have been won by 1, but eval was {b2_eval}"
    assert b2b_eval == b2_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 2b should have been won by 1, but eval was {b2b_eval}"
    assert b3_eval == winning_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 3 should have been won by 1, but eval was {b3_eval}"
    assert b4_eval == -winning_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 4 should have been won by -1, but eval was {b4_eval}"
    assert b5_eval == -winning_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 5 should have been won by -1, but eval was {b5_eval}"
    assert b6_eval == -winning_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 6 should have been won by -1, but eval was {b6_eval}"
    assert b7_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 7 should be 0, but eval was {b7_eval}"
    assert b8_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 8 is a full draw, but eval was {b8_eval}"
    assert b9_eval == -single_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 9 evaluation should be a negative single val, but eval was {b9_eval}"
    assert b10_eval == -b9_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 10 evaluation should be inverse of Board 9, but b10 eval was {b10_eval}, while b9 eval was {b9_eval}"
    assert b11_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 11 should be 0 for Draw, but Eval was {b11_eval}"
    assert b12_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 12 should be 0 for Draw, but Eval was {b12_eval}"
    assert b13_eval == 4*double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 13 should have an evaluation of {4*double_eval}, but eval was {b13_eval}"
    assert b14_eval == b28_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 14 should have the same evaluation as Board 28, but eval was {b14_eval}"
    assert b15_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 14 should have an evaluation of 0, but eval was {b14_eval}"
    assert 0.12 < b16_eval < double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 16 should have an evaluation between 0.12 and 0.6, but eval was {b16_eval}"
    assert 0.12 < b17_eval < double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 17 should have an evaluation between 0.12 and 0.6, but eval was {b17_eval}"
    assert 0.12 < b18_eval < double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 18 should have an evaluation between 0.12 and 0.6, but eval was {b18_eval}"
    assert b19_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 19 should have an evaluation of 0, but eval was {b19_eval}"
    assert b20_eval == double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 20 should have an evaluation of 0.6, but eval was {b20_eval}"
    assert b21_eval == double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 21 should have an evaluation of 0.6, but eval was {b21_eval}"
    assert b22_eval == double_eval + single_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 22 should have an evaluation of 0.6, but eval was {b22_eval}"
    assert b23_eval == double_eval - single_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 23 should have an evaluation of 0.6, but eval was {b23_eval}"
    
    assert b27_eval == 5 * double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 27 should have an evaluation of {5*double_eval}, but eval was {b27_eval}"
    assert b27_eval == max_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 27 should be the maximum, but the maximum was {max_eval}, b27 eval was {b27_eval}"
    assert b28_eval == -b27_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 28 should have an evaluation of {-5*double_eval}, but eval was {b28_eval}"
    assert b28_eval == min_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 28 should be the minimum, but the minimum was {min_eval}, b28 eval was {b28_eval}"
    assert b29_eval == b27_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 29 should have an evaluation of {5*double_eval}, but eval was {b29_eval}"
    assert b30_eval == -b29_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 30 should have an evaluation of {-5*double_eval}, but eval was {b30_eval}"
    assert b31_eval == 4 * double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 31 should have an evaluation of {4*double_eval}, but eval was {b31_eval}"
    assert b32_eval == -b31_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 32 should have an evaluation of {-4*double_eval}, but eval was {b32_eval}"
    assert b33_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 33 should have an evaluation of 0, but eval was {b33_eval}"
    assert b34_eval == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board 34 should have an evaluation of 0, but eval was {b34_eval}"
    assert b35_eval < b18_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 35 should have an evaluation less than Board 18, but 18 eval was {b18_eval}, 35 eval was {b35_eval}"
    assert b36_eval == -b18_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 36 should have an evaluation equal to Board 18, but 18 eval was {b18_eval}, 36 eval was {b36_eval}"
    assert b18_eval < b37_eval < double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 37 should have an evaluation between 0.6 and 0.12, but eval was {b37_eval}"
    assert b37_eval < b38_eval < double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 38 should have an evaluation between 0.6 and 0.12, but eval was {b38_eval}"
    assert double_eval < b39_eval < 2 * double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 39 should have an evaluation between 0.6 and 1.2, but eval was {b39_eval}"
    assert b40_eval == -b39_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 40 should have an evaluation equal to Board 39, but 39 eval was {b39_eval}, 40 eval was {b40_eval}"
    assert b41_eval > b39_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 41 should have an evaluation greater than Board 39, but 39 eval was {b39_eval}, 41 eval was {b41_eval}"
    assert b42_eval > b41_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 42 should have an evaluation greater than Board 41, but 41 eval was {b41_eval}, 42 eval was {b42_eval}"
    assert b43_eval > b42_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 43 should have an evaluation greater than Board 42, but 42 eval was {b42_eval}, 43 eval was {b43_eval}"
    assert b44_eval > b43_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 44 should have an evaluation greater than Board 43, but 43 eval was {b43_eval}, 44 eval was {b44_eval}"
    assert double_eval < b45_eval < double_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 45 should have an evaluation between 0.6 and 1.2, but eval was {b45_eval}"
    assert b46_eval < b39_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 46 should have an evaluation less than Board 39, but 39 eval was {b39_eval}, 46 eval was {b46_eval}"
    assert b47_eval < b42_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 47 should have an evaluation less than Board 42, but 42 eval was {b42_eval}, 47 eval was {b47_eval}"
    # Evaluations for Special Boards
    assert bEMP == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Board Empty should have an evaluation of 0, but eval was {bEMP}"
    assert bCO == CENTER_ONLY_EVAL, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center Only should have an evaluation of 0.421, but eval was {bCO}"
    assert bCEO == -CENTER_ONLY_EVAL, Style.BRIGHT + Fore.RED + f"Test Failed! Board Center Enemy Only should have an evaluation of -0.421, but eval was {bCEO}"

    # debug
    print(f"b16 score is {b16_score}, b16 eval is {b16_eval}, best connection coef is {best_connection_coefficient(board_16, player=b16_lead / 3)}")
    print(f"b17 score is {b17_score}, b17 eval is {b17_eval}, best connection coef is {best_connection_coefficient(board_17, player=b17_lead / 3)}")
    print(f"b18 score is {b18_score}, b18 eval is {b18_eval}, best connection coef is {best_connection_coefficient(board_18, player=b18_lead / 3)}")


def run_eval_results_tests(agent):
    # assert agent.get_results_board_eval(board_1) == b1_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 evaluation does not match"
    # assert agent.get_results_board_eval(board_2) == b2_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 evaluation does not match"
    # assert agent.get_results_board_eval(board_3) == b3_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 evaluation does not match"
    # assert agent.get_results_board_eval(board_4) == b4_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 evaluation does not match"
    # assert agent.get_results_board_eval(board_5) == b5_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 evaluation does not match"
    # assert agent.get_results_board_eval(board_6) == b6_eval, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 evaluation does not match"
    assert agent.get_results_board_eval(board_7) == round(0.75 * b7_eval, 2), Style.BRIGHT + Fore.RED + f"Test Failed! Board 7 evaluation does not match"
    assert agent.get_results_board_eval(board_8) == b8_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 8 evaluation does not match, evaluation is {agent.get_results_board_eval(board_8)}"
    assert agent.get_results_board_eval(board_9) == round((0.75 * -0.15), 2), Style.BRIGHT + Fore.RED + f"Test Failed! Board 9 evaluation does not match, evaluation is {agent.get_results_board_eval(board_9)}"
    assert agent.get_results_board_eval(board_10) == round((0.75 * 0.15), 2), Style.BRIGHT + Fore.RED + f"Test Failed! Board 10 evaluation does not match, evaluation is {agent.get_results_board_eval(board_10)}"
    assert agent.get_results_board_eval(board_11) == b11_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 11 evaluation does not match, evaluation is {agent.get_results_board_eval(board_11)}"
    assert agent.get_results_board_eval(board_12) == b12_eval, Style.BRIGHT + Fore.RED + f"Test Failed! Board 12 evaluation does not match, evaluation is {agent.get_results_board_eval(board_12)}"
    
    assert agent.get_results_board_eval(results_1) == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Results 1 evaluation does not match, the evaluation was {agent.get_results_board_eval(results_1)}"
    assert agent.get_results_board_eval(results_2) == 0.45, Style.BRIGHT + Fore.RED + f"Test Failed! Results 2 evaluation does not match, the evaluation was {agent.get_results_board_eval(results_2)}"
    assert agent.get_results_board_eval(results_3) == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Results 3 evaluation does not match, the evaluation was {agent.get_results_board_eval(results_3)}"
    assert agent.get_results_board_eval(results_4) == 0, Style.BRIGHT + Fore.RED + f"Test Failed! Results 4 evaluation does not match, the evaluation was {agent.get_results_board_eval(results_4)}"
    assert agent.get_results_board_eval(results_5) == 0.6, Style.BRIGHT + Fore.RED + f"Test Failed! Results 5 evaluation does not match, the evaluation was {agent.get_results_board_eval(results_5)}"

    print("All Results Board Eval tests passed successfully!")

def run_draw_tests(agent):
    assert agent.get_draw_hash(board_1) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should not be a draw"
    assert agent.get_draw_hash(board_2) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should not be a draw"
    assert agent.get_draw_hash(board_3) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should not be a draw"
    assert agent.get_draw_hash(board_4) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should not be a draw"
    assert agent.get_draw_hash(board_5) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should not be a draw"
    assert agent.get_draw_hash(board_6) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should not be a draw"
    assert agent.get_draw_hash(board_7) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not be a draw"
    assert agent.get_draw_hash(board_8) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should be a draw"
    assert agent.get_draw_hash(board_9) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not be a draw"
    assert agent.get_draw_hash(board_10) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should not be a draw"
    assert agent.get_draw_hash(board_11) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should be a draw"
    assert agent.get_draw_hash(board_12) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should be a draw"

    print("All Draw-Board tests passed successfully!")

def run_draw_results_tests(agent):
    assert agent.get_draw_result_hash(board_1) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 1 should not be a draw, result was {agent.get_draw_result_hash(board_1)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_2) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 2 should not be a draw, result was {agent.get_draw_result_hash(board_2)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_3) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 3 should not be a draw, result was {agent.get_draw_result_hash(board_3)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_4) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 4 should not be a draw, result was {agent.get_draw_result_hash(board_4)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_5) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 5 should not be a draw, result was {agent.get_draw_result_hash(board_5)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_6) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 6 should not be a draw, result was {agent.get_draw_result_hash(board_6)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_7) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 7 should not be a draw, result was {agent.get_draw_result_hash(board_7)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_8) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 8 should be a draw, result was {agent.get_draw_result_hash(board_8)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_9) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 9 should not be a draw, result was {agent.get_draw_result_hash(board_9)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_10) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 10 should not be a draw, result was {agent.get_draw_result_hash(board_10)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_11) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 11 should be a draw, result was {agent.get_draw_result_hash(board_11)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(board_12) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Board 12 should be a draw, result was {agent.get_draw_result_hash(board_12)}" + Style.RESET_ALL

    assert agent.get_draw_result_hash(results_1) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 1 should not be a draw, result was {agent.get_draw_result_hash(results_1)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_2) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 2 should not be a draw, result was {agent.get_draw_result_hash(results_2)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_3) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 3 should not be a draw, result was {agent.get_draw_result_hash(results_3)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_4) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 4 should not be a draw, result was {agent.get_draw_result_hash(results_4)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_5) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 5 should not be a draw, result was {agent.get_draw_result_hash(results_5)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_6) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 6 should not be a draw, result was {agent.get_draw_result_hash(results_6)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_7) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 7 should not be a draw, result was {agent.get_draw_result_hash(results_7)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_8) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 8 should be a draw, result was {agent.get_draw_result_hash(results_8)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_9) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 9 should be a draw, result was {agent.get_draw_result_hash(results_9)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_10) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 10 should not be a draw, result was {agent.get_draw_result_hash(results_10)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_11) == False, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 11 should not be a draw, result was {agent.get_draw_result_hash(results_11)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_12) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 12 should be a draw, result was {agent.get_draw_result_hash(results_12)}" + Style.RESET_ALL
    assert agent.get_draw_result_hash(results_13) == True, Style.BRIGHT + Fore.RED + Style.BRIGHT + Fore.RED + f"Test Failed! Results 13 should be a draw, result was {agent.get_draw_result_hash(results_13)}" + Style.RESET_ALL

    print("All Draw-Results tests passed successfully!")

def run_over_tests(agent):
    assert agent.get_over_hash(board_1) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should be over"
    assert agent.get_over_hash(board_2) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should be over"
    assert agent.get_over_hash(board_3) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should be over"
    assert agent.get_over_hash(board_4) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should be over"
    assert agent.get_over_hash(board_5) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should be over"
    assert agent.get_over_hash(board_6) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should be over"
    assert agent.get_over_hash(board_7) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not be over"
    assert agent.get_over_hash(board_8) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should be over"
    assert agent.get_over_hash(board_9) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not be over"
    assert agent.get_over_hash(board_10) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should not be over"
    assert agent.get_over_hash(board_11) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should not be over"
    assert agent.get_over_hash(board_12) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should not be over"
    print("All Over-Board tests passed successfully!")

def run_playable_tests(agent):
    assert agent.get_playable_hash(board_1) == isPlayable(board_1) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should not be playable"
    assert agent.get_playable_hash(board_2) == isPlayable(board_2) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should not be playable"
    assert agent.get_playable_hash(board_3) == isPlayable(board_3) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should not be playable"
    assert agent.get_playable_hash(board_4) == isPlayable(board_4) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should not be playable"
    assert agent.get_playable_hash(board_5) == isPlayable(board_5) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should not be playable"
    assert agent.get_playable_hash(board_6) == isPlayable(board_6) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should not be playable"
    assert agent.get_playable_hash(board_7) == isPlayable(board_7) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should be playable"
    assert agent.get_playable_hash(board_8) == isPlayable(board_8) == False, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should not be playable"
    assert agent.get_playable_hash(board_9) == isPlayable(board_9) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should be playable"
    assert agent.get_playable_hash(board_10) == isPlayable(board_10) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should be playable"
    assert agent.get_playable_hash(board_11) == isPlayable(board_11) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should be playable"
    assert agent.get_playable_hash(board_12) == isPlayable(board_12) == True, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should be playable"
    print("All Playable-Board tests passed successfully!")

def run_eval_commonsense_tests(agent):
    assert agent.get_eval_hash(board_1) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should have a score of 6.4 since its won"
    assert agent.get_eval_hash(board_2) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should have a score of 6.4 since its won"
    assert agent.get_eval_hash(board_3) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should have a score of 6.4 since its won"
    assert agent.get_eval_hash(board_4) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should have a score of -6.4 since its won"
    assert agent.get_eval_hash(board_5) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should have a score of -6.4 since its won"
    assert agent.get_eval_hash(board_6) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_eval_hash(board_7)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_eval_hash(board_7) >= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not have a negative score"
    assert abs(agent.get_eval_hash(board_8)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should have a score of 0"
    assert agent.get_eval_hash(board_9) <= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not have a positive score"
    assert abs(agent.get_eval_hash(board_9)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_eval_hash(board_10) == -1 * agent.get_eval_hash(board_9), Style.BRIGHT + Fore.RED + "Test Failed! Board 10 score should be inverse of Board 9"
    assert agent.get_eval_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should have a score of 0"
    assert agent.get_eval_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should have a score of 0"

    print("All Eval Common-Sense tests passed successfully!")

def run_eval_v2_commonsense_tests(agent):
    assert agent.get_eval_v2_hash(board_1) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should have a score of 6.4 since its won"
    assert agent.get_eval_v2_hash(board_2) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should have a score of 6.4 since its won"
    assert agent.get_eval_v2_hash(board_3) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should have a score of 6.4 since its won"
    assert agent.get_eval_v2_hash(board_4) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should have a score of -6.4 since its won"
    assert agent.get_eval_v2_hash(board_5) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should have a score of -6.4 since its won"
    assert agent.get_eval_v2_hash(board_6) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_eval_v2_hash(board_7)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_eval_v2_hash(board_7) >= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not have a negative score"
    assert abs(agent.get_eval_v2_hash(board_8)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should have a score of 0"
    assert agent.get_eval_v2_hash(board_9) <= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not have a positive score"
    assert abs(agent.get_eval_v2_hash(board_9)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_eval_v2_hash(board_10) == -1 * agent.get_eval_v2_hash(board_9), Style.BRIGHT + Fore.RED + "Test Failed! Board 10 score should be inverse of Board 9"
    assert agent.get_eval_v2_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should have a score of 0"
    assert agent.get_eval_v2_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should have a score of 0"

    print("All Eval V2 Common-Sense tests passed successfully!")

def run_eval_v3_commonsense_tests(agent):
    assert agent.get_eval_v3_hash(board_1) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should have a score of 6.4 since its won"
    assert agent.get_eval_v3_hash(board_2) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should have a score of 6.4 since its won"
    assert agent.get_eval_v3_hash(board_3) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should have a score of 6.4 since its won"
    assert agent.get_eval_v3_hash(board_4) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should have a score of -6.4 since its won"
    assert agent.get_eval_v3_hash(board_5) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should have a score of -6.4 since its won"
    assert agent.get_eval_v3_hash(board_6) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_eval_v3_hash(board_7)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_eval_v3_hash(board_7) >= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not have a negative score"
    assert abs(agent.get_eval_v3_hash(board_8)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should have a score of 0"
    assert agent.get_eval_v3_hash(board_9) <= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not have a positive score"
    assert abs(agent.get_eval_v3_hash(board_9)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_eval_v3_hash(board_10) == -1 * agent.get_eval_v3_hash(board_9), Style.BRIGHT + Fore.RED + "Test Failed! Board 10 score should be inverse of Board 9"
    assert agent.get_eval_v3_hash(board_11) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should have a score of 0"
    assert agent.get_eval_v3_hash(board_12) == 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should have a score of 0"

    print("All Eval V3 Common-Sense tests passed successfully!")
    
def run_eval_glob_commonsense_tests(agent):
    assert agent.get_board_info(board_1) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should have a score of 6.4 since its won"
    assert agent.get_board_info(board_2) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should have a score of 6.4 since its won"
    assert agent.get_board_info(board_3) == 6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should have a score of 6.4 since its won"
    assert agent.get_board_info(board_4) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should have a score of -6.4 since its won"
    assert agent.get_board_info(board_5) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should have a score of -6.4 since its won"
    assert agent.get_board_info(board_6) == -6.4, Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should have a score of -6.4 since its won"
    assert abs(agent.get_board_info(board_7)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_board_info(board_7) >= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not have a negative score"
    assert agent.get_board_info(board_9) <= 0, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not have a positive score"
    assert abs(agent.get_board_info(board_9)) < 1, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should have a low absolute score"
    assert agent.get_board_info(board_10) == -1 * agent.get_board_info(board_9), Style.BRIGHT + Fore.RED + "Test Failed! Board 10 score should be inverse of Board 9"

    print("All Eval Global Local Common-Sense tests passed successfully!")

def run_winnable_tests_one(agent):
    # Boards winnable by player 1
    assert agent.get_winnable_by_one_hash(board_1) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_2) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_3) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_4) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_5) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_6) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_7) == {(2, 0)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_8) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_9) == {(0, 2)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_10) == {(1, 2)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_11) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_12) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_13) == {(0, 1), (1, 1), (1, 2), (2, 0)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 13 should be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_14) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 14 should not be winnable by player 1"
    assert agent.get_winnable_by_one_hash(board_15) == {(0, 2), (2, 0)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 15 should be winnable by player 1"

    print("All Winnable-By-One tests passed successfully!")

def run_winnable_tests_minus_one(agent):
    # Boards winnable by player -1
    assert agent.get_winnable_by_minus_one_hash(board_1) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 1 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_2) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 2 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_3) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 3 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_4) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 4 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_5) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 5 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_6) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 6 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_7) == {(2, 0)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 7 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_8) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 8 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_9) == {(1, 2)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 9 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_10) == {(2, 2)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 10 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_11) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 11 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_12) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 12 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_13) == set(), Style.BRIGHT + Fore.RED + "Test Failed! Board 13 should not be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_14) == {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 14 should be winnable by player -1"
    assert agent.get_winnable_by_minus_one_hash(board_15) == {(0, 2), (2, 0)}, Style.BRIGHT + Fore.RED + "Test Failed! Board 15 should be winnable by player -1"

    print("All Winnable-By-Minus-One tests passed successfully!")

def run_HyphenNumeric_tests(agent):
    assert agent.get_HyphenNumeric_hash(super_board_1, btp1) == bestmove1, Style.BRIGHT + Fore.RED + "Test Failed! Super Board 1 should have a best move of (2, 0, 0, 2)"
    assert agent.get_HyphenNumeric_hash(super_board_2, btp2) == bestmove2, Style.BRIGHT + Fore.RED + "Test Failed! Super Board 2 should have a best move of (0, 2, 2, 0)"
    
    print("All HyphenNumeric tests passed successfully!" + Style.RESET_ALL)

# Test Running Function
def run_all_agent_tests(agent):
    t0 = time.time()
    # run_eval_hash_completion_tests(agent)
    # run_results_hash_completion_tests(agent)
    run_won_tests(agent)
    run_won_results_tests(agent)
    run_blizzard_over_board_tests(agent)
    run_blizzard_winners_tests(agent)
    run_eval_tests_v1(agent)
    run_eval_tests_v2(agent)
    run_eval_tests_v3(agent)
    run_board_info_tests(agent)
    run_board_info_commonsense_tests(agent)
    run_eval_results_tests(agent)
    run_draw_tests(agent)
    run_draw_results_tests(agent)
    run_over_tests(agent)
    run_playable_tests(agent)
    run_eval_commonsense_tests(agent)
    run_eval_v2_commonsense_tests(agent)
    run_eval_v3_commonsense_tests(agent)
    run_winnable_tests_one(agent)
    run_winnable_tests_minus_one(agent)
    run_HyphenNumeric_tests(agent)
    t_final_ms = (time.time() - t0) * 1000
    
    print(Style.BRIGHT + Fore.GREEN + "\nAll tests passed successfully! 😄" + Style.RESET_ALL)
    print(Style.BRIGHT + Fore.LIGHTBLACK_EX + f"Total time taken: {t_final_ms:.2f} miliseconds" + Style.RESET_ALL)

# Run the Tests
run_all_agent_tests(agent)
