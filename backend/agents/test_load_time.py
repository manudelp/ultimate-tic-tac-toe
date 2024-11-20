from bot.randy import RandomAgent
from bot.monkey import MonkeyAgent
from bot.jardy import GardenerAgent
from bot.taylor import TaylorAgent
from bot.jardito import JardineritoAgent
from bot.straightArrow import StraightArrowAgent
from bot.iterold import IteroldAgent
from bot.itterino import ItterinoAgent
from bot.ordy import TidyPodatorAgent
from bot.twinny import TwinPrunerAgent
from bot.maxi import MaximilianoAgent
from bot.jarditonomid import JardineritoAntiMidAgent
from bot.jarditobetter import BetterJardineritoAgent
from foofinder import FooFinderAgent

import time

t_before_initializing_agents = time.time()
# IDs Dictionary, Agent:obj ; ID:int
AGENTS = {
    RandomAgent().id : RandomAgent(),
    MonkeyAgent().id : MonkeyAgent(), 
    GardenerAgent().id : GardenerAgent(), 
    TaylorAgent().id : TaylorAgent(), 
    JardineritoAgent().id : JardineritoAgent(), 
    StraightArrowAgent().id : StraightArrowAgent(), 
    IteroldAgent().id : IteroldAgent(), 
    ItterinoAgent().id : ItterinoAgent(), 
    TidyPodatorAgent().id : TidyPodatorAgent(),
    TwinPrunerAgent().id : TwinPrunerAgent(), 
    MaximilianoAgent().id : MaximilianoAgent(), 
    JardineritoAntiMidAgent().id : JardineritoAntiMidAgent(), 
    BetterJardineritoAgent().id : BetterJardineritoAgent(), 
    FooFinderAgent().id : FooFinderAgent()
}
t_after_initializing_agents = time.time()

# Print the time taken to initialize the agents
time_to_initialize_agents = t_after_initializing_agents - t_before_initializing_agents
print(f"\nTime taken to initialize the agents: {time_to_initialize_agents:.2f} seconds")