import numpy as np
import test_utils as utils
import time
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional
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
from bot.gardentranspositor import GardenTranspositorAgent
from bot.itervanbytes import IterVanBytesAgent
from foofinder import FooFinderAgent
from bot.jarditonomid import JardineritoAntiMidAgent
from bot.jarditobetter import BetterJardineritoAgent

t0 = time.time()

# Initialize agents
AGENT1 = JardineritoAgent()    # Replace with your chosen agent
AGENT2 = BetterJardineritoAgent()  # Replace with your chosen agent
ROUNDS = 2 # each round is 2 games
GAMES = ROUNDS * 2

agent1_name = str(AGENT1)
agent2_name = str(AGENT2)

# Run the simulation
agent1_wins, agent2_wins, draws, agent1_time, agent2_time = utils.play_multiple_games(AGENT1, AGENT2, ROUNDS)
agent1_time_secs = agent1_time / 1000
agent2_time_secs = agent2_time / 1000
if agent1_wins > agent2_wins:
    final_winner = agent1_name
elif agent1_wins < agent2_wins:
    final_winner = agent2_name
else:
    final_winner = "DRAW "

ag1_percentage = agent1_wins / GAMES * 100
ag2_percentage = agent2_wins / GAMES * 100
draw_percentage = draws / GAMES * 100

print(Style.BRIGHT + f"\n ----+---- FINAL RESULTS ----+----")

if final_winner == agent1_name:
    print(Fore.GREEN + Style.BRIGHT + f"{agent1_name} Won  {agent1_wins} games ({ag1_percentage:.2f}%)" + Style.RESET_ALL)
    print(Fore.RED + Style.BRIGHT + f"{agent2_name} Won  {agent2_wins} games ({ag2_percentage:.2f}%)" + Style.RESET_ALL)
elif final_winner == agent2_name:
    print(Fore.RED + Style.BRIGHT + f"{agent2_name} Won  {agent2_wins} games ({ag2_percentage:.2f}%)" + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + f"{agent1_name} Won  {agent1_wins} games ({ag1_percentage:.2f}%)" + Style.RESET_ALL)
else:
    print(Fore.YELLOW + Style.BRIGHT + f"{agent1_name} Won  {agent1_wins} games ({ag1_percentage:.2f}%)" + Style.RESET_ALL)
    print(Fore.YELLOW + Style.BRIGHT + f"{agent2_name} Won  {agent2_wins} games ({ag2_percentage:.2f}%)" + Style.RESET_ALL)
print(Style.BRIGHT + f"Drawn games: {draws}")

print(Style.BRIGHT + f"\n FINAL WINNER IS {final_winner}")

print(Style.BRIGHT + Fore.LIGHTBLACK_EX)
print(f"\nAverage full game time taken for {agent1_name}: {agent1_time_secs:.2f} seconds")
print(f"Average full game time taken for {agent2_name}: {agent2_time_secs:.2f} seconds")
print(f"Time taken to play {GAMES} games: {(time.time() - t0):.2f} seconds" + Style.RESET_ALL)
