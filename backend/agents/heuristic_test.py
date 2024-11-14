import numpy as np
import test_utils as utils
import random
from collections import defaultdict
import trueskill
import os
import sys
import time

from bot.randy import RandomAgent
from bot.monkey import MonkeyAgent
from bot.jardy import GardenerAgent
from bot.jardito import JardineritoAgent
from bot.maxi import MaximilianoAgent
from bot.taylor import TaylorAgent
from bot.straightArrow import StraightArrowAgent
from bot.iterold import IteroldAgent
from bot.itterino import ItterinoAgent
from bot.ordy import TidyPodatorAgent
from bot.twinny import TwinPrunerAgent
from foofinder import FooFinderAgent
from bot.gardentranspositor import GardenTranspositorAgent
from bot.itervanbytes import IterVanBytesAgent
from bot.jarditonomid import JardineritoAntiMidAgent
from bot.jarditobetter import BetterJardineritoAgent
from bot.itterinobetter import BetterItterinoAgent

# Agents Initializations
RandomAgent = RandomAgent()
MonkeyAgent = MonkeyAgent()
GardenerAgent = GardenerAgent()
JardineritoAgent = JardineritoAgent()
MaximilianoAgent = MaximilianoAgent()
TaylorAgent = TaylorAgent()
StraightArrowAgent = StraightArrowAgent()
IteroldAgent = IteroldAgent()
ItterinoAgent = ItterinoAgent()
TidyPodatorAgent = TidyPodatorAgent()
TwinPrunerAgent = TwinPrunerAgent()
FooFinderAgent = FooFinderAgent()
GardenTranspositorAgent = GardenTranspositorAgent()
IterVanBytesAgent = IterVanBytesAgent()
JardineritoAntiMidAgent = JardineritoAntiMidAgent()
BetterJardineritoAgent = BetterJardineritoAgent()
BetterItterinoAgent = BetterItterinoAgent()

# Define Local Boards
local_Empty = np.array([[0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]])  # Random board, no meaningful characteristics

local_Rnd_1 = np.array([[1, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]])  # Random board, no meaningful characteristics

local_Rnd_2 = np.array([[1, 0, 0],
                        [0, 0, 0],
                        [-1, 0, 0]])  # Random board

local_Rnd_3 = np.array([[1, 0, -1],
                        [0, 0, 0],
                        [-1, 0, 1]])  # Random board

local_Rnd_4 = np.array([[0, 1, 0],
                        [1, -1, 1],
                        [0, 1, 0]])  # Random board

local_Rnd_5 = np.array([[1, -1, 1],
                        [0, 0, 1],
                        [1, 1, -1]])  # Random board

local_Rnd_6 = np.array([[1, 0, 0],
                        [0, 0, -1],
                        [-1, -1, 0]])  # Random board

local_topOne_1 = np.array([[0, 0, 0],
                        [0, 1, 1],
                        [0, 1, 1]])  # Random board

local_topTwo_1 = np.array([[0, 0, 0],
                        [0, -1, -1],
                        [0, -1, -1]])  # Random board

local_topOne_2 = np.array([[0, 1, 1],
                        [1, 0, 1],
                        [1, 1, 0]])  # Random board

local_topTwo_2 = np.array([[0, -1, -1],
                        [-1, 0, -1],
                        [-1, -1, 0]])  # Random board

local_OneWon_1 = np.array([[1, 1, 1],
                    [0, -1, -1],
                    [0, 0, -1]])  # Player 1 wins on the top row

local_OneWon_2 = np.array([[0, -1, 1],
                    [0, 1, -1],
                    [1, 0, -1]])  # Player 1 wins on the diagonal

local_OneWon_3 = np.array([[-1, -1, 0],
                    [1, 1, 1],
                    [0, -1, 0]])  # Player 1 wins on the middle row

local_TwoWon_1 = np.array([[0, -1, 1],
                    [-1, -1, 1],
                    [1, -1, 0]])  # Player -1 wins on the middle column

local_TwoWon_2 = np.array([[-1, 1, 0],
                    [1, -1, 0],
                    [1, 0, -1]])  # Player -1 wins on the diagonal

local_TwoWon_3 = np.array([[-1, -1, -1],
                    [1, 1, 0],
                    [0, 1, 0]])  # Player -1 wins on the top row

local_BothWnbl_1 = np.array([[1, -1, -1],
                    [1, -1, -1],
                    [0, 1, 1]])  # No winner yet

local_BothWnbl_2 = np.array([[1, 1, 0],
                    [-1, -1, 0],
                    [0, 0, 0]])  # Not a win yet, but close

local_BothWnbl_3 = np.array([[0, 0, 0],
                            [1, 1, 0],
                            [-1, -1, 0]])  # Another close board without a winner

local_BothWnbl_4 = np.array([[-1, -1, 0],
                            [-1, 0, 1],
                            [0, 1, 1]]) # winnable by 1 in (0, 2), (2, 0) || winnable by -1 in (0, 2), (2, 0)

local_Draw_1 = np.array([[1, -1, 1],
                            [1, -1, -1],
                            [-1, 1, 1]])  # Draw (no more moves possible)

local_toDraw_1 = np.array([[1, -1, 1],
                            [-1, -1, 1],
                            [0, 1, -1]])  # Secured Draw (will always be Draw)

local_toDraw_2 = np.array([[-1, 0, 1],
                            [1, -1, -1],
                            [-1, 1, 1]]) # Secured Draw (will always be Draw)

local_OneWnbl_1 = np.array([[1, 0, 1],
                            [1, 0, 0],
                            [0, 1, 1]]) # winnable by 1 in (0, 1), (1, 1), (1, 2), (2, 0)

local_TwoWnbl_1 = np.array([[0, 0, 0],
                            [-1, -1, 0],
                            [-1, -1, 0]]) # winnable by -1 in (0, 0), (0, 1), (0, 2), (1, 2), (2, 2)

local_great_pOne = np.array([[1, 0, 1],
                            [0, 1, 0],
                            [0, 0, 0]])

local_good_pOne = np.array([[1, 0, 1],
                            [0, 1, 0],
                            [0, 0, 0]])

local_mid_pOne = np.array([[1, 0, 0],
                            [0, 0, 1],
                            [0, 1, 0]])

# Define Global Boards
global_mid = np.zeros((3, 3, 3, 3), dtype=int)
global_mid[1, 1] = local_TwoWon_1
global_mid[0, 0] = local_OneWon_2
global_mid[2, 2] = local_OneWon_3

global_alr = np.zeros((3, 3, 3, 3), dtype=int)
global_alr[0, 0] = local_OneWon_1
global_alr[2, 1] = local_OneWon_2
global_alr[1, 2] = local_OneWon_3

global_good = np.zeros((3, 3, 3, 3), dtype=int)
global_good[1, 0] = local_OneWon_1
global_good[2, 0] = local_OneWon_2
global_good[2, 1] = local_OneWon_3

global_great = np.zeros((3, 3, 3, 3), dtype=int)
global_great[0, 0] = local_OneWon_1
global_great[1, 1] = local_OneWon_2
global_great[0, 2] = local_OneWon_3

global_victory = np.zeros((3, 3, 3, 3), dtype=int)
global_victory[0, 0] = local_OneWon_1
global_victory[1, 1] = local_OneWon_2
global_victory[2, 2] = local_OneWon_3

# Original Evals
og_eval_mid = JardineritoAgent.boardBalance(global_mid)
og_eval_alr = JardineritoAgent.boardBalance(global_alr)
og_eval_good = JardineritoAgent.boardBalance(global_good)
og_eval_great = JardineritoAgent.boardBalance(global_great)

# Better Evals
better_eval_mid = BetterJardineritoAgent.boardBalance(global_mid)
better_eval_alr = BetterJardineritoAgent.boardBalance(global_alr)
better_eval_good = BetterJardineritoAgent.boardBalance(global_good)
better_eval_great = BetterJardineritoAgent.boardBalance(global_great)

# Print
print(f"Mid Board Evals: Original: {og_eval_mid} | Better: {better_eval_mid}")
print(f"Alright Board Evals: Original: {og_eval_alr} | Better: {better_eval_alr}")
print(f"Good Board Evals: Original: {og_eval_good} | Better: {better_eval_good}")
print(f"Great Board Evals: Original: {og_eval_great} | Better: {better_eval_great}")
