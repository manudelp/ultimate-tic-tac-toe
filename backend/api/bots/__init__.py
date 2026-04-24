from flask import Blueprint
from agents.bots.randy import RandomAgent
from agents.bots.jardito import JardineritoAgent
from agents.bots.greedy import GreedyAgent
from agents.bots.jardishow import JardiShowAgent
# from agents.bots.arthy import ArthyAgent
# from agents.bots.monkey import MonkeyAgent
# from agents.bots.santa import SantaAgent
# from agents.foofinder import FooFinderAgent

# Create the bots blueprint
bot_routes = Blueprint('bots', __name__)

# IDs Dictionary, Agent:obj ; ID:int
AGENTS = {
    RandomAgent().id : RandomAgent(),
    GreedyAgent().id : GreedyAgent(), 
    JardineritoAgent().id : JardineritoAgent(),
    JardiShowAgent().id : JardiShowAgent(),
}

# Pre-load all agents
for agent in AGENTS.values():
    try:
        agent.load()
    except Exception as e:
        print(f"Failed to load {agent.name}: {e}")

# Import routes at the end to avoid circular imports
from . import routes