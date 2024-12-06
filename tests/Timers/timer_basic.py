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

def A(lista, coefs):
    a0, a1, a2, a3, a4, a5, a6, a7, a8 = lista
    b0, b1, b2, b3, b4, b5, b6, b7, b8 = coefs
    result = a0*b0 + a1*b1 + a2*b2 + a3*b3 + a4*b4 + a5*b5 + a6*b6 + a7*b7 + a8*b8
    return result

def B(lista, coefs):
    a_arr = np.array(lista)
    b_arr = np.array(coefs)
    result = np.dot(a_arr, b_arr)
    return result

# def C(lista, coefs):
#     a_list = lista
#     b_list = coefs
#     result = sum([a*b for a,b in zip(a_list, b_list)])
#     return result

# def D(lista, coefs):
#     a_list = lista
#     b_list = coefs
#     result = a_list @ b_list
#     return result

# Timeit tests with direct lambda calls
iters = 10_000
samples = 1200
total_iters = iters * samples # 2_062_500_000
total_time_A = 0
total_time_B = 0
total_time_C = 0
total_time_D = 0

for i in range(samples):
    a_list_rnd = random.sample(range(1, 100), 9)
    b_list_rnd = random.sample(range(1, 100), 9)
    
    time_A = timeit.timeit(lambda: A(a_list_rnd, b_list_rnd), number=iters)
    time_B = timeit.timeit(lambda: B(a_list_rnd, b_list_rnd), number=iters)
    # time_C = timeit.timeit(lambda: C(a_list_rnd, b_list_rnd), number=iters)
    # time_D = timeit.timeit(lambda: D(a_list_rnd, b_list_rnd), number=iters)

    # if not (A(a_list_rnd, b_list_rnd) == B(a_list_rnd, b_list_rnd) == C(a_list_rnd, b_list_rnd) == D(a_list_rnd, b_list_rnd)):
    #     raise ValueError(f"Results are not the same! Results are {A(a_list_rnd, b_list_rnd)}, {B(a_list_rnd, b_list_rnd)}, {C(a_list_rnd, b_list_rnd)}, {D(a_list_rnd, b_list_rnd)} for parameters {a_list_rnd, b_list_rnd}")
    
    if i%200 == 0:
        percentage_completed = (i/samples) * 100
        print(f"Completed {percentage_completed:.2f}% of the total samples...")

    total_time_A += time_A
    total_time_B += time_B
    # total_time_C += time_C
    # total_time_D += time_D

# Print the time results
print(f"Below are the Time Results after {total_iters} total iterations")
print(f"Time for Option A: {total_time_A:.4f} seconds")
print(f"Time for Option B: {total_time_B:.4f} seconds")
# print(f"Time for Option C: {total_time_C:.4f} seconds")
# print(f"Time for Option D: {total_time_D:.4f} seconds")