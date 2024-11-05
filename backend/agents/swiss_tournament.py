import numpy as np
import test_utils as utils
from agents.bot.randy import RandomAgent
from agents.bot.monkey import MonkeyAgent
from agents.bot.jardy import GardenerAgent
from agents.bot.taylor import TaylorAgent
from agents.bot.straightArrow import StraightArrowAgent
from agents.bot.iterold import IteroldAgent
from agents.bot.itterino import ItterinoAgent
from agents.bot.ordy import TidyPodatorAgent
from agents.bot.twinny import TwinPrunerAgent
from agents.foofinder import FooFinderAgent

# Initialize agents
AGENTS = [
    RandomAgent(),
    GardenerAgent(),
    MonkeyAgent(),
    TaylorAgent(),
    StraightArrowAgent(),
    IteroldAgent(),
    ItterinoAgent(),
    TidyPodatorAgent(),
    TwinPrunerAgent()
]



