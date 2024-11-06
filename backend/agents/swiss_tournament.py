import numpy as np
import test_utils as utils
import random
from collections import defaultdict
import trueskill
import os
import sys
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
ROUNDS = 3  # Number of rounds to play
ROUNDS_PER_MATCH = 1  # Number of games to play between each pair of agents
REPEAT_SWISS = 16  # Number of times to repeat the Swiss tournament


# Initialize agents
AGENTS = [
    RandomAgent(),
    StraightArrowAgent(),
    JardineritoAgent(),
    MaximilianoAgent(),
    TaylorAgent(),
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

    def pair_and_play(self, rounds_per_match):
        # Sort agents by score in descending order
        sorted_agents = sorted(self.agents, key=lambda agent: self.scores[agent], reverse=True)
        results = []

        # Pair agents for this round, ensuring no rematches
        i = 0
        while i < len(sorted_agents) - 1:
            agent1 = sorted_agents[i]
            agent2 = sorted_agents[i + 1]
            if agent2 not in self.matches[agent1]:  # Avoid rematch
                # Record the match to avoid repeating it
                self.matches[agent1].append(agent2)
                self.matches[agent2].append(agent1)

                # Suppress agent prints while playing the game
                with redirect_stdout(suppress_agent_prints()):
                    # Play multiple games between the agents, alternating starter turns
                    agent1_wins, agent2_wins, draws = utils.play_multiple_games(agent1, agent2, rounds_per_match)

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
                i += 2
            else:
                # Move to the next agent if a rematch is found
                i += 1
        return results

    def run_swiss(self, rounds, rounds_per_match):
        """Runs a full Swiss-style tournament."""
        # Start printing the tournament rounds with Unicode support
        for round_num in range(1, rounds + 1):
            print(f"\n--- Round {round_num} ---")
            results = self.pair_and_play(rounds_per_match)

            # Update and display results for the round
            self.update_results_table()
            self.display_results_table()

    def update_results_table(self):
        """Updates the results table and accumulates ratings/scores."""
        # Correct access to TrueSkill ratings
        current_scores = {agent: self.ratings[agent].mu for agent in self.agents}  # Using .mu instead of indexing
        self.history[len(self.history) + 1] = sorted(current_scores.items(), key=lambda x: x[1], reverse=True)

    def display_results_table(self):
        """Display the final results after all repeats."""
        # Correct access to TrueSkill ratings
        final_scores = {agent: self.ratings[agent].mu for agent in self.agents}  # Using .mu instead of indexing
        final_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        print("\n--- FINAL RESULTS ---")
        for rank, (agent, score) in enumerate(final_results, start=1):
            print(f"{rank}. {str(agent)} - Rating: {score:.2f}")

    def display_final_results(self):
        """Display the final results after all repeats."""
        final_scores = {agent: self.ratings[agent].mu for agent in self.agents}
        final_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        print("\n--- FINAL RESULTS ---")
        for rank, (agent, score) in enumerate(final_results, start=1):
            print(f"{rank}. {str(agent)} - Rating: {score:.2f}")

    def repeat_swiss(self, repeats, rounds, rounds_per_match):
        """Runs the Swiss tournament multiple times and averages the final scores."""
        # Reset scores and matches
        self.history = defaultdict(list)

        for repeat_num in range(1, repeats + 1):
            print(f"\n=== Repeat Swiss Tournament {repeat_num} ===")
            
            # Reset ratings and scores for each repeat
            self.scores = {agent: 0 for agent in self.agents}
            self.matches = defaultdict(list)

            # Run a single Swiss tournament
            self.run_swiss(rounds, rounds_per_match)

            # Display results after each repeat
            self.display_results_table()

        # Display the final rankings after all repeats
        self.display_final_results()


# Call the Swiss Tournament
tournament = SwissTournament(AGENTS)

tournament.repeat_swiss(
    repeats=REPEAT_SWISS, 
    rounds=ROUNDS, 
    rounds_per_match=ROUNDS_PER_MATCH)
