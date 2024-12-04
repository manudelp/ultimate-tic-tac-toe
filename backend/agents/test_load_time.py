from bots.randy import RandomAgent
from bots.monkey import MonkeyAgent
from bots.jardy import GardenerAgent
from bots.taylor import TaylorAgent
from bots.jardito import JardineritoAgent
from bots.straightArrow import StraightArrowAgent
from bots.iterold import IteroldAgent
from bots.itterino import ItterinoAgent
from bots.ordy import TidyPodatorAgent
from bots.twinny import TwinPrunerAgent
from bots.maxi import MaximilianoAgent
from bots.jarditonomid import JardineritoAntiMidAgent
from bots.jarditobetter import BetterJardineritoAgent
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