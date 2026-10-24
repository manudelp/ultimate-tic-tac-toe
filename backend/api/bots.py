from flask import jsonify
from api import bot_routes
from bots import AGENTS
from bots.difficulty import describe, load_ratings


@bot_routes.route('/get-bot-list', methods=['GET'])
def get_bot_list():
    try:
        ratings = load_ratings()
        bot_list = [{
            'id': agent.id,
            'name': agent.name,
            'icon': agent.icon,
            'description': agent.description,
            'difficulty': describe(ratings.get(agent.id)),
        } for agent in AGENTS.values()]
        bot_list.sort(key=lambda b: b['difficulty']['rating'] if b['difficulty']['rating'] is not None else float('inf'))
        return jsonify(bot_list)
    except Exception as e:
        print(f"Error in /get-bot-list: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
