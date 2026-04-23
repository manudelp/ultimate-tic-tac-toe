import random
from flask import jsonify, request
from flask_socketio import Namespace, emit, join_room
from . import online_routes, lobbies, socketio

connected_users = 0
matchmaking_queue = []

# Helper to get real IP address, accounting for proxies
def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def generate_lobby_code():
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# Define a Socket.IO namespace for online gameplay
class OnlineNamespace(Namespace):
    
    def on_connect(self):
        global connected_users
        connected_users += 1
        ip = get_client_ip()
        emit('connectedUsers', connected_users, broadcast=True, namespace='/online')
        print(f"Client connected to /online namespace: {ip} (Total: {connected_users})")

    def on_disconnect(self):
        global connected_users, matchmaking_queue
        connected_users = max(connected_users - 1, 0)
        ip = get_client_ip()
        sid = request.sid
        emit('connectedUsers', connected_users, broadcast=True, namespace='/online')
        print(f"Client {ip} disconnected from /online namespace (Total: {connected_users})")

        matchmaking_queue = [p for p in matchmaking_queue if p['sid'] != sid]

        for code, lobby in list(lobbies.items()):
            if sid in lobby['players']:
                emit('opponentDisconnected', {}, room=code, include_self=False)
                del lobbies[code]
                print(f"Lobby {code} removed because SID {sid} disconnected")
                break

    def on_createLobby(self, data):
        ip = get_client_ip()
        print(f"Creating lobby from IP {ip} with data: {data}")
        code = data['code']

        for existing in lobbies.values():
            if existing['ip'] == ip:
                emit('error', {'message': 'You already have a lobby'})
                return

        if code not in lobbies:
            lobbies[code] = {'players': [request.sid], 'ip': ip}
            join_room(code)
            emit('lobbyCreated', {'code': code})
            print(f"Lobby {code} created by IP: {ip}")
            print(f"Current lobbies: {lobbies}")
        else:
            emit('error', {'message': 'Lobby code already exists'})

    def on_joinLobby(self, data):
        ip = get_client_ip()
        code = data['code']
        print(f"IP {ip} attempting to join lobby {code} with data: {data}")

        if code not in lobbies:
            print(f"Lobby {code} does not exist")
            emit('error', {'message': 'Lobby does not exist'})
            return

        if len(lobbies[code]['players']) == 1:
            lobbies[code]['players'].append(request.sid)
            join_room(code)

            players = lobbies[code]['players']
            player1_sid, player2_sid = players[0], players[1]

            emit('startGame', {'yourLetter': 'X', 'opponentLetter': 'O', 'yourTurn': True}, room=player1_sid)
            emit('startGame', {'yourLetter': 'O', 'opponentLetter': 'X', 'yourTurn': False}, room=player2_sid)

            print(f"IP {ip} joined lobby {code}")
        else:
            emit('error', {'message': 'Lobby is full or empty'})

    def on_leaveLobby(self, data):
        ip = get_client_ip()
        code = data.get('code')
        print(f"IP {ip} leaving lobby {code}")

        if not code or code not in lobbies:
            return

        if lobbies[code]['ip'] == ip or request.sid in lobbies[code]['players']:
            for sid in lobbies[code]['players']:
                if sid != request.sid:
                    emit('opponentLeft', {'message': 'Your opponent has left the game'}, room=sid)

            del lobbies[code]
            print(f"Lobby {code} removed because IP {ip} left")

    def on_makeMove(self, data):
        code = data['code']
        move = data['move']
        print(f"Move made in lobby {code}: {move}")
        emit('opponentMove', move, room=code, include_self=False)

    def on_gameOver(self, data):
        code = data['code']
        winner = data['winner']
        winningLine = data.get('winningLine')

        print(f"Game over in lobby {code}. Winner: {winner}")
        emit('gameOver', {
            'winner': winner,
            'winningLine': winningLine
        }, room=code, include_self=False)

    def on_matchmakingSearch(self):
        sid = request.sid
        ip = get_client_ip()
        print(f"IP {ip} searching for match")

        for entry in matchmaking_queue:
            if entry['ip'] == ip:
                emit('error', {'message': 'Already in queue'})
                return

        if not matchmaking_queue:
            matchmaking_queue.append({'sid': sid, 'ip': ip})
            emit('searching')
            return

        opponent = matchmaking_queue.pop(0)
        opponent_sid = opponent['sid']
        opponent_ip = opponent['ip']

        code = generate_lobby_code()
        lobbies[code] = {'players': [opponent_sid, sid], 'ip': 'matchmaking'}

        join_room(code, sid=sid)
        join_room(code, sid=opponent_sid)

        if random.choice([True, False]):
            first_sid, second_sid = sid, opponent_sid
        else:
            first_sid, second_sid = opponent_sid, sid

        emit('startGame', {'yourLetter': 'X', 'opponentLetter': 'O', 'yourTurn': True}, room=first_sid)
        emit('startGame', {'yourLetter': 'O', 'opponentLetter': 'X', 'yourTurn': False}, room=second_sid)

        # Update matchFound events to include the player's letter
        emit('matchFound', {'code': code, 'yourLetter': 'X'}, room=first_sid)
        emit('matchFound', {'code': code, 'yourLetter': 'O'}, room=second_sid)

        print(f"Matchmaking: {ip} vs {opponent_ip} in lobby {code}")

# Register the namespace
socketio.on_namespace(OnlineNamespace('/online'))

# Add a debug route
@online_routes.route('/debug-lobbies', methods=['GET'])
def debug_lobbies():
    return jsonify({
        'lobbies': {code: {'players': players['players'], 'ip': players['ip']} for code, players in lobbies.items()},
        'count': len(lobbies)
    })
