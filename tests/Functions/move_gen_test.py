import numpy as np
import timeit

# Setup: Create a small random array and precompute all indices as a NumPy array
board = np.random.randint(0, 2, size=(3, 3), dtype=int)  # 3D array with 0s and 1s
arr = np.argwhere(board == 0)  # Get all indices of 1s in the 3D array

# Test Ways to convert it from a 2d array, to a list of arrays
list_version1 = list(arr)
print(f"v1: {list_version1}, \nstructure type: {type(list_version1)}, \nexample item: {list_version1[2]}, \nexample item-slice: {list_version1[1][1]}, \nitem-type: {type(list_version1[0])}\n")

list_version2 = [row for row in arr]
print(f"v2: {list_version2}, \nstructure type: {type(list_version2)}, \nexample item: {list_version1[2]}, \nexample item-slice: {list_version1[1][1]}, \nitem-type: {type(list_version2[0])}\n")

list_version3 = [arr[i] for i in range(len(arr))]
print(f"v3: {list_version3}, \nstructure type: {type(list_version3)}, \nexample item: {list_version1[2]}, \nexample item-slice: {list_version1[1][1]}, \nitem-type: {type(list_version3[0])}\n")

list_version4 = [arr[i, :] for i in range(len(arr))]
print(f"v4: {list_version4}, \nstructure type: {type(list_version4)}, \nexample item: {list_version1[2]}, \nexample item-slice: {list_version1[1][1]}, \nitem-type: {type(list_version4[0])}\n")

# Test Times
def v1(arr):
    return arr.tolist()

def v2(arr):
    return [row for row in arr]

def v3(arr):
    return [arr[i] for i in range(len(arr))]

def v4(arr):
    return [arr[i, :] for i in range(len(arr))]

iters = 7_000_000
v1_time = timeit.timeit(lambda: v1(arr), number=iters)
v2_time = timeit.timeit(lambda: v2(arr), number=iters)
v3_time = timeit.timeit(lambda: v3(arr), number=iters)
v4_time = timeit.timeit(lambda: v4(arr), number=iters)

print(f"Detailed Time Tests after {iters} iterations!")
print(f"v1: {v1_time}")
print(f"v2: {v2_time}")
print(f"v3: {v3_time}")
print(f"v4: {v4_time}")