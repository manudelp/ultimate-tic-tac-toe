import numpy as np
import test_utils as utils
from bot.randy import RandomAgent
from bot.monkey import MonkeyAgent
from bot.jardy import GardenerAgent
from bot.taylor import TaylorAgent
from bot.straightArrow import StraightArrowAgent
from bot.iterold import IteroldAgent
from bot.itterino import ItterinoAgent
from bot.ordy import TidyPodatorAgent
from bot.twinny import TwinPrunerAgent
from foofinder import FooFinderAgent

# Initialize agents
AGENT1 = StraightArrowAgent()  # Replace with your chosen agent
AGENT2 = RandomAgent()         # Replace with your chosen agent
ROUNDS = 10  # Number of rounds to play

# Initialize game board
board = np.zeros((3, 3, 3, 3), dtype=int)  # 4D board, initialized to zeros

# Run the simulation
utils.play_multiple_games(AGENT1, AGENT2, ROUNDS)
