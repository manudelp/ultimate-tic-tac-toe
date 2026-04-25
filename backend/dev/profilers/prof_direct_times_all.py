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

# Aca hacer que haga un for con los boards y los btps, y que en cada uno printee