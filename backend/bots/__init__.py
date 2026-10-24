from bots.randy import RandomAgent
from bots.greedy import GreedyAgent
from bots.jardishow import JardiShowAgent
from bots.nmcts2 import Nmcts2Agent

# Jardinerito (bots.jardito) is off: Jardinero covers the same search, deeper.
# The arena can still seat it by name.
_AGENT_CLASSES = [RandomAgent, GreedyAgent, JardiShowAgent, Nmcts2Agent]
AGENTS = {}

for cls in _AGENT_CLASSES:
    agent = cls()
    try:
        agent.load()
    except Exception as e:
        print(f"Failed to load {agent.name}: {e}")
    AGENTS[agent.id] = agent
