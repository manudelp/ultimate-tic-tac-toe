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
    # TaylorAgent().id : TaylorAgent(), 
    GreedyAgent().id : GreedyAgent(), 
    JardineritoAgent().id : JardineritoAgent(),
    JardiShowAgent().id : JardiShowAgent(),
    # ArthyAgent().id : ArthyAgent(),
    # MonkeyAgent().id : MonkeyAgent(),
    # FooFinderAgent().id : FooFinderAgent(),
    # SantaAgent().id : SantaAgent()
}

# Import routes at the end to avoid circular imports
from . import routes