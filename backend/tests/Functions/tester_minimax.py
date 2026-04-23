import numpy as np
import timeit

def balance(board):
    ''' Returns balance of the board, being the sum of the indices of each player's moves '''
    rows, cols, l_rows, l_cols = board.shape
    balance = 0

    for row in range(rows):
        for col in range(cols):
            for l_row in range(l_rows):
                for l_col in range(l_cols):
                    suma = row + col + l_row + l_col
                    if board[row, col, l_row, l_col] == 1:
                        balance += suma
                    elif board[row, col, l_row, l_col] == -1:
                        balance -= suma
    return balance
                    

def moveQuality(board, move):
    a, b, c, d = move
    board[a, b, c, d] = 1
    score = balance(board)
    board[a, b, c, d] = 0
    return score

board = np.random.randint((3, 3, 3, 3), dtype=int)

moves = np.argwhere(board == 0)

def array_sort(board, moves):
    sorted_indices = np.argsort([-moveQuality(board, move) for move in moves])  # Negate to sort descending
    sorted_moves = moves[sorted_indices]
    return sorted_moves

def custom_sort(board, moves):
    # Convert NumPy array to list, sort, and return sorted list
    return sorted(moves, key=lambda move: moveQuality(board, move), reverse=True)

array_sorted = array_sort(board, moves)
custom_sorted = custom_sort(board, moves)

# print(f"Array sort: {array_sorted}")
# print(f"Custom sort: {custom_sorted}")

# Iterable Test
# for i, move in enumerate(array_sorted):
#     print(f"Rank {i+1} is {move} by array_sorted")

# print("\n")

# for i, move in enumerate(custom_sorted):
#     print(f"Rank {i+1} is {move} by custom_sorted")

iters = 1_000
print(f"Array sort time for {iters} iterations: {timeit.timeit(lambda: array_sort(board, moves), number=iters)}")
print(f"Custom sort time for {iters} iterations: {timeit.timeit(lambda: custom_sort(moves, board), number=iters)}")


