import os
import sys
import uuid
from flask import jsonify, request
from flask_socketio import Namespace, emit, join_room
from . import online_routes, lobbies, socketio

# Define a Socket.IO namespace for online gameplay
class OnlineNamespace(Namespace):
    def on_connect(self):
        print("Client connected to /online namespace")

    def on_disconnect(self):
        print(f"Client {request.sid} disconnected from /online namespace")
        
        # Find any lobbies this player is in
        for code, lobby in list(lobbies.items()):
            if request.sid in lobby['players']:
                # Notify other players in the lobby
                emit('opponentDisconnected', {}, room=code, include_self=False)
                
                # Remove the lobby
                del lobbies[code]
                print(f"Lobby {code} removed because player {request.sid} disconnected")
                break

    def on_createLobby(self, data):
        code = data['code']
        if code not in lobbies:
            lobbies[code] = {'players': [request.sid]}
            join_room(code)
            emit('lobbyCreated', {'code': code})
            print(f"Lobby {code} created by player: {request.sid}")
        else:
            emit('error', {'message': 'Lobby code already exists'})

    def on_joinLobby(self, data):
        code = data['code']
        if code in lobbies and len(lobbies[code]['players']) == 1:
            lobbies[code]['players'].append(request.sid)
            join_room(code)

            players = lobbies[code]['players']
            player1_sid, player2_sid = players[0], players[1]

            # Assign player1 -> X, player2 -> O
            emit('startGame', {'yourLetter': 'X', 'opponentLetter': 'O', 'yourTurn': True}, room=player1_sid)
            emit('startGame', {'yourLetter': 'O', 'opponentLetter': 'X', 'yourTurn': False}, room=player2_sid)

            print(f"Player {request.sid} joined lobby {code}")
        else:
            print(f"Lobby code is {code}, while lobbies are {lobbies}")
            print(f"Amount of players in lobby is {len(lobbies[code]['players']) if code in lobbies else 'N/A'}")
            
    def on_leaveLobby(self, data):
        code = data.get('code')
        if not code or code not in lobbies:
            return
        
        # Find this player's SID
        player_sid = request.sid
        
        # Check if player is in this lobby
        if code in lobbies and player_sid in lobbies[code]['players']:
            # Notify other players in the lobby that this player left
            for sid in lobbies[code]['players']:
                if sid != player_sid:
                    emit('opponentLeft', {
                        'message': 'Your opponent has left the game'
                    }, room=sid)
            
            # Remove the lobby
            del lobbies[code]
            print(f"Lobby {code} removed because player {player_sid} left")

    def on_makeMove(self, data):
        code = data['code']
        move = data['move']
        print(f"Move made in lobby {code}: {move}")
        emit('opponentMove', move, room=code, include_self=False)
        
    def on_gameOver(self, data):
        code = data['code']
        winner = data['winner']
        winningLine = data.get('winningLine')  # This might be optional
        
        print(f"Game over in lobby {code}. Winner: {winner}")
        # Broadcast to everyone in the room except sender
        emit('gameOver', {
            'winner': winner,
            'winningLine': winningLine
        }, room=code, include_self=False)

# Register the namespace
socketio.on_namespace(OnlineNamespace('/online'))
