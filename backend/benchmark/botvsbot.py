import numpy as np
import api.utils as utils
from agents.bot.randy import RandomAgent
from agents.bot.monkey import MonkeyAgent
from agents.bot.jardy import GardenerAgent
from agents.bot.taylor import TaylorAgent
from agents.bot.straightArrow import StraightArrowAgent
from agents.bot.iterold import IteroldAgent
from agents.bot.itterino import ItterinoAgent
from agents.bot.ordy import TidyPodatorAgent
from agents.bot.twinny import TwinPrunerAgent
from agents.foofinder import FooFinderAgent

# Initialize agents
AGENT1 = StraightArrowAgent()  # Replace with your chosen agent
AGENT2 = RandomAgent()         # Replace with your chosen agent

# Initialize game board
board = np.zeros((3, 3, 3, 3), dtype=int)  # 4D board, initialized to zeros

# Function to play a full game
def play_game(agent1, agent2):
    current_agent = agent1
    next_agent = agent2
    board_to_play = None  # Initially, agents can choose any board

    while True:
        # Current agent makes a move
        move = current_agent.action(board, board_to_play)
        x, y, i, j = move

        # Update board with the move
        board[x, y, i, j] = 1 if current_agent == agent1 else -1

        # Check if game is over
        if utils.is_game_over(board):
            winner = utils.get_winner(board)  # Assuming this returns 1 for agent1, -1 for agent2, or 0 for a draw
            if winner == 1:
                print("Agent 1 wins!")
            elif winner == -1:
                print("Agent 2 wins!")
            else:
                print("It's a draw!")
            break

        # Determine next board_to_play based on this move
        board_to_play = (i, j) if utils.is_board_open(board, i, j) else None

        # Swap agents for next turn
        current_agent, next_agent = next_agent, current_agent

# Run the game simulation
play_game(AGENT1, AGENT2)

