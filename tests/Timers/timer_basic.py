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

def A(coord):
    return coord in [(0, 0), (0, 2), (2, 0), (2, 2)]

def B(x, y):
    return (x+y) % 2 == 1

def C(coord):
    ''' Center '''
    return coord == (1, 1)

# Timeit tests with direct lambda calls
iters = 750_000
samples = 2750
total_iters = iters * samples # 2_062_500_000
total_time_A = 0
total_time_B = 0
total_time_C = 0

for i in range(samples):
    coord = random.randint(0, 2), random.randint(0, 2)
    x, y = coord

    if i % 250 == 0:
        if A(coord):
            state = "a corner"
        elif B(x, y):
            state = "an edge"
        elif C(coord):
            state = "a center"
        print(f"At Iteration {i}, {coord} is {state} position")

    time_A = timeit.timeit(lambda: A(coord), number=iters)
    time_B = timeit.timeit(lambda: B(x, y), number=iters)
    time_C = timeit.timeit(lambda: C(coord), number=iters)

    if A(coord) == B(x, y) == C(coord):
        raise ValueError(f"They were equal! Their values are: A({A(coord)}), B({B(x, y)}), C({C(coord)})! Coord was {coord}")

    total_time_A += time_A
    total_time_B += time_B
    total_time_C += time_C

# Print the time results
print(f"Below are the Time Results after {total_iters} total iterations")
print(f"Time for Option A: {total_time_A:.4f} seconds")
print(f"Time for Option B: {total_time_B:.4f} seconds")
print(f"Time for Option C: {total_time_C:.4f} seconds")

