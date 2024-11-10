import numpy as np
import time 

# t0 = time.time()

# for i in range(100):
#     # Example list of NumPy arrays
#     moves_to_try = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])]
#     current_best_move = np.array([4, 5, 6])

# # Find the index of the current_best_move
# index_to_remove = next((i for i, arr in enumerate(moves_to_try) if np.array_equal(arr, current_best_move)), None)

# if index_to_remove is not None:
#     # Remove the array from the list
#     del moves_to_try[index_to_remove]
#     # Insert it at the beginning of the list
#     moves_to_try.insert(0, current_best_move)

# t1 = time.time()

# print(t1-t0)

# print(moves_to_try)

# def list_cutoffs(ordered_list, cut_percentage) -> list:
#     ''' Given an ordered list, cuts off the last/bottom 'cut_percentage' items of the list 
#     and returns the new list with the remaining first elements '''
#     length = len(ordered_list)
#     moves_to_delete = int(length * cut_percentage)
#     moves_to_keep = length - moves_to_delete
#     return ordered_list[:moves_to_keep]

# # Generate random list of numpy arrays
# my_list = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9]), np.array([10, 11, 12]), np.array([13, 14, 15]), np.array([16, 17, 18]), np.array([19, 20, 21]), np.array([22, 23, 24]), np.array([25, 26, 27]), np.array([28, 29, 30])]
# print(f"Length of my_list: {len(my_list)}")
# print(f"Original list: {my_list}\n")
# cut_percentage = 0.3
# new_list = list_cutoffs(my_list, cut_percentage)
# print(f"Length of new_list: {len(new_list)}")
# print(f"New list: {new_list}")

# results_balance = 0.8
# balance = results_balance * ((1 + abs(results_balance))**2.5) * 1.85
# print(balance)

a = -6.1
b = -0.8
c = -3.2
d = 5.9
e = 6.4
f = 2.5

a_p = int(a/6)
b_p = int(b/6)
c_p = int(c/6)
d_p = int(d/6)
e_p = int(e/6)
f_p = int(f/6)

print(f"a_p: {a_p}")
print(f"b_p: {b_p}")
print(f"c_p: {c_p}")
print(f"d_p: {d_p}")
print(f"e_p: {e_p}")
print(f"f_p: {f_p}")