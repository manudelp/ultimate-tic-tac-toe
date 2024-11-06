import numpy as np
import test_utils as utils
import time
from bot.randy import RandomAgent
from bot.monkey import MonkeyAgent
from bot.jardy import GardenerAgent
from bot.jardito import JardineritoAgent
from bot.taylor import TaylorAgent
from bot.straightArrow import StraightArrowAgent
from bot.iterold import IteroldAgent
from bot.itterino import ItterinoAgent
from bot.ordy import TidyPodatorAgent
from bot.twinny import TwinPrunerAgent
from bot.maxi import MaximilianoAgent
from foofinder import FooFinderAgent

t0 = time.time()

# Initialize agents
AGENT1 = JardineritoAgent()    # Replace with your chosen agent
AGENT2 = TaylorAgent()  # Replace with your chosen agent
ROUNDS = 1  # Number of rounds to play, each round represents 2 games (with alternating pieces)
GAMES = ROUNDS * 2

agent1_name = str(AGENT1)
agent2_name = str(AGENT2)

# Run the simulation
agent1_wins, agent2_wins, draws = utils.play_multiple_games(AGENT1, AGENT2, ROUNDS)

ag1_percentage = agent1_wins / GAMES * 100
ag2_percentage = agent2_wins / GAMES * 100
draw_percentage = draws / GAMES * 100

# TODO: Make it print an actual nice-looking table!
# get design inspiration from the actual website
# print the winner's results in green and loser's in red like in the actual website
print(f"{agent1_name} Wins: {agent1_wins}")
print(f"{agent2_name} Wins: {agent2_wins}")
print(f"Draws: {draws}")
# print who was the overall winner, big and bright font please

print(f"Time taken to play {GAMES} games: {(time.time() - t0):.2f} seconds")
