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






