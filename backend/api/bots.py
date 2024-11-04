import numpy as np
import api.utils as utils
from flask import Blueprint, jsonify, request
from agents.bot.randy import RandomAgent
from agents.bot.monkey import MonkeyAgent
from agents.bot.jardy import GardenerAgent
from agents.bot.taylor import TaylorAgent
from agents.bot.straightArrow import StraightArrowAgent
from agents.bot.iterold import IteroldAgent
from agents.bot.itterino import ItterinoAgent
from agents.bot.ordy import TidyPodatorAgent
from agents.bot.twinny import TwinPrunerAgent

bot_routes = Blueprint('bots', __name__)

# Initialize agents
# INITIALIZE THE FIRST AGENT. WILL PLAY 1VPLAYER, AND PLAY FIRST AGAINST BOTS
# AGENT1 = RandomAgent()
# AGENT1 = GardenerAgent()
# AGENT1 = MonkeyAgent()
AGENT1 = TaylorAgent()
# AGENT1 = StraightArrowAgent()
# AGENT1 = FooFinderAgent()
# AGENT1 = IteroldAgent()
# AGENT1 = ItterinoAgent()
# AGENT1 = TidyPodatorAgent()
# AGENT1 = TwinPrunerAgent()

# INITIALIZE THE SECOND AGENT. WILL PLAY SECOND AGAINST BOTS
# AGENT2 = RandomAgent()
# AGENT2 = GardenerAgent()
# AGENT2 = MonkeyAgent()
# AGENT2 = TaylorAgent()
AGENT2 = StraightArrowAgent()
# AGENT2 = FooFinderAgent()
# AGENT2 = IteroldAgent()
# AGENT2 = ItterinoAgent()
# AGENT2 = TidyPodatorAgent()
# AGENT2 = TwinPrunerAgent()

@bot_routes.route('/get-bot-names', methods=['GET'])
def get_bot_names():
    try:
        agent1_name = str(AGENT1)
        agent2_name = str(AGENT2)
        return jsonify({'agent1_name': agent1_name, 'agent2_name': agent2_name})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@bot_routes.route('/get-bot-move', methods=['POST'])
def get_bot_move():
    try:
        # Get the JSON data from the request
        data = request.json
        
        # Print the JSON data for debugging
        # print("\n\nJSON data received:", data)

        # Extract 'board' and 'activeMiniBoard' from the JSON data
        board = data.get('board')
        active_mini_board = data.get('activeMiniBoard')
        turn = data.get('turn')

        # Check if 'board' is present in the JSON data
        if board is None:
            print("Invalid input - missing board")  # Print error message for debugging
            return jsonify({'error': 'Invalid input, missing Board'}), 400  # Return error response

        # Convert the board to a 3x3x3x3 4D NumPy array
        board_array = np.array(board, dtype=int).reshape((3, 3, 3, 3))
        board_results = utils.get_board_results(board_array)
        if active_mini_board is not None:
            board_to_play = board_array[active_mini_board[0]][active_mini_board[1]]
        else:
            board_to_play = None

        # for debug
        if turn == "O":
            agent_turn = str(AGENT1)
        elif turn == "X":
            agent_turn = str(AGENT2)
        else:
            raise ValueError(f"TURN IS NEITHER 'X' NOR 'O'!")

        # print(f"It will be turn {turn} for the bot, meaning turn for {agent_turn}")
        # print(f"Their received board to play in is {active_mini_board}, which looks like this currently:\n{board_to_play}")  # Print the turn for debugging
        # print("Their received board is:")  # Print the turn for debugging
        # utils.fancyBoardPrinter(board_array)  # Print the board for debugging

        # print(f"\nReceived board results is \n{board_results}\n")  # Print the board results for debugging

        # Check if the game is already over
        winner = utils.get_GlobalWinner(board_results)
        if winner != 0:
            print("che alguien gano pa'")
            return jsonify({'error': 'Game Over'}), 400
        
        # Get the move from the agent
        if turn == "O":
            agent_id = str(AGENT1)
            move = AGENT1.action(board_array, active_mini_board)
        elif turn == "X":
            agent_id = str(AGENT2)
            board_negative = -1 * board_array
            move = AGENT2.action(board_negative, active_mini_board)
        else:
            raise ValueError(f"TURN IS NEITHER 'X' NOR 'O'!")

        # board_copy = board_array.copy()
        # board_copy[move[0]][move[1]][move[2]][move[3]] = 1 if turn == "O" else -1
        # board_copy_results = utils.get_board_results(board_copy)

        # print("\nBoard after move:")  # Print the board after the move for debugging
        # utils.fancyBoardPrinter(board_copy)  # Print the board for debugging

        # print(f"\nNow board results is \n{board_copy_results}!!\n")  # Print the board results for debugging

        # Convert the move to a tuple of integers
        move_response = (int(move[0]), int(move[1]), int(move[2]), int(move[3]))
        print(f"\nMove calculated by {agent_id}:", move_response)  # Print the calculated move for debugging

        # Return the move and agent's id as a JSON response
        return jsonify({'move': move_response, 'agent_id': agent_id})
    except Exception as e:
        print(f"\nError: {e}\n")

        # Return an internal server error response
        return jsonify({'error': 'Internal Server Error'}), 500

@bot_routes.route('/agents-reset', methods=['POST'])
def agents_reset():
    try:
        # Reset the agents
        AGENT1.reset()
        AGENT2.reset()

        # Return a success response
        return jsonify({'message': 'Agents reset successfully'})
    except Exception as e:
        print(f"\nError: {e}\n")

        # Return an internal server error response
        return jsonify({'error': 'Internal Server Error'}), 500
