import numpy as np
import test_utils as utils
import time
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

# Main Bots
from bots.randy import RandomAgent
from bots.monkey import MonkeyAgent
from bots.straightArrow import StraightArrowAgent
from bots.jardito import JardineritoAgent
from bots.arthy import ArthyAgent
from bots.foofinder import FooFinderAgent

# Other Dev Bots
from others.jardy import GardenerAgent
from others.itterinobetter import BetterItterinoAgent
from others.taylor import TaylorAgent
from others.iterold import IteroldAgent
from others.itterino import ItterinoAgent
from others.ordy import TidyPodatorAgent
from others.twinny import TwinPrunerAgent
from others.maxi import MaximilianoAgent
from others.gardentranspositor import GardenTranspositorAgent
from others.itervanbytes import IterVanBytesAgent
from others.jarditonomid import JardineritoAntiMidAgent
from others.jarditobetter import BetterJardineritoAgent
from others.alterjardito import AlterJardineritoAgent

# Heuristic Testing Bots



t0 = time.time()

# Initialize agents
AGENT1 = GardenerAgent()    # Replace with your chosen agent
AGENT2 = ArthyAgent()  # Replace with your chosen agent
ROUNDS = 1
GAMES = ROUNDS * 2
BLIZZARD_MODE = False

agent1_name = str(AGENT1)
agent2_name = str(AGENT2)

# Run the simulation
if BLIZZARD_MODE:
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + f"\n ----+---- 🌨️❄️ PLAYING {GAMES} GAMES IN BLIZZARD MODE ❄️🌨️ ----+----")
    agent1_wins, agent2_wins, draws, agent1_time, agent2_time = utils.play_multiple_games(AGENT1, AGENT2, ROUNDS, gamemode="blizzard")
else:
    agent1_wins, agent2_wins, draws, agent1_time, agent2_time = utils.play_multiple_games(AGENT1, AGENT2, ROUNDS)

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

print(Style.BRIGHT + f"\nFINAL WINNER IS {final_winner}")

print(Style.BRIGHT + Fore.LIGHTBLACK_EX)
print(f"\nAverage full game time taken for {agent1_name}: {agent1_time:.2f} of I have no idea what unit ngl")
print(f"Average full game time taken for {agent2_name}: {agent2_time:.2f} of I have no idea what unit ngl")
print(f"Time taken to play {GAMES} games: {(time.time() - t0):.2f} seconds" + Style.RESET_ALL)
