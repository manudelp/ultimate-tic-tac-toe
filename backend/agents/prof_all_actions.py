import numpy as np
import time
import timeit
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

# Main Bots
from bots.randy import RandomAgent
from bots.monkey import MonkeyAgent
from bots.greedy import GreedyAgent
from bots.jardito import JardineritoAgent
from bots.arthy import ArthyAgent
from bots.foofinder import FooFinderAgent

# Other Dev Bots
from others.jardy import GardenerAgent
from others.itterinobetter import BetterItterinoAgent
from others.taylor import TaylorAgent
from others.iterold import IteroldAgent
from others.itterino import ItterinoAgent
from others.ordy import TidyPodatorAgent
from others.twinny import TwinPrunerAgent
from others.maxi import MaximilianoAgent
from others.gardentranspositor import GardenTranspositorAgent
from others.itervanbytes import IterVanBytesAgent
from others.jarditonomid import JardineritoAntiMidAgent
from others.jarditobetter import BetterJardineritoAgent
from others.alterjardito import AlterJardineritoAgent

# Agents
randy = RandomAgent()
monkey = MonkeyAgent()
gardener = GardenerAgent()
taylor = TaylorAgent()
straight = GreedyAgent()
iterold = IteroldAgent()
itterino = ItterinoAgent()
ordy = TidyPodatorAgent()
twinny = TwinPrunerAgent()
foofinder = FooFinderAgent()

# Board Seed
seeds_list = [22, 25, 29, 36, 74, 23843005]
np.random.seed(22)
# Seeds to consider:
# Seed 22, playables list is [(0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
# Seed 25, playables list is [(0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 2)]
# Seed 29. playables list is [(0, 0), (0, 1)] (pronto todo acabara)
# Seed 36, playables list is [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2)]
# Seed 74, playables list is [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)], 40 playables
# Seed 23843005, playables list is [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)], 53 playables (estamo loco)

# Board Set Up
board = np.random.randint(-1, 2, (3, 3, 3, 3))
board_to_play = None

parameters_list = []
for seed in seeds_list:
    np.random.seed(seed)
    board = np.random.randint(-1, 2, (3, 3, 3, 3))
    if seed > 100_000 or seed == 25:
        board_to_play = None
    else:
        board_to_play = (0, 1)
    parameters_list.append((board, board_to_play))

# Move Getting Functions
def get_randy_move(board, board_to_play):
    return randy.action(board=board, board_to_play=board_to_play)

def get_monkey_move(board, board_to_play):
    return monkey.action(board=board, board_to_play=board_to_play)

def get_gardener_move(board, board_to_play):
    return gardener.action(board=board, board_to_play=board_to_play)

def get_taylor_move(board, board_to_play):
    return taylor.action(board=board, board_to_play=board_to_play)

def get_straight_move(board, board_to_play):
    return straight.action(board=board, board_to_play=board_to_play)

def get_iterold_move(board, board_to_play):
    return iterold.action(board=board, board_to_play=board_to_play)

def get_itterino_move(board, board_to_play):
    return itterino.action(board=board, board_to_play=board_to_play)

def get_ordy_move(board, board_to_play):
    return ordy.action(board=board, board_to_play=board_to_play)

def get_twinny_move(board, board_to_play):
    return twinny.action(board=board, board_to_play=board_to_play)

def get_foofinder_move(board, board_to_play):
    return foofinder.action(board=board, board_to_play=board_to_play)

# Plain Time Testers

t_before_randy = time.time()
randy_move = get_randy_move(board, board_to_play=None)
t_after_randy = time.time()

t_before_monkey = time.time()
monkey_move = get_monkey_move(board, board_to_play=None)
t_after_monkey = time.time()

t_before_gardener = time.time()
gardener_move = get_gardener_move(board, board_to_play=None)
t_after_gardener = time.time()

t_before_taylor = time.time()
taylor_move = get_taylor_move(board, board_to_play=None)
t_after_taylor = time.time()

t_before_straight = time.time()
straight_move = get_straight_move(board, board_to_play=None)
t_after_straight = time.time()

t_before_iterold = time.time()
iterold_move = get_iterold_move(board, board_to_play=None)
t_after_iterold = time.time()

t_before_itterino = time.time()
itterino_move = get_itterino_move(board, board_to_play=None)
t_after_itterino = time.time()

t_before_ordy = time.time()
ordy_move = get_ordy_move(board, board_to_play=None)
t_after_ordy = time.time()

t_before_twinny = time.time()
twinny_move = get_twinny_move(board, board_to_play=None)
t_after_twinny = time.time()

t_before_foofinder = time.time()
foofinder_move = get_foofinder_move(board, board_to_play=None)
t_after_foofinder = time.time()

randy_time = t_after_randy - t_before_randy
monkey_time = t_after_monkey - t_before_monkey
gardener_time = t_after_gardener - t_before_gardener
taylor_time = t_after_taylor - t_before_taylor
straight_time = t_after_straight - t_before_straight
iterold_time = t_after_iterold - t_before_iterold
itterino_time = t_after_itterino - t_before_itterino
ordy_time = t_after_ordy - t_before_ordy
twinny_time = t_after_twinny - t_before_twinny
foofinder_time = t_after_foofinder - t_before_foofinder

# TIMEIT BELOW  
ITERS = 10
SAMPLE_SIZE = len(seeds_list)

# Timeit Single Board Tester
time_simple_randy = timeit.timeit(lambda: get_randy_move(board=board, board_to_play=None), number=ITERS)
time_simple_monkey = timeit.timeit(lambda: get_monkey_move(board=board, board_to_play=None), number=ITERS)
time_simple_gardener = timeit.timeit(lambda: get_gardener_move(board=board, board_to_play=None), number=ITERS)
time_simple_taylor = timeit.timeit(lambda: get_taylor_move(board=board, board_to_play=None), number=ITERS)
time_simple_straight = timeit.timeit(lambda: get_straight_move(board=board, board_to_play=None), number=ITERS)
time_simple_iterold = timeit.timeit(lambda: get_iterold_move(board=board, board_to_play=None), number=ITERS)
time_simple_itterino = timeit.timeit(lambda: get_itterino_move(board=board, board_to_play=None), number=ITERS)
time_simple_ordy = timeit.timeit(lambda: get_ordy_move(board=board, board_to_play=None), number=ITERS)
time_simple_twinny = timeit.timeit(lambda: get_twinny_move(board=board, board_to_play=None), number=ITERS)
time_simple_foofinder = timeit.timeit(lambda: get_foofinder_move(board=board, board_to_play=None), number=ITERS)

# Timeit Advanced Tester, all bpt Nones
total_time_randy_nones = 0
total_time_monkey_nones = 0
total_time_gardener_nones = 0
total_time_taylor_nones = 0
total_time_straight_nones = 0
total_time_iterold_nones = 0
total_time_itterino_nones = 0
total_time_ordy_nones = 0
total_time_twinny_nones = 0
total_time_foofinder_nones = 0

for param in parameters_list:
    board = param[0]
    board_to_play = None
    total_time_randy_nones += timeit.timeit(lambda: get_randy_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_monkey_nones += timeit.timeit(lambda: get_monkey_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_gardener_nones += timeit.timeit(lambda: get_gardener_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_taylor_nones += timeit.timeit(lambda: get_taylor_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_straight_nones += timeit.timeit(lambda: get_straight_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_iterold_nones += timeit.timeit(lambda: get_iterold_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_itterino_nones += timeit.timeit(lambda: get_itterino_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_ordy_nones += timeit.timeit(lambda: get_ordy_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_twinny_nones += timeit.timeit(lambda: get_twinny_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_foofinder_nones += timeit.timeit(lambda: get_foofinder_move(board=board, board_to_play=board_to_play), number=ITERS)

# Timeit Advanced Tester, all bpt appropriate
total_time_randy_aprop = 0
total_time_monkey_aprop = 0
total_time_gardener_aprop = 0
total_time_taylor_aprop = 0
total_time_straight_aprop = 0
total_time_iterold_aprop = 0
total_time_itterino_aprop = 0
total_time_ordy_aprop = 0
total_time_twinny_aprop = 0
total_time_foofinder_aprop = 0

for param in parameters_list:
    board = param[0]
    board_to_play = param[1]
    total_time_randy_aprop += timeit.timeit(lambda: get_randy_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_monkey_aprop += timeit.timeit(lambda: get_monkey_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_gardener_aprop += timeit.timeit(lambda: get_gardener_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_taylor_aprop += timeit.timeit(lambda: get_taylor_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_straight_aprop += timeit.timeit(lambda: get_straight_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_iterold_aprop += timeit.timeit(lambda: get_iterold_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_itterino_aprop += timeit.timeit(lambda: get_itterino_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_ordy_aprop += timeit.timeit(lambda: get_ordy_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_twinny_aprop += timeit.timeit(lambda: get_twinny_move(board=board, board_to_play=board_to_play), number=ITERS)
    total_time_foofinder_aprop += timeit.timeit(lambda: get_foofinder_move(board=board, board_to_play=board_to_play), number=ITERS)

# NOW PRINT ALL THE TOTAL TIME RESULTS FROM ALL TESTS

# First, print the simple time results, in Aqua Color
print(f"{Fore.AQUA}Simple Time Results:")
print(f"Randy: {randy_time:.4f} seconds")
print(f"Monkey: {monkey_time:.4f} seconds")
print(f"Gardener: {gardener_time:.4f} seconds")
print(f"Taylor: {taylor_time:.4f} seconds")
print(f"Straight: {straight_time:.4f} seconds")
print(f"Iterold: {iterold_time:.4f} seconds")
print(f"Itterino: {itterino_time:.4f} seconds")
print(f"Ordinator: {ordy_time:.4f} seconds")
print(f"Twinny: {twinny_time:.4f} seconds")
print(f"FooFinder: {foofinder_time:.4f} seconds")
print(Style.RESET_ALL)

# Now, print the timeit results, in Green Color
print(f"{Fore.GREEN}Timeit Single Board Results:")
print(f"Randy: {time_simple_randy:.4f} seconds")
print(f"Monkey: {time_simple_monkey:.4f} seconds")
print(f"Gardener: {time_simple_gardener:.4f} seconds")
print(f"Taylor: {time_simple_taylor:.4f} seconds")
print(f"Straight: {time_simple_straight:.4f} seconds")
print(f"Iterold: {time_simple_iterold:.4f} seconds")
print(f"Itterino: {time_simple_itterino:.4f} seconds")
print(f"Ordinator: {time_simple_ordy:.4f} seconds")
print(f"Twinny: {time_simple_twinny:.4f} seconds")
print(f"FooFinder: {time_simple_foofinder:.4f} seconds")

# Now, print the advanced timeit results, in lightred Color
print(f"{Fore.LIGHTRED_EX}Timeit Advanced bptNone  Results:")
print(f"Randy: {total_time_randy_nones:.4f} seconds")
print(f"Monkey: {total_time_monkey_nones:.4f} seconds")
print(f"Gardener: {total_time_gardener_nones:.4f} seconds")
print(f"Taylor: {total_time_taylor_nones:.4f} seconds")
print(f"Straight: {total_time_straight_nones:.4f} seconds")
print(f"Iterold: {total_time_iterold_nones:.4f} seconds")
print(f"Itterino: {total_time_itterino_nones:.4f} seconds")
print(f"Ordinator: {total_time_ordy_nones:.4f} seconds")
print(f"Twinny: {total_time_twinny_nones:.4f} seconds")
print(f"FooFinder: {total_time_foofinder_nones:.4f} seconds")
print(Style.RESET_ALL)

# Now, print the adavanced timeit results, in lightblue Color
print(f"{Fore.LIGHTBLUE_EX}Timeit Advanced bptAppropriate Results:")
print(f"Randy: {total_time_randy_aprop:.4f} seconds")
print(f"Monkey: {total_time_monkey_aprop:.4f} seconds")
print(f"Gardener: {total_time_gardener_aprop:.4f} seconds")
print(f"Taylor: {total_time_taylor_aprop:.4f} seconds")
print(f"Straight: {total_time_straight_aprop:.4f} seconds")
print(f"Iterold: {total_time_iterold_aprop:.4f} seconds")
print(f"Itterino: {total_time_itterino_aprop:.4f} seconds")
print(f"Ordinator: {total_time_ordy_aprop:.4f} seconds")
print(f"Twinny: {total_time_twinny_aprop:.4f} seconds")
print(f"FooFinder: {total_time_foofinder_aprop:.4f} seconds")
print(Style.RESET_ALL)



