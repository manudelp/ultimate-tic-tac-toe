# backend/api/bots.py

import numpy as np
import api.utils as utils
import time
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional
from flask import Blueprint, jsonify, request
from agents.bot.randy import RandomAgent
from agents.bot.monkey import MonkeyAgent
from agents.bot.jardy import GardenerAgent
from agents.bot.taylor import TaylorAgent
from agents.bot.jardito import JardineritoAgent
from agents.bot.straightArrow import StraightArrowAgent
from agents.bot.iterold import IteroldAgent
from agents.bot.itterino import ItterinoAgent
from agents.bot.ordy import TidyPodatorAgent
from agents.bot.twinny import TwinPrunerAgent
from agents.bot.maxi import MaximilianoAgent
from agents.bot.jarditonomid import JardineritoAntiMidAgent
from agents.bot.jarditobetter import BetterJardineritoAgent
from agents.foofinder import FooFinderAgent

bot_routes = Blueprint('bots', __name__)

# IDs Dictionary, Agent:obj ; ID:int
AGENTS = {
    RandomAgent().id : RandomAgent(),
    TaylorAgent().id : TaylorAgent(), 
    StraightArrowAgent().id : StraightArrowAgent(), 
    JardineritoAgent().id : JardineritoAgent(), 
    BetterJardineritoAgent().id : BetterJardineritoAgent(), 
    MonkeyAgent().id : MonkeyAgent(),
    FooFinderAgent().id : FooFinderAgent(),
}

@bot_routes.route('/get-bot-list', methods=['GET'])
def get_bot_list():
    # Extract id, name and icon from each agent
    bot_list = [{'id': agent.id, 'name': agent.name, 'icon': agent.icon} for agent in AGENTS.values()]
    return jsonify(bot_list)
    

@bot_routes.route('/get-bot-move', methods=['POST'])
def get_bot_move():
    # print(Fore.BLUE + Style.BRIGHT + "TRYING GET_BOT_MOVE FROM THE BACKEND" + Style.RESET_ALL)
    try:
        # Get the JSON data from the request
        data = request.json
        
        # Print the JSON data for debugging
        # print("\n\nJSON data received:", data)

        # Extract 'board' and 'activeMiniBoard' from the JSON data
        id = data.get('bot') 
        bot = AGENTS.get(id)
        
        if bot is None:
            print(f"Invalid bot id: {id}")  # Print error message for debugging
            return jsonify({'error': 'Invalid bot id'}), 400  # Return error response
        
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

        # # # DEBUG BEFORE MOVE (UNCOMMENT ME)
        # print(f"It will be turn {turn} for the bot, meaning turn for {agent_turn}")
        # print(f"Their received board to play in is {active_mini_board}, which looks like this currently:\n{board_to_play}")  # Print the turn for debugging
        # print("Their received board is:")  # Print the turn for debugging
        # utils.fancyBoardPrinter(board_array)  # Print the board for debugging
        # print(f"\nReceived board results is \n{board_results}\n")  # Print the board results for debugging

        # Check if the game is already over
        winner = utils.get_winner(board_results)
        if winner != 0:
            print("che alguien gano pa'")
            return jsonify({'error': 'Game Over'}), 400
        
        # Get the move from the agent
        if turn == "X":
            board_array = board_array * -1
            move = bot.action(board_array, active_mini_board)
        else:
            move = bot.action(board_array, active_mini_board)

        # # # DEBUG AFTER MOVE (UNCOMMENT ME)
        # board_copy = board_array.copy()
        # board_copy[move[0]][move[1]][move[2]][move[3]] = 1 if turn == "O" else -1
        # board_copy_results = utils.get_board_results(board_copy)
        # print("\nBoard after move:")  # Print the board after the move for debugging
        # utils.fancyBoardPrinter(board_copy)  # Print the board for debugging
        # print(f"Current active Mini Board or Board to Play is {active_mini_board}")  # Print the active mini board for debugging
        # print(f"\nNow board results is \n{board_copy_results}!!\n")  # Print the board results for debugging

        # Convert the move to a tuple of integers
        move_response = (int(move[0]), int(move[1]), int(move[2]), int(move[3]))
        print(f"\nMove calculated by {bot.name}:", move_response)  # Print the calculated move for debugging

        # Return the move and agent's id as a JSON response
        return jsonify({'move': move_response, 'bot_name': bot.name})
    except Exception as e:
        print(f"\nError: {e}\n")

        # Return an internal server error response
        return jsonify({'error': 'Internal Server Error'}), 500

@bot_routes.route('/agents-reset', methods=['POST'])
def agents_reset():
    try:
        
        # Identify the agent to reset
        id = request.json.get('id')
        bot = AGENTS.get(id)
        
        # Reset the agents
        bot.reset()

        # Return a success response
        return jsonify({'message': 'Agent reset successfully'})
    except Exception as e:
        print(f"\nError: {e}\n")

        # Return an internal server error response
        return jsonify({'error': 'Internal Server Error'}), 500
