import numpy as np
import time
import timeit
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional
from bots.iterold import IteroldAgent
from bots.itterino import ItterinoAgent
from bots.jardy import GardenerAgent
from bots.monkey import MonkeyAgent
from bots.ordy import TidyPodatorAgent
from bots.straightArrow import StraightArrowAgent
from bots.twinny import TwinPrunerAgent
from bots.taylor import TaylorAgent
from bots.randy import RandomAgent
from foofinder import FooFinderAgent

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






