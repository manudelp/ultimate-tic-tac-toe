import numpy as np
import test_utils as utils
import random
from collections import defaultdict
import trueskill
import os
import sys
import time
from contextlib import redirect_stdout

from bot.randy import RandomAgent
from bot.monkey import MonkeyAgent
from bot.jardy import GardenerAgent
from bot.jardito import JardineritoAgent
from bot.maxi import MaximilianoAgent
from bot.taylor import TaylorAgent
from bot.straightArrow import StraightArrowAgent
from bot.iterold import IteroldAgent
from bot.itterino import ItterinoAgent
from bot.ordy import TidyPodatorAgent
from bot.twinny import TwinPrunerAgent
from foofinder import FooFinderAgent
from bot.gardentranspositor import GardenTranspositorAgent
from bot.itervanbytes import IterVanBytesAgent

# Hyperparameters
ROUNDS = 3  # Number of rounds to play
ROUNDS_PER_MATCH = 1  # Number of games to play between each pair of agents
REPEAT_SWISS = 16  # Number of times to repeat the Swiss tournament


# Initialize agents
AGENTS = [
    RandomAgent(),
    StraightArrowAgent(),
    TaylorAgent(),
    JardineritoAgent(),
    MaximilianoAgent(),
    # GardenerAgent(),
    # MonkeyAgent(),
    # IteroldAgent(),
    # ItterinoAgent(),
    # TidyPodatorAgent(),
    # TwinPrunerAgent(),
    # GardenTranspositorAgent(),
    # IterVanBytesAgent(),
    # FooFinderAgent()
]

def suppress_agent_prints():
    """Suppress prints from agents only, while allowing others."""
    return open(os.devnull, 'w', encoding='utf-8')


class SwissTournament:
    def __init__(self, agents):
        self.agents = agents
        self.scores = {agent: 0 for agent in agents}  # Initialize scores to zero
        self.matches = defaultdict(list)  # Track who has played against whom
        self.trueskill_env = trueskill.TrueSkill()  # Initialize TrueSkill environment
        self.ratings = {agent: self.trueskill_env.create_rating() for agent in agents}  # Initialize TrueSkill ratings
        self.cumulative_times = {agent: 0.0 for agent in agents}  # Track cumulative time for each agent
        self.play_counts = {agent: 0 for agent in agents}  # Track the number of games played per agent
        self.history = defaultdict(list)  # To accumulate history of results for each round

    def display_round_progress_bar(self, current_match, total_matches, avg_game_time_secs):
        bar_length = 30  # Length of the progress bar
        progress = current_match / total_matches
        filled_length = int(bar_length * progress)
        
        # Green bar using ANSI escape codes
        bar = f'\033[92m{"█" * filled_length}\033[0m' + '-' * (bar_length - filled_length)
        
        # Display progress bar with games left and average game time
        sys.stdout.write(
            f'\r|{bar}| {current_match}/{total_matches} games | Average Game Time: {avg_game_time_secs:.2f} secs'
        )
        sys.stdout.flush()

    def pair_and_play(self, rounds_per_match):
        sorted_agents = sorted(self.agents, key=lambda agent: self.scores[agent], reverse=True)
        results = []
        total_matches = len(sorted_agents) // 2
        current_match = 0
        total_time_secs = 0

        self.display_round_progress_bar(current_match, total_matches, avg_game_time_secs=0)

        i = 0
        while i < len(sorted_agents) - 1:
            agent1 = sorted_agents[i]
            agent2 = sorted_agents[i + 1]
            if agent2 not in self.matches[agent1]:  # Avoid rematch
                self.matches[agent1].append(agent2)
                self.matches[agent2].append(agent1)

                # Measure time for each subgame
                start_time = time.time()
                
                with redirect_stdout(suppress_agent_prints()):
                    agent1_wins, agent2_wins, draws = utils.play_multiple_games(agent1, agent2, rounds_per_match)
                
                elapsed_time_secs = (time.time() - start_time)
                total_time_secs += elapsed_time_secs
                avg_game_time_secs = total_time_secs / (current_match + 1)

                # Track cumulative time and play count for each agent
                self.cumulative_times[agent1] += elapsed_time_secs / rounds_per_match
                self.cumulative_times[agent2] += elapsed_time_secs / rounds_per_match
                self.play_counts[agent1] += rounds_per_match
                self.play_counts[agent2] += rounds_per_match

                # Update scores and ratings
                self.scores[agent1] += agent1_wins + (0.5 * draws)
                self.scores[agent2] += agent2_wins + (0.5 * draws)

                if agent1_wins > agent2_wins:
                    self.ratings[agent1], self.ratings[agent2] = self.trueskill_env.rate_1vs1(self.ratings[agent1], self.ratings[agent2])
                elif agent2_wins > agent1_wins:
                    self.ratings[agent2], self.ratings[agent1] = self.trueskill_env.rate_1vs1(self.ratings[agent2], self.ratings[agent1])

                results.append((agent1, agent2, agent1_wins, agent2_wins, draws))
                
                current_match += 1
                self.display_round_progress_bar(current_match, total_matches, avg_game_time_secs)
                
                i += 2
            else:
                i += 1
        print()
        return results

    def run_swiss(self, rounds, rounds_per_match):
        for round_num in range(1, rounds + 1):
            results = self.pair_and_play(rounds_per_match)
            self.update_results_table()

    def display_averaged_results(self, accumulated_scores, repeat_num=None):
        # Final standings with average score and sigma deviation for each agent
        final_standings = sorted(
            [(agent, self.ratings[agent].mu, self.ratings[agent].sigma, self.cumulative_times[agent] / max(1, self.play_counts[agent])) 
             for agent in self.agents], 
            key=lambda x: x[1], reverse=True
        )

        # Header for the table with optional Repeat Swiss number
        if repeat_num:
            print(f"\n--- Results after Repeat Swiss {repeat_num} ---")
        else:
            print("\n--- Final Averaged Standings ---")

        # Table header with the new columns for sigma and Avg Time
        print("+------+------------------------------+----------------+-------------------+")
        print("| Rank |             Agent            |   Score (±σ)   | Avg Game Time (s) |")
        print("+------+------------------------------+----------------+-------------------+")

        for rank, (agent, mu, sigma, avg_time_secs) in enumerate(final_standings, start=1):
            score_display = f"{mu:.2f} ± {sigma:.2f}"
            print(f"| {rank:<4} | {str(agent):<27} | {score_display:<13} | {avg_time_secs:<13.2f} |")

        print("+------+----------------+------------------+------------+")

    def repeat_swiss(self, repeats, rounds, rounds_per_match):
        accumulated_scores = {agent: 0 for agent in self.agents}

        for repeat_num in range(1, repeats + 1):
            self.scores = {agent: 0 for agent in self.agents}
            self.matches = defaultdict(list)
            self.cumulative_times = {agent: 0.0 for agent in self.agents}
            self.play_counts = {agent: 0 for agent in self.agents}

            self.run_swiss(rounds, rounds_per_match)

            # Calculate the accumulated TrueSkill `mu` scores over all repeats
            for agent in self.agents:
                accumulated_scores[agent] += self.ratings[agent].mu

            self.display_averaged_results(accumulated_scores, repeat_num)

        print("\n=== FINAL RESULTS ===")
        self.display_averaged_results(accumulated_scores)

    def update_results_table(self):
        """Updates the results table and accumulates ratings/scores."""
        # Retrieve current mu and sigma for each agent
        current_scores = {agent: (self.ratings[agent].mu, self.ratings[agent].sigma) for agent in self.agents}
        
        # Sort by score (mu) in descending order
        sorted_scores = sorted(current_scores.items(), key=lambda x: x[1][0], reverse=True)
        
        # Store in history with round number as the key
        self.history[len(self.history) + 1] = sorted_scores

# Call the Swiss Tournament
tournament = SwissTournament(AGENTS)

t0 = time.time()

tournament.repeat_swiss(
    repeats=REPEAT_SWISS, 
    rounds=ROUNDS, 
    rounds_per_match=ROUNDS_PER_MATCH)

print(f"\nTotal Time Taken: {(time.time() - t0):.2f} seconds")
