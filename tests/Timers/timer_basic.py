import timeit
import numpy as np
import random

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

list_random = [20, 291, 9, 3829, 291, 29, 38, 11, 6]

def A(lista):
    a0, a1, a2, a3, a4, a5, a6, a7, a8 = lista
    return None

def B(lista):
    a0 = lista[0]
    a1 = lista[1]
    a2 = lista[2]
    a3 = lista[3]
    a4 = lista[4]
    a5 = lista[5]
    a6 = lista[6]
    a7 = lista[7]
    a8 = lista[8]
    return None

# Timeit tests with direct lambda calls
iters = 32_000
samples = 1600
total_iters = iters * samples # 2_062_500_000
total_time_A = 0
total_time_B = 0

for i in range(samples):
    time_A = timeit.timeit(lambda: A(list_random), number=iters)
    time_B = timeit.timeit(lambda: B(list_random), number=iters)

    if A(list_random) != B(list_random):
        raise ValueError(f"They were not equal! Their values are: A({A(list_random)}), B({B(list_random)})! List was {list_random}")
    
    if i%250 == 0:
        percentage_completed = (i/samples) * 100
        print(f"Completed {percentage_completed:.2f}% of the total samples...")

    total_time_A += time_A
    total_time_B += time_B

# Print the time results
print(f"Below are the Time Results after {total_iters} total iterations")
print(f"Time for Option A: {total_time_A:.4f} seconds")
print(f"Time for Option B: {total_time_B:.4f} seconds")

time_difference = (total_time_A - total_time_B) / total_time_A
min_diff = 0.05

if time_difference < min_diff:
    time_percentage_slower_B = ((total_time_B - total_time_A) / total_time_B) * 100
    print(f"Option A was faster! Option B was slower by {time_percentage_slower_B:.2f}%")
elif time_difference > min_diff:
    time_percentage_slower_A = ((total_time_A - total_time_B) / total_time_A) * 100
    print(f"Option B was faster! Option A was slower by {time_percentage_slower_A:.2f}%")
else:
    print("Both options took around the same")
