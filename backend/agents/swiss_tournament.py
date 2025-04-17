import numpy as np
import test_utils as utils
import random
from collections import defaultdict
import trueskill
import os
import sys
import time
from contextlib import redirect_stdout

# Main Bots
from bots.randy import RandomAgent
from bots.monkey import MonkeyAgent
from bots.greedy import GreedyAgent
from bots.jardito import JardineritoAgent
from bots.arthy import ArthyAgent
# from bots.foofinder import FooFinderAgent

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
from dev.heuristic.ht_bettereval import BetterEvalAgent
from dev.heuristic.ht_fullinfo import FullInfoAgent
from dev.heuristic.ht_original import OriginalAgent


# Hyperparameters
ROUNDS_PER_MATCH = 1  # Number of games to play between each pair of agents
REPEAT_SWISS = 16  # Number of times to repeat the Swiss tournament


# Initialize agents
AGENTS = [
    RandomAgent(),
    GreedyAgent(),
    TaylorAgent(),
    JardineritoAgent(),
    # MaximilianoAgent(),
    # JardineritoAntiMidAgent(),
    BetterJardineritoAgent(),
    GardenerAgent(),
    ArthyAgent(),
    # MonkeyAgent(),
    # IteroldAgent(),
    # ItterinoAgent(),
    # BetterItterinoAgent(),
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
        for agent_bot in agents:
            agent_bot.load()
        self.scores = {agent: 0 for agent in agents}  # Initialize scores to zero
        self.matches = defaultdict(list)  # Track who has played against whom
        self.trueskill_env = trueskill.TrueSkill()  # Initialize TrueSkill environment
        self.ratings = {agent: self.trueskill_env.create_rating() for agent in agents}  # Initialize TrueSkill ratings
        # self.cumulative_times = {agent: 0.0 for agent in agents}  # Track cumulative time for each agent
        # self.play_counts = {agent: 0 for agent in agents}  # Track the number of games played per agent
        self.history = defaultdict(list)  # To accumulate history of results for each round
        self.move_times = {agent: 0.0 for agent in agents}  # Cumulative move time for each agent
        self.matchup_counts = {agent: 0 for agent in agents}  # Count of moves for each agent

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
        i = 0
        
        self.display_round_progress_bar(current_match, total_matches, avg_game_time_secs=0)

        while i < len(sorted_agents) - 1:
            agent1 = sorted_agents[i]
            agent2 = sorted_agents[i + 1]
            if agent2 not in self.matches[agent1]:  # Avoid rematch
                self.matches[agent1].append(agent2)
                self.matches[agent2].append(agent1)
                
                start_time = time.time()

                # Suppress agent prints while playing the game
                with redirect_stdout(suppress_agent_prints()):
                    agent1_wins, agent2_wins, draws, agent1_avg_times_per_game, agent2_avg_times_per_game = utils.play_multiple_games(agent1, agent2, rounds_per_match)

                elapsed_time_secs = (time.time() - start_time)
                total_time_secs += elapsed_time_secs
                avg_game_time_secs = total_time_secs / (current_match + 1)

                # Update move time statistics, where move_times is the average move duration, and matchup_counts is the number of matchups played
                self.move_times[agent1] += agent1_avg_times_per_game
                self.matchup_counts[agent1] += 1
                self.move_times[agent2] += agent2_avg_times_per_game
                self.matchup_counts[agent2] += 1

                # Update scores
                self.scores[agent1] += agent1_wins + (0.5 * draws)
                self.scores[agent2] += agent2_wins + (0.5 * draws)

                # Update TrueSkill ratings based on results
                if agent1_wins > agent2_wins:
                    self.ratings[agent1], self.ratings[agent2] = self.trueskill_env.rate_1vs1(self.ratings[agent1], self.ratings[agent2])
                elif agent2_wins > agent1_wins:
                    self.ratings[agent2], self.ratings[agent1] = self.trueskill_env.rate_1vs1(self.ratings[agent2], self.ratings[agent1])

                current_match += 1
                self.display_round_progress_bar(current_match, total_matches, avg_game_time_secs)

                results.append((agent1, agent2, agent1_wins, agent2_wins, draws))
                i += 2
            else:
                i += 1
        print()
        return results

    def run_swiss(self, rounds, rounds_per_match):
        for round_num in range(1, rounds + 1):
            results = self.pair_and_play(rounds_per_match)
            self.update_results_table()

    def display_averaged_results(self, averaged_scores, repeat_num=None):
        final_standings = sorted(
            [(agent, (self.ratings[agent].mu, self.ratings[agent].sigma)) 
             for agent in self.agents], 
            key=lambda x: x[1], reverse=True
        )
        
        if repeat_num:
            print(f"\n--- Results after Repeat Swiss {repeat_num} ---")
        else:
            print("\n--- Final Averaged Standings ---")

        print("+------+------------------------------+----------------+---------------+")
        print("| Rank |             Agent            |   Score (±σ)   | Avg Time (ms) |")
        print("+------+------------------------------+----------------+---------------+")

        for rank, (agent, (score, deviation)) in enumerate(final_standings, start=1):
            avg_move_time = self.move_times[agent] / self.matchup_counts[agent] if self.matchup_counts[agent] > 0 else 0.0
            score_display = f"{score:.2f} ± {deviation:.2f}"
            print(f"| {rank:<4} | {str(agent):<27} | {score_display:<14} | {avg_move_time:<10.4f} ms |")

        print("+------+------------------------------+----------------+---------------+")

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

# Rounds is the log base 2 of the number of agents, rounded down, + 1
agents_number = len(AGENTS)
ROUNDS = int(np.log2(agents_number)) + 1

tournament.repeat_swiss(
    repeats=REPEAT_SWISS, 
    rounds=ROUNDS, 
    rounds_per_match=ROUNDS_PER_MATCH)

print(f"\nTotal Time Taken: {(time.time() - t0):.2f} seconds")
