# import numpy as np
# import test_utils as utils
# import random
# from collections import defaultdict
# import trueskill
# import os
# import sys
# import time
# from colorama import Style, Fore

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

# # Agents Initializations
# RandomAgent = RandomAgent()
# MonkeyAgent = MonkeyAgent()
# GardenerAgent = GardenerAgent()
# JardineritoAgent = JardineritoAgent()
# MaximilianoAgent = MaximilianoAgent()
# TaylorAgent = TaylorAgent()
# GreedyAgent = GreedyAgent()
# IteroldAgent = IteroldAgent()
# ItterinoAgent = ItterinoAgent()
# TidyPodatorAgent = TidyPodatorAgent()
# TwinPrunerAgent = TwinPrunerAgent()
# FooFinderAgent = FooFinderAgent()
# GardenTranspositorAgent = GardenTranspositorAgent()
# IterVanBytesAgent = IterVanBytesAgent()
# JardineritoAntiMidAgent = JardineritoAntiMidAgent()
# BetterJardineritoAgent = BetterJardineritoAgent()
# BetterItterinoAgent = BetterItterinoAgent()

# # Define Local Boards
# local_Empty = np.array([[0, 0, 0],
#                         [0, 0, 0],
#                         [0, 0, 0]])  # Random board, no meaningful characteristics

# local_Rnd_1 = np.array([[1, 0, 0],
#                         [0, 0, 0],
#                         [0, 0, 0]])  # Random board, no meaningful characteristics

# local_Rnd_2 = np.array([[1, 0, 0],
#                         [0, 0, 0],
#                         [-1, 0, 0]])  # Random board

# local_Rnd_3 = np.array([[1, 0, -1],
#                         [0, 0, 0],
#                         [-1, 0, 1]])  # Random board

# local_Rnd_4 = np.array([[0, 1, 0],
#                         [1, -1, 1],
#                         [0, 1, 0]])  # Random board

# local_Rnd_5 = np.array([[1, -1, 1],
#                         [0, 0, 1],
#                         [1, 1, -1]])  # Random board

# local_Rnd_6 = np.array([[1, 0, 0],
#                         [0, 0, -1],
#                         [-1, -1, 0]])  # Random board

# local_topOne_1 = np.array([[0, 0, 0],
#                         [0, 1, 1],
#                         [0, 1, 1]])  # Random board

# local_topTwo_1 = np.array([[0, 0, 0],
#                         [0, -1, -1],
#                         [0, -1, -1]])  # Random board

# local_topOne_2 = np.array([[0, 1, 1],
#                         [1, 0, 1],
#                         [1, 1, 0]])  # Random board

# local_topTwo_2 = np.array([[0, -1, -1],
#                         [-1, 0, -1],
#                         [-1, -1, 0]])  # Random board

# local_OneWon_1 = np.array([[1, 1, 1],
#                     [0, -1, -1],
#                     [0, 0, -1]])  # Player 1 wins on the top row

# local_OneWon_2 = np.array([[0, -1, 1],
#                     [0, 1, -1],
#                     [1, 0, -1]])  # Player 1 wins on the diagonal

# local_OneWon_3 = np.array([[-1, -1, 0],
#                     [1, 1, 1],
#                     [0, -1, 0]])  # Player 1 wins on the middle row

# local_TwoWon_1 = np.array([[0, -1, 1],
#                     [-1, -1, 1],
#                     [1, -1, 0]])  # Player -1 wins on the middle column

# local_TwoWon_2 = np.array([[-1, 1, 0],
#                     [1, -1, 0],
#                     [1, 0, -1]])  # Player -1 wins on the diagonal

# local_TwoWon_3 = np.array([[-1, -1, -1],
#                     [1, 1, 0],
#                     [0, 1, 0]])  # Player -1 wins on the top row

# local_BothWnbl_1 = np.array([[1, -1, -1],
#                     [1, -1, -1],
#                     [0, 1, 1]])  # No winner yet

# local_BothWnbl_2 = np.array([[1, 1, 0],
#                     [-1, -1, 0],
#                     [0, 0, 0]])  # Not a win yet, but close

# local_BothWnbl_3 = np.array([[0, 0, 0],
#                             [1, 1, 0],
#                             [-1, -1, 0]])  # Another close board without a winner

# local_BothWnbl_4 = np.array([[-1, -1, 0],
#                             [-1, 0, 1],
#                             [0, 1, 1]]) # winnable by 1 in (0, 2), (2, 0) || winnable by -1 in (0, 2), (2, 0)

# local_Draw_1 = np.array([[1, -1, 1],
#                             [1, -1, -1],
#                             [-1, 1, 1]])  # Draw (no more moves possible)

# local_toDraw_1 = np.array([[1, -1, 1],
#                             [-1, -1, 1],
#                             [0, 1, -1]])  # Secured Draw (will always be Draw)

# local_toDraw_2 = np.array([[-1, 0, 1],
#                             [1, -1, -1],
#                             [-1, 1, 1]]) # Secured Draw (will always be Draw)

# local_OneWnbl_1 = np.array([[1, 0, 1],
#                             [1, 0, 0],
#                             [0, 1, 1]]) # winnable by 1 in (0, 1), (1, 1), (1, 2), (2, 0)

# local_TwoWnbl_1 = np.array([[0, 0, 0],
#                             [-1, -1, 0],
#                             [-1, -1, 0]]) # winnable by -1 in (0, 0), (0, 1), (0, 2), (1, 2), (2, 2)

# local_great_pOne = np.array([[1, 0, 1],
#                             [0, 1, 0],
#                             [0, 0, 0]])

# local_good_pOne = np.array([[1, 0, 1],
#                             [0, 1, 0],
#                             [0, 0, 0]])

# local_mid_pOne = np.array([[1, 0, 0],
#                             [0, 0, 1],
#                             [0, 1, 0]])

# local_toBeDrawn = np.array([[1, -1, 1],
#                             [-1, -1, 1],
#                             [0, 1, -1]])  # Secured Draw (will always be Draw)

# # Define Global Boards
# global_to_draw = np.zeros((3, 3, 3, 3), dtype=int)
# global_to_draw[0, 0] = local_OneWon_1
# global_to_draw[0, 1] = local_TwoWon_1
# global_to_draw[0, 2] = local_OneWon_2
# global_to_draw[1, 0] = local_TwoWon_2
# global_to_draw[1, 1] = local_TwoWon_2
# global_to_draw[1, 2] = local_OneWon_3
# global_to_draw[2, 1] = local_OneWon_3
# global_to_draw[2, 2] = local_TwoWon_3

# global_full_draw = np.zeros((3, 3, 3, 3), dtype=int)
# global_full_draw[0, 0] = local_OneWon_2
# global_full_draw[0, 1] = local_TwoWon_1
# global_full_draw[0, 2] = local_OneWon_3
# global_full_draw[1, 0] = local_TwoWon_2
# global_full_draw[1, 1] = local_TwoWon_3
# global_full_draw[1, 2] = local_OneWon_1
# global_full_draw[2, 0] = local_OneWon_3
# global_full_draw[2, 1] = local_OneWon_1
# global_full_draw[2, 2] = local_TwoWon_2

# global_mid = np.zeros((3, 3, 3, 3), dtype=int)
# global_mid[1, 1] = local_TwoWon_1
# global_mid[0, 0] = local_OneWon_2
# global_mid[2, 2] = local_OneWon_3

# global_alr = np.zeros((3, 3, 3, 3), dtype=int)
# global_alr[0, 0] = local_OneWon_1
# global_alr[2, 1] = local_OneWon_2
# global_alr[1, 2] = local_OneWon_3

# global_good = np.zeros((3, 3, 3, 3), dtype=int)
# global_good[1, 0] = local_OneWon_1
# global_good[2, 0] = local_OneWon_2
# global_good[2, 1] = local_OneWon_3

# global_great = np.zeros((3, 3, 3, 3), dtype=int)
# global_great[0, 0] = local_OneWon_1
# global_great[1, 1] = local_OneWon_2
# global_great[0, 2] = local_OneWon_3

# global_victory = np.zeros((3, 3, 3, 3), dtype=int)
# global_victory[0, 0] = local_OneWon_1
# global_victory[1, 1] = local_OneWon_2
# global_victory[2, 2] = local_OneWon_3

# # Original Evals
# og_eval_to_be_drawn = JardineritoAgent.boardBalance(global_to_draw)
# og_eval_full_draw = JardineritoAgent.boardBalance(global_full_draw)
# og_eval_mid = JardineritoAgent.boardBalance(global_mid)
# og_eval_alr = JardineritoAgent.boardBalance(global_alr)
# og_eval_good = JardineritoAgent.boardBalance(global_good)
# og_eval_great = JardineritoAgent.boardBalance(global_great)
# og_eval_victory = JardineritoAgent.boardBalance(global_victory)

# # Better Evals
# better_eval_to_be_drawn = BetterJardineritoAgent.boardBalance(global_to_draw)
# better_eval_full_draw = BetterJardineritoAgent.boardBalance(global_full_draw)
# better_eval_mid = BetterJardineritoAgent.boardBalance(global_mid)
# better_eval_alr = BetterJardineritoAgent.boardBalance(global_alr)
# better_eval_good = BetterJardineritoAgent.boardBalance(global_good)
# better_eval_great = BetterJardineritoAgent.boardBalance(global_great)
# better_eval_victory = BetterJardineritoAgent.boardBalance(global_victory)

# # Common Sense Checks
# tbd_check = "✅" if og_eval_to_be_drawn == better_eval_to_be_drawn else "❌"
# fd_check = "✅" if og_eval_full_draw == better_eval_full_draw else "❌"
# mid_check = "✅" if og_eval_mid < better_eval_mid else "❌"
# alr_check = "✅" if (1.1 * og_eval_alr) < better_eval_alr else "❌"
# good_check = "✅" if (1.2 * og_eval_good) < better_eval_good else "❌"
# great_check = "✅" if (1.3 * og_eval_great) < better_eval_great else "❌"
# victory_check = "✅" if (2 * og_eval_victory) < better_eval_victory else "❌"

# # Print
# print(Style.BRIGHT + f"---+--- Board Evaluation Results ---+---")
# print(Fore.GREEN if tbd_check == "✅" else Fore.RED)
# print(f"{tbd_check}  ToBe-Drawn Board Evals: Original: {og_eval_to_be_drawn} | Better: {better_eval_to_be_drawn}")
# print(Fore.GREEN if fd_check == "✅" else Fore.RED)
# print(f"{fd_check}  Full Draw Board Evals: Original: {og_eval_full_draw} | Better: {better_eval_full_draw}")
# print(Fore.GREEN if mid_check == "✅" else Fore.RED)
# print(f"{mid_check}  Mid Board Evals: Original: {og_eval_mid} | Better: {better_eval_mid}")
# print(Fore.GREEN if alr_check == "✅" else Fore.RED)
# print(f"{alr_check}  Alright Board Evals: Original: {og_eval_alr} | Better: {better_eval_alr}")
# print(Fore.GREEN if good_check == "✅" else Fore.RED)
# print(f"{good_check}  Good Board Evals: Original: {og_eval_good} | Better: {better_eval_good}")
# print(Fore.GREEN if great_check == "✅" else Fore.RED)
# print(f"{great_check}  Great Board Evals: Original: {og_eval_great} | Better: {better_eval_great}")
# print(Fore.GREEN if victory_check == "✅" else Fore.RED)
# print(f"{victory_check}  Victory Board Evals: Original: {og_eval_victory} | Better: {better_eval_victory}")
# print(Style.RESET_ALL)
