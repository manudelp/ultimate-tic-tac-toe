from bots.randy import RandomAgent
from bots.greedy import GreedyAgent
from bots.jardito import JardineritoAgent
from bots.jardishow import JardiShowAgent

_AGENT_CLASSES = [RandomAgent, GreedyAgent, JardineritoAgent, JardiShowAgent]
AGENTS = {}

for cls in _AGENT_CLASSES:
    agent = cls()
    try:
        agent.load()
    except Exception as e:
        print(f"Failed to load {agent.name}: {e}")
    AGENTS[agent.id] = agent
