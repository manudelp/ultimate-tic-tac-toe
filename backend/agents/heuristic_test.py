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
