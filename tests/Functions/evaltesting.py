import math
import numpy as np
from typing import List, Tuple

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

def advanced_line_eval(line, player=1):
    ''' Works like lineEval, but also considering tiles with a '2' as being blocked,
    not counting to any player, and blocking any row/column/diagonal from a potential 3-in-line '''
    if line.count(2) > 0:
        return 0
    # TODO: Keep testing single_eval and double_eval
    return lineEval(line, player=player, single_eval=0.15, double_eval=0.60)

def local_evaluation(local_board):
    # TIMEIT APPROVED ✅
    ''' 
    Intended to Work for Global Board Results Eval as a 3x3
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    When both players threat, tone down but just a tiny bit
    NO CENTER COEFFICIENT OR ANYTHING LIKE THAT
    '''

    center_only_eval = 0.35
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
    winning_eval = 4.5
    player1_threat, player2_threat = False, False
    p1_threat_spaces, p2_threat_spaces = set(), set()


    # Row1
    row1 = (local_board[0, 0], local_board[0, 1], local_board[0, 2])
    row1_indeces = [(0, 0), (0, 1), (0, 2)]
    row1_eval = lineEval((row1), single_eval=single_eval, double_eval=double_eval)
    
    if abs(row1_eval) == 1:
        return winning_eval * row1_eval
    
    if detectDouble(row1):
        if row1_eval > 0:
            player1_threat = True
            p1_threat_tile = row1_indeces[row1.index(0)]
            
            if p1_threat_tile in p1_threat_spaces:
                score += 0
            else:
                score += row1_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row1_eval < 0:
            player2_threat = True
            p2_threat_tile = row1_indeces[row1.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += row1_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row1}")
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
            else:
                score += row2_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row2_eval < 0:
            player2_threat = True
            p2_threat_tile = row2_indeces[row2.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += row2_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row2}")
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
            else:
                score += row3_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row3_eval < 0:
            player2_threat = True
            p2_threat_tile = row3_indeces[row3.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += row3_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row3}")
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
            else:
                score += col1_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col1_eval < 0:
            player2_threat = True
            p2_threat_tile = col1_indeces[col1.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += col1_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col1}")
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
            else:
                score += col2_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col2_eval < 0:
            player2_threat = True
            p2_threat_tile = col2_indeces[col2.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += col2_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col2}")
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
            else:
                score += col3_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col3_eval < 0:
            player2_threat = True
            p2_threat_tile = col3_indeces[col3.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += col3_eval
                p2_threat_spaces.add(p2_threat_tile)
                
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col3}")
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
            else:
                score += diagTB_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif diagTB_eval < 0:
            player2_threat = True
            p2_threat_tile = diagTB_indeces[diagTB.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += diagTB_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {diagTB}")
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
            else:
                score += diagBT_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif diagBT_eval < 0:
            player2_threat = True
            p2_threat_tile = diagBT_indeces[diagBT.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += diagBT_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {diagBT}")
    else:
        score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        if empties == 1:
            return 0
        if empties == 2:
            if len(p1_threat_spaces) == 1 and len(p2_threat_spaces) == 1:
                return 0
        else:
            final_score = score * 0.75
            return round(final_score, 2)

    final_score = round(score, 2)
    return final_score

def better_evaluation(local_board):
    ''' Copiar la de arriba, pero hacer que si hay una tile ya contada por una doble, 
    que no se repita ever, ni en dobles ni en singles del mismp player 
    Ponerle un 2 no sirve porque le sacas los conteos al rival en sus 
    posibles amenazas con esa Tile desde otras lineas '''

    center_only_eval = 0.35
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
    winning_eval = 4.5
    player1_threat, player2_threat = False, False
    p1_threat_spaces, p2_threat_spaces = set(), set()


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
            else:
                score += row1_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row1_eval < 0:
            player2_threat = True
            p2_threat_tile = row1_indeces[row1.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += row1_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row1}")
    
    elif detectSingle(row1):
        if abs(row1_eval) != single_eval:
            raise ValueError(f"Invalid! Detected Single but Eval was {row1_eval}")
        
        open_A = row1_indeces[row1.index(0)]
        open_B = row1_indeces[row1.index(0, row1.index(0) + 1)]

        if row1_eval > 0:
            if open_A in p1_threat_spaces or open_B in p1_threat_spaces:
                score += 0
            else:
                score += row1_eval
        
        elif row1_eval < 0:
            if open_A in p2_threat_spaces or open_B in p2_threat_spaces:
                score += 0
            else:
                score += row1_eval

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
            else:
                score += row2_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row2_eval < 0:
            player2_threat = True
            p2_threat_tile = row2_indeces[row2.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += row2_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row2}")
    
    elif detectSingle(row2):
        if row2_eval > 0:
            p1_open_A = row2_indeces[row2.index(0)]
            p1_open_B = row2_indeces[row2.index(0, row2.index(0) + 1)]

            if p1_open_A in p1_threat_spaces or p1_open_B in p1_threat_spaces:
                score += 0
            else:
                score += row2_eval

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
            else:
                score += row3_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif row3_eval < 0:
            player2_threat = True
            p2_threat_tile = row3_indeces[row3.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += row3_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {row3}")
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
            else:
                score += col1_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col1_eval < 0:
            player2_threat = True
            p2_threat_tile = col1_indeces[col1.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += col1_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col1}")
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
            else:
                score += col2_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col2_eval < 0:
            player2_threat = True
            p2_threat_tile = col2_indeces[col2.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += col2_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col2}")
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
            else:
                score += col3_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif col3_eval < 0:
            player2_threat = True
            p2_threat_tile = col3_indeces[col3.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += col3_eval
                p2_threat_spaces.add(p2_threat_tile)
                
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {col3}")
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
            else:
                score += diagTB_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif diagTB_eval < 0:
            player2_threat = True
            p2_threat_tile = diagTB_indeces[diagTB.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += diagTB_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {diagTB}")
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
            else:
                score += diagBT_eval
                p1_threat_spaces.add(p1_threat_tile)
                
        elif diagBT_eval < 0:
            player2_threat = True
            p2_threat_tile = diagBT_indeces[diagBT.index(0)]
            
            if p2_threat_tile in p2_threat_spaces:
                score += 0
            else:
                score += diagBT_eval
                p2_threat_spaces.add(p2_threat_tile)
        else:
            raise ValueError(f"Invalid! Threat Detected but line eval was 0, line was {diagBT}")
    else:
        score += diagBT_eval

    # Check for conflicting threats, tone down final score
    if player1_threat and player2_threat:
        if empties == 1:
            return 0
        if empties == 2:
            if len(p1_threat_spaces) == 1 and len(p2_threat_spaces) == 1:
                return 0
        else:
            final_score = score * 0.75
            return round(final_score, 2)

    final_score = round(score, 2)
    return final_score