# backend/api/online.py

import os
import sys
import uuid
from flask import Blueprint, jsonify, request
from flask_socketio import Namespace, emit, join_room
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from socketio_instance import socketio

# Create a blueprint for online routes
online_routes = Blueprint('online', __name__)

# In-memory storage for lobbies
lobbies = {}

# Define a Socket.IO namespace for online gameplay
class OnlineNamespace(Namespace):
    def on_connect(self):
        print("Client connected to /online namespace")

    def on_disconnect(self):
        print("Client disconnected from /online namespace")

    def on_createLobby(self, data):
        code = data['code']
        if code not in lobbies:
            lobbies[code] = {'players': [request.sid]}
            join_room(code)
            emit('lobbyCreated', {'code': code})
            print(f"Lobby {code} created by {request.sid}")
        else:
            emit('error', {'message': 'Lobby code already exists'})

    def on_joinLobby(self, data):
        code = data['code']
        if code in lobbies and len(lobbies[code]['players']) == 1:
            lobbies[code]['players'].append(request.sid)
            join_room(code)
            emit('startGame', room=code)
            print(f"Player {request.sid} joined lobby {code}")
        else:
            emit('error', {'message': 'Lobby not found or full'})

    def on_makeMove(self, data):
        code = data['code']
        move = data['move']
        emit('opponentMove', move, room=code, include_self=False)

# Register the namespace
socketio.on_namespace(OnlineNamespace('/online'))

# HTTP routes
@online_routes.route('/create-lobby', methods=['POST'])
def create_lobby():
    try:
        player_id = request.json['player_id']
        user_letter = request.json['user_letter']
        online_starts = request.json['online_starts']
        lobby_id = str(uuid.uuid4()) + user_letter.lower() + online_starts.lower()

        if lobby_id in lobbies:
            return jsonify({'status': 'error', 'message': 'Lobby already exists'}), 400

        lobbies[lobby_id] = {'players': [player_id]}

        print(f"Lobby {lobby_id} created by player {player_id}")

        return jsonify({'lobby_id': lobby_id, 'player_id': player_id})
    except KeyError as e:
        return jsonify({'status': 'error', 'message': f'Missing key: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@online_routes.route('/join-lobby', methods=['POST'])
def join_lobby():
    try:
        lobby_id = request.json['lobby_id']
        player_id = request.json['player_id']
        if lobby_id in lobbies:
            lobbies[lobby_id]['players'].append(player_id)
            print(f"Player {player_id} joined lobby {lobby_id}")
            return jsonify({'status': 'joined'})
        return jsonify({'status': 'error', 'message': 'Lobby not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@online_routes.route('/send-move', methods=['POST'])
def send_move():
    try:
        lobby_id = request.json['lobby_id']
        player_id = request.json['player_id']
        move = request.json['move']

        socketio.emit('move', {'player_id': player_id, 'move': move}, room=lobby_id)
        print(f"Move made in lobby {lobby_id}")
        return jsonify({'status': 'success'})
    except KeyError as e:
        return jsonify({'status': 'error', 'message': f'Missing key: {str(e)}'}), 400
    except Exception as e:
        print(f"Unhandled Exception: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
