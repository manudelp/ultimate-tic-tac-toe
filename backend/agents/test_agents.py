import numpy as np
import test_utils as utils
import time
from bot.randy import RandomAgent
from bot.monkey import MonkeyAgent
from bot.jardy import GardenerAgent
from bot.taylor import TaylorAgent
from bot.straightArrow import StraightArrowAgent
from bot.iterold import IteroldAgent
from bot.itterino import ItterinoAgent
from bot.ordy import TidyPodatorAgent
from bot.twinny import TwinPrunerAgent
from bot.maxi import MaximilianoAgent
from foofinder import FooFinderAgent

# Initialize agents
AGENT1 = MaximilianoAgent()  # Replace with your chosen agent
AGENT2 = StraightArrowAgent()         # Replace with your chosen agent
ROUNDS = 15  # Number of rounds to play

# Initialize game board
board = np.zeros((3, 3, 3, 3), dtype=int)  # 4D board, initialized to zeros

# Run the simulation
t0 = time.time()
utils.play_multiple_games(AGENT1, AGENT2, ROUNDS)
t1 = time.time()
time_taken = t1 - t0

print(f"Time taken to play LITERALLY {ROUNDS} FUCKING rounds: {time_taken:.2f} seconds")
