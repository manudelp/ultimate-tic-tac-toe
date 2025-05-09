# # Main Bots
# from bots.randy import RandomAgent
# from bots.monkey import MonkeyAgent
# from bots.greedy import GreedyAgent
# from bots.jardito import JardineritoAgent
# from bots.arthy import ArthyAgent
# from bots.foofinder import FooFinderAgent

# # Other Dev Bots
# from others.jardy import GardenerAgent
# from others.itterinobetter import BetterItterinoAgent
# from others.taylor import TaylorAgent
# from others.iterold import IteroldAgent
# from others.itterino import ItterinoAgent
# from others.ordy import TidyPodatorAgent
# from others.twinny import TwinPrunerAgent
# from others.maxi import MaximilianoAgent
# from others.gardentranspositor import GardenTranspositorAgent
# from others.itervanbytes import IterVanBytesAgent
# from others.jarditonomid import JardineritoAntiMidAgent
# from others.jarditobetter import BetterJardineritoAgent
# from others.alterjardito import AlterJardineritoAgent

# import time

# t_before_initializing_agents = time.time()
# # IDs Dictionary, Agent:obj ; ID:int
# AGENTS = {
#     RandomAgent().id : RandomAgent(),
#     MonkeyAgent().id : MonkeyAgent(), 
#     GardenerAgent().id : GardenerAgent(), 
#     TaylorAgent().id : TaylorAgent(), 
#     JardineritoAgent().id : JardineritoAgent(), 
#     GreedyAgent().id : GreedyAgent(), 
#     IteroldAgent().id : IteroldAgent(), 
#     ItterinoAgent().id : ItterinoAgent(), 
#     TidyPodatorAgent().id : TidyPodatorAgent(),
#     TwinPrunerAgent().id : TwinPrunerAgent(), 
#     MaximilianoAgent().id : MaximilianoAgent(), 
#     JardineritoAntiMidAgent().id : JardineritoAntiMidAgent(), 
#     BetterJardineritoAgent().id : BetterJardineritoAgent(), 
#     FooFinderAgent().id : FooFinderAgent()
# }
# t_after_initializing_agents = time.time()

# # Print the time taken to initialize the agents
# time_to_initialize_agents = t_after_initializing_agents - t_before_initializing_agents
# print(f"\nTime taken to initialize the agents: {time_to_initialize_agents:.2f} seconds")