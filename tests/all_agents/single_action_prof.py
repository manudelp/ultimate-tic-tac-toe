import numpy as np
import time
import timeit
from ...backend.api.utils import fancyBoardPrinter, get_board_results, load_winning_boards, get_GlobalWinner
from ...backend.agents.bot.iterold import IteroldAgent
from ...backend.agents.bot.itterino import ItterinoAgent
from ...backend.agents.bot.jardy import GardenerAgent
from ...backend.agents.bot.monkey import MonkeyAgent
from ...backend.agents.bot.ordy import TidyPodatorAgent
from ...backend.agents.bot.straightArrow import StraightArrowAgent
from ...backend.agents.bot.twinny import TwinPrunerAgent
from ...backend.agents.bot.taylor import TaylorAgent
from ...backend.agents.bot.randy import RandomAgent
from ...backend.agents.foofinder import FooFinderAgent

# Agents
randy = RandomAgent()
monkey = MonkeyAgent()
gardener = GardenerAgent()
taylor = TaylorAgent()
straight = StraightArrowAgent()
iterold = IteroldAgent()
itterino = ItterinoAgent()
ordy = TidyPodatorAgent()
twinny = TwinPrunerAgent()
foofinder = FooFinderAgent()

# Board Seed
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






