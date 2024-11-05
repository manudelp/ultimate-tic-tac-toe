# backend/api/online.py
from flask import Blueprint, jsonify, request
from flask_socketio import join_room, emit
import uuid
from socketio_instance import socketio

online_routes = Blueprint('online', __name__)
lobbies = {}


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

        print(f"\033[1;32mLobby {lobby_id} created by player {player_id}\033[0m")

        return jsonify({'lobby_id': lobby_id, 'player_id': player_id})
    except KeyError as e:
        return jsonify({'status': 'error', 'message': f'Missing key: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@online_routes.route('/join-lobby', methods=['POST'])
def join_lobby():
    lobby_id = request.json['lobby_id']
    player_id = request.json['player_id']
    if lobby_id in lobbies:
        lobbies[lobby_id]['players'].append(player_id)
        print(f"\033[1;32mPlayer {player_id} joined lobby {lobby_id}\033[0m")
        print(f"\033[1;32mCurrent players in lobby {lobby_id}: {lobbies[lobby_id]['players']}\033[0m")
        return jsonify({'status': 'joined'})
    return jsonify({'status': 'error', 'message': 'Lobby not found'}), 404

@socketio.on('join')
def on_join(data):
    lobby_id = data['lobby_id']
    player_id = data['player_id']
    user_letter = lobby_id[-2].upper()
    online_starts = lobby_id[-1].upper()

    if user_letter == 'X':
        user_letter = 'O'
    elif user_letter == 'O':
        user_letter = 'X'
    else:
        raise ValueError(f'Invalid user letter received, letter received was: {user_letter}')

    join_room(lobby_id)
    emit('player-joined', {'player_id': player_id}, room=lobby_id)
    
    # Automatically start the game when a player joins
    if len(lobbies[lobby_id]['players']) == 2:
        emit('game-started', {
            'user_letter': user_letter,
            'online_starts': online_starts,
            'lobby_id': lobby_id
        }, room=lobby_id)
        print(f"\033[1;34mGame started in lobby {lobby_id}\033[0m")

@online_routes.route('/send-move', methods=['POST'])
def send_move():
    lobby_id = request.json['lobby_id']
    player_id = request.json['player_id']
    move = request.json['move']
    emit('move', {'player_id': player_id, 'move': move}, room=lobby_id)

    return jsonify({'status': 'move sent'})
