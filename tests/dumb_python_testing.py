import numpy as np
import time 

t0 = time.time()

for i in range(100):
    # Example list of NumPy arrays
    moves_to_try = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])]
    current_best_move = np.array([4, 5, 6])

# Find the index of the current_best_move
index_to_remove = next((i for i, arr in enumerate(moves_to_try) if np.array_equal(arr, current_best_move)), None)

if index_to_remove is not None:
    # Remove the array from the list
    del moves_to_try[index_to_remove]
    # Insert it at the beginning of the list
    moves_to_try.insert(0, current_best_move)

t1 = time.time()

print(t1-t0)

print(moves_to_try)
