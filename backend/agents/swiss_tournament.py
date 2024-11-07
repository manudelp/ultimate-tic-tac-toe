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
from bot.gardentranspositor import TransJardiAgent
from bot.itervanbytes import IterVanBytesAgent

# Hyperparameters
ROUNDS = 2  # Number of rounds to play
ROUNDS_PER_MATCH = 1  # Number of games to play between each pair of agents
REPEAT_SWISS = 16  # Number of times to repeat the Swiss tournament


# Initialize agents
AGENTS = [
    RandomAgent(),
    # StraightArrowAgent(),
    # TaylorAgent(),
    JardineritoAgent(),
    MaximilianoAgent(),
    # GardenerAgent(),
    # MonkeyAgent(),
    # IteroldAgent(),
    # ItterinoAgent(),
    # TidyPodatorAgent(),
    # TwinPrunerAgent(),
    # TransJardiAgent(),
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
        self.history = defaultdict(list)  # To accumulate history of results

class SwissTournament:
    def __init__(self, agents):
        self.agents = agents
        self.scores = {agent: 0 for agent in agents}  # Initialize scores to zero
        self.matches = defaultdict(list)  # Track who has played against whom
        self.trueskill_env = trueskill.TrueSkill()  # Initialize TrueSkill environment
        self.ratings = {agent: self.trueskill_env.create_rating() for agent in agents}  # Initialize TrueSkill ratings
        self.history = defaultdict(list)  # To accumulate history of results

    def display_round_progress_bar(self, current_match, total_matches, avg_game_time_ms):
        bar_length = 30  # Length of the progress bar
        progress = current_match / total_matches
        filled_length = int(bar_length * progress)
        
        # Green bar using ANSI escape codes
        bar = f'\033[92m{"█" * filled_length}\033[0m' + '-' * (bar_length - filled_length)
        
        # Display progress bar with games left and average game time
        sys.stdout.write(
            f'\r|{bar}| {current_match}/{total_matches} games | Average Game Time: {avg_game_time_ms:.2f} ms'
        )
        sys.stdout.flush()

    def pair_and_play(self, rounds_per_match):
        # Sort agents by score in descending order
        sorted_agents = sorted(self.agents, key=lambda agent: self.scores[agent], reverse=True)
        results = []
        total_matches = len(sorted_agents) // 2
        current_match = 0
        total_time_ms = 0

        # Initial display of progress bar at 0/R
        self.display_round_progress_bar(current_match, total_matches, avg_game_time_ms=0)

        # Pair agents for this round, ensuring no rematches
        i = 0
        while i < len(sorted_agents) - 1:
            agent1 = sorted_agents[i]
            agent2 = sorted_agents[i + 1]
            if agent2 not in self.matches[agent1]:  # Avoid rematch
                # Record the match to avoid repeating it
                self.matches[agent1].append(agent2)
                self.matches[agent2].append(agent1)

                # Measure time for the current subgame
                start_time = time.time()
                
                # Suppress agent prints while playing the game
                with redirect_stdout(suppress_agent_prints()):
                    # Play multiple games between the agents, alternating starter turns
                    agent1_wins, agent2_wins, draws = utils.play_multiple_games(agent1, agent2, rounds_per_match)
                
                # Calculate elapsed time in milliseconds and update total time
                elapsed_time_ms = (time.time() - start_time) * 1000
                total_time_ms += elapsed_time_ms
                avg_game_time_ms = total_time_ms / (current_match + 1)

                # Update scores based on results
                self.scores[agent1] += agent1_wins + (0.5 * draws)
                self.scores[agent2] += agent2_wins + (0.5 * draws)

                # Update TrueSkill ratings based on results
                if agent1_wins > agent2_wins:
                    self.ratings[agent1], self.ratings[agent2] = self.trueskill_env.rate_1vs1(self.ratings[agent1], self.ratings[agent2])
                elif agent2_wins > agent1_wins:
                    self.ratings[agent2], self.ratings[agent1] = self.trueskill_env.rate_1vs1(self.ratings[agent2], self.ratings[agent1])

                # Record the result for display purposes
                results.append((agent1, agent2, agent1_wins, agent2_wins, draws))
                
                # Update and display the progress bar with average game time for the current round
                current_match += 1
                self.display_round_progress_bar(current_match, total_matches, avg_game_time_ms)

                i += 2
            else:
                # Move to the next agent if a rematch is found
                i += 1
        print()  # Move to the next line after the progress bar completes
        return results

    def run_swiss(self, rounds, rounds_per_match):
        """Runs a full Swiss-style tournament."""
        for round_num in range(1, rounds + 1):
            print(f"\n--- Round {round_num} ---")
            results = self.pair_and_play(rounds_per_match)

            # Update results table after each round
            self.update_results_table()

    def update_results_table(self):
        """Updates the results table and accumulates ratings/scores."""
        # Accumulate `mu` and `sigma` values in the standings
        current_scores = {agent: (self.ratings[agent].mu, self.ratings[agent].sigma) for agent in self.agents}
        self.history[len(self.history) + 1] = sorted(current_scores.items(), key=lambda x: x[1][0], reverse=True)

    def repeat_swiss(self, repeats, rounds, rounds_per_match):
        """Runs the Swiss tournament multiple times and averages the final scores."""
        accumulated_scores = {agent: (0, 0) for agent in self.agents}

        for repeat_num in range(1, repeats + 1):
            # Reset scores and matches for each repeat
            self.scores = {agent: 0 for agent in self.agents}
            self.matches = defaultdict(list)

            # Run a single Swiss tournament
            self.run_swiss(rounds, rounds_per_match)

            # Accumulate mu and sigma values from this repeat
            for agent in self.agents:
                mu, sigma = self.ratings[agent].mu, self.ratings[agent].sigma
                accumulated_mu, accumulated_sigma = accumulated_scores[agent]
                accumulated_scores[agent] = (accumulated_mu + mu, accumulated_sigma + sigma)

            # Display results after each Repeat Swiss
            averaged_scores = {agent: (accumulated_scores[agent][0] / repeat_num, accumulated_scores[agent][1] / repeat_num) for agent in self.agents}
            self.display_averaged_results(averaged_scores, repeat_num)

        # Display final averaged results after all repeats
        print("\n=== FINAL RESULTS ===")
        self.display_averaged_results(averaged_scores)

    def display_averaged_results(self, averaged_scores, repeat_num=None):
        """Displays final standings with averaged scores (mu ± sigma) after each repeat or all repeats."""
        final_standings = sorted(averaged_scores.items(), key=lambda x: x[1][0], reverse=True)

        # Header for the table with optional Repeat Swiss number
        if repeat_num:
            print(f"\n--- Results after Repeat Swiss {repeat_num} ---")
        else:
            print("\n--- Final Averaged Standings ---")

        # Table border and header
        print("+------+----------------+------------------+")
        print("| Rank |     Agent      |     Score       |")
        print("+------+----------------+------------------+")

        # Display each agent with mean and deviation (mu ± sigma)
        for rank, (agent, (mu, sigma)) in enumerate(final_standings, start=1):
            print(f"| {rank:<4} | {str(agent):<23} | {mu:.2f} ± {sigma:.2f} |")

        # Close the table
        print("+------+----------------+------------------+")

# Call the Swiss Tournament
tournament = SwissTournament(AGENTS)

t0 = time.time()

tournament.repeat_swiss(
    repeats=REPEAT_SWISS, 
    rounds=ROUNDS, 
    rounds_per_match=ROUNDS_PER_MATCH)

print(f"\nTotal Time Taken: {(time.time() - t0):.2f} seconds")
