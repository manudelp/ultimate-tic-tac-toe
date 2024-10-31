import sys
import os
import timeit
import numpy as np
# Determine the root directory of the project
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the root directory to sys.path
sys.path.append(root_dir)
from backend.agents.foofinder import FooFinderAgent
agent = FooFinderAgent()


board = np.zeros((3, 3, 3, 3), dtype=int)
# endregion

def gen_2d_board():
    return np.random.randint(-1, 2, (3, 3), dtype=np.int64)

def gen_4d_board():
    return np.random.randint(-1, 2, (3, 3, 3, 3), dtype=np.int64)

def lineEval(line, player=1):
    # TIMEIT APPROVED ✅
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

def localBoardEval(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    '''
    # TODO If board is on the precomputed hash, then fetch it and return the value!
    # precomputed boards logic

    score = 0

    # Rows
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

    # Columns
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

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    # If the Local Board is Won, cut and return ±10
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    # If the Local Board is Won, cut and return ±10
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    return score

def balance(board):
    rows, cols, *_ = board.shape
    balance = 0

    # Auxiliar For Now!
    for r in range(rows):
        for c in range(cols):
            localBoard = board[r, c]
            balance += agent.get_eval(localBoard)
    
    return balance

def moveQuality(board, move):
    a, b, c, d = move
    board[a, b, c, d] = 1
    score = balance(board)
    board[a, b, c, d] = 0
    return score

def array_sort_method(board, moves):
    ''' CHANGE MY NAME FROM array_sort_method TO THE ACTUAL FUNCTION, USE CTRL+H TO REPLACE ON ALL '''
    moves = np.array(moves)
    sorted_indices = np.argsort([-moveQuality(board, move) for move in moves])  # Negate to sort descending
    sorted_moves = moves[sorted_indices]
    return sorted_moves

def list_sort_method(board, moves):
    ''' CHANGE MY NAME FROM list_sort_method TO THE ACTUAL FUNCTION, USE CTRL+H TO REPLACE ON ALL '''
    return sorted(moves, key=lambda move: moveQuality(board, move), reverse=True)

# def C(board):
#     pass

final_time_array_sort_method = 0
final_time_list_sort_method = 0
final_time_C_placeholder = 0
aux = 0

iters = 10_000
samples = 20
looks = samples//10
total_iters = iters * samples

# Timeit tests with direct lambda calls
for i in range(samples):

    # board = gen_2d_board()
    board = gen_4d_board()
    moves = np.argwhere(board == 0)
    moves = [np.array([a, b, c, d]) for a, b, c, d in moves]

    time_array_sort_method = timeit.timeit(lambda: array_sort_method(board, moves), number=iters)
    final_time_array_sort_method += time_array_sort_method

    time_list_sort_method = timeit.timeit(lambda: list_sort_method(board, moves), number=iters)
    final_time_list_sort_method += time_list_sort_method

    # time_C = timeit.timeit(lambda: C(board), number=iters)
    # final_time_C += time_C

    array_sort_method_value = array_sort_method(board, moves)
    list_sort_method_value = list_sort_method(board, moves)

    # if abs(array_sort_method_value - list_sort_method_value) > 0.001:
    #     raise ValueError(f"Error at turn {i}! array_sort_method: {array_sort_method_value}, list_sort_method: {list_sort_method_value} while board is {board}")

    if i%looks == 0:

        # Print the winner results
        print(f"array_sort_method at turn {i} returns: {array_sort_method_value}")
        print(f"list_sort_method at turn {i} returns: {list_sort_method_value}")
        # print(f"C at turn {i} returns: {C(board)}")

        # Print the time results
        print(f"Running array_sort_method at turn {i} takes : {time_array_sort_method:.4f} seconds")
        print(f"Running list_sort_method at turn {i} takes : {time_list_sort_method:.4f} seconds")
        # print(f"Running C at turn {i} takes : {time_C:.4f} seconds")
        print("\n")

# Print the final time results
print("\n")
print(f"Final time for array_sort_method: {final_time_array_sort_method:.4f} seconds, after running {total_iters} iterations")
print(f"Final time for list_sort_method: {final_time_list_sort_method:.4f} seconds, after running {total_iters} iterations")
# print(f"Final time for Option C: {final_time_C:.4f} seconds, after running {total_iters} iterations")