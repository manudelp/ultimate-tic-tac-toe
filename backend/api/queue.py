from flask import jsonify
from api import queue_routes
from core.store import store


@queue_routes.route('/queue-counts', methods=['GET'])
def get_queue_counts():
    return jsonify(store.waiting_counts())
