from flask import jsonify
from api import queue_routes
from api.game import matchmaking_queue
from collections import Counter


@queue_routes.route('/queue-counts', methods=['GET'])
def get_queue_counts():
    counts = Counter(entry.get("timeControl", 300) for entry in matchmaking_queue)
    return jsonify(dict(counts))
