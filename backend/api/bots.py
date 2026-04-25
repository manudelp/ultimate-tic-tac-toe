from flask import jsonify
from api import bot_routes
from bots import AGENTS


@bot_routes.route('/get-bot-list', methods=['GET'])
def get_bot_list():
    try:
        bot_list = [{
            'id': agent.id,
            'name': agent.name,
            'icon': agent.icon,
            'description': agent.description,
            'difficulty': agent.difficulty,
        } for agent in AGENTS.values()]
        return jsonify(bot_list)
    except Exception as e:
        print(f"Error in /get-bot-list: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
