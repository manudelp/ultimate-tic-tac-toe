import time
import random
import numpy as np
import gevent
from gevent.threadpool import ThreadPoolExecutor
from flask import request
from flask_socketio import Namespace, emit, join_room, leave_room
from core.socketio import socketio
from core.engine import GameEngine
from bots import AGENTS


# In-memory stores
games = {}           # game_id -> GameEngine
player_games = {}    # sid -> game_id
game_players = {}    # game_id -> {"player1_sid", "player2_sid", "player1_num"}
matchmaking_queue = []  # [{'sid': ..., 'time': ..., 'timeControl': ...}]
DEFAULT_BOT_ID = 1   # Greedy as default fallback
_bot_executor = ThreadPoolExecutor(max_workers=2)


def get_bot_move(game, bot_id):
    """Get a move from a bot agent for the current game state."""
    bot = AGENTS.get(bot_id)
    if not bot:
        bot = AGENTS.get(DEFAULT_BOT_ID)

    # Bots always play as 1 internally, so flip board so bot sees itself as 1
    board = game.board.copy() * -game.active_player

    forced = list(game.forced_board) if game.forced_board else None
    move = bot.action(board, forced)
    return int(move[0]), int(move[1]), int(move[2]), int(move[3])


def schedule_bot_move(game_id, bot_id, delay=0.5):
    """Schedule a bot move after a short delay for natural feel."""
    def _do_bot_move():
        gevent.sleep(delay)
        game = games.get(game_id)
        if not game or game.status != "ongoing":
            return

        try:
            a, b, c, d = _bot_executor.submit(get_bot_move, game, bot_id).result()
            success, err = game.make_move(game.active_player, a, b, c, d)
            if success:
                state = game.to_dict()
                socketio.emit("game_state", state, room=game_id, namespace="/game")

                # If game is still ongoing and it's still bot's turn, move again
                if game.status == "ongoing":
                    bot_player = game_id_to_bot.get(game_id, {}).get("player")
                    if bot_player == game.active_player:
                        schedule_bot_move(game_id, bot_id)
        except Exception as e:
            print(f"Bot move error: {e}")

    gevent.spawn(_do_bot_move)


# Track which games have bots: game_id -> {"bot_id": int, "player": int}
game_id_to_bot = {}
# Track local PvP games (no bot, both moves from same client)
local_games = set()
# Track pending timeout greenlets: game_id -> greenlet
timeout_greenlets = {}


def schedule_timeout(game_id):
    """Schedule a greenlet to end the game when the active player's clock expires."""
    game = games.get(game_id)
    if not game or not game.clocks or game.status != "ongoing":
        return
    remaining = game.clocks[game.active_player]
    if remaining <= 0:
        return

    old = timeout_greenlets.pop(game_id, None)
    if old:
        old.kill()

    def _on_timeout():
        gevent.sleep(remaining)
        g = games.get(game_id)
        if not g or g.status != "ongoing":
            return
        if g.check_timeout():
            socketio.emit("game_state", g.to_dict(), room=game_id, namespace="/game")
        timeout_greenlets.pop(game_id, None)

    timeout_greenlets[game_id] = gevent.spawn(_on_timeout)


class GameNamespace(Namespace):

    def on_connect(self):
        print(f"Client {request.sid} connected to /game")

    def on_disconnect(self):
        sid = request.sid
        global matchmaking_queue
        matchmaking_queue = [p for p in matchmaking_queue if p["sid"] != sid]

        game_id = player_games.pop(sid, None)
        if game_id and game_id in games:
            game = games[game_id]
            if game.status == "ongoing":
                game.pause_clock()
                old = timeout_greenlets.pop(game_id, None)
                if old:
                    old.kill()
                # Only notify opponent in real PvP games
                if game_id not in local_games and game_id not in game_id_to_bot:
                    emit("opponent_left", {}, room=game_id, include_self=False)
            def _cleanup():
                games.pop(game_id, None)
                game_players.pop(game_id, None)
                game_id_to_bot.pop(game_id, None)
                local_games.discard(game_id)
                g = timeout_greenlets.pop(game_id, None)
                if g:
                    g.kill()
            gevent.spawn_later(300, _cleanup)

        print(f"Client {sid} disconnected from /game")

    def on_rejoin_game(self, data):
        sid = request.sid
        game_id = data.get("gameId")
        my_player = data.get("myPlayer")  # "X" or "O"
        game = games.get(game_id)

        if not game:
            emit("rejoin_failed", {})
            return

        players = game_players.get(game_id, {})
        p1_num = players.get("player1_num", 1)
        # Determine target slot from the player's own reported identity
        if my_player == ("X" if p1_num == 1 else "O"):
            players["player1_sid"] = sid
        elif my_player == ("O" if p1_num == 1 else "X"):
            players["player2_sid"] = sid
        else:
            # Fallback: replace first disconnected slot
            connected_sids = set(socketio.server.manager.get_participants("/game", game_id))
            if players.get("player1_sid") not in connected_sids:
                players["player1_sid"] = sid
            else:
                players["player2_sid"] = sid

        player_games[sid] = game_id
        join_room(game_id)

        if game.status == "ongoing":
            game.resume_clock()
            schedule_timeout(game_id)

        # Notify the other player that opponent rejoined
        if game_id not in local_games and game_id not in game_id_to_bot:
            socketio.emit("opponent_rejoined", {}, room=game_id, namespace="/game", skip_sid=sid)

        player_num = self._get_player_number(game_id, sid)
        your_player = "X" if player_num == 1 else "O"
        is_local = game_id in local_games
        bot_info = game_id_to_bot.get(game_id)
        bot = AGENTS.get(bot_info["bot_id"]) if bot_info else None

        emit("game_started", {
            "gameId": game_id,
            "yourPlayer": your_player,
            "state": game.to_dict(),
            "opponent": {"type": "bot", "name": bot.name, "icon": bot.icon} if bot else None,
            "local": is_local or None,
        })

    def on_find_game(self, data):
        sid = request.sid
        mode = data.get("mode", "matchmaking")

        if mode == "local":
            self._start_local_game(sid, data)
        elif mode == "bot":
            self._start_bot_game(sid, data)
        elif mode == "lobby_create":
            self._create_lobby(sid, data)
        elif mode == "lobby_join":
            self._join_lobby(sid, data)
        else:
            self._enter_matchmaking(sid, data)

    def on_make_move(self, data):
        sid = request.sid
        game_id = player_games.get(sid)
        if not game_id or game_id not in games:
            emit("error", {"message": "No active game"})
            return

        game = games[game_id]

        if game_id in local_games:
            player = game.active_player
        else:
            player = self._get_player_number(game_id, sid)
            if player is None:
                emit("error", {"message": "Not a player in this game"})
                return

        a, b, c, d = data.get("a"), data.get("b"), data.get("c"), data.get("d")
        if any(v is None for v in (a, b, c, d)):
            emit("error", {"message": "Invalid move format"})
            return

        success, err = game.make_move(player, int(a), int(b), int(c), int(d))
        if not success:
            if err == "Time expired":
                socketio.emit("game_state", game.to_dict(), room=game_id, namespace="/game")
            emit("error", {"message": err})
            return

        state = game.to_dict()
        socketio.emit("game_state", state, room=game_id, namespace="/game")

        if game.status == "ongoing":
            schedule_timeout(game_id)
            if game_id in game_id_to_bot:
                bot_info = game_id_to_bot[game_id]
                if game.active_player == bot_info["player"]:
                    schedule_bot_move(game_id, bot_info["bot_id"])

    def on_resign(self, data):
        sid = request.sid
        game_id = player_games.get(sid)
        if not game_id or game_id not in games:
            return

        game = games[game_id]
        if game.status != "ongoing":
            return

        if game_id in local_games:
            game.status = "won"
            game.winner = -game.active_player
        else:
            player = self._get_player_number(game_id, sid)
            if not player:
                return
            game.status = "won"
            game.winner = -player

        socketio.emit("game_state", game.to_dict(), room=game_id, namespace="/game")

    # ── Private methods ──

    def _start_local_game(self, sid, data):
        starts = data.get("starts", "player")
        time_control = data.get("timeControl", 300)

        game = GameEngine(time_per_player=time_control)
        game_id = game.id
        games[game_id] = game
        local_games.add(game_id)

        join_room(game_id)
        player_games[sid] = game_id
        game_players[game_id] = {
            "player1_sid": sid,
            "player2_sid": None,
            "player1_num": 1,
        }

        game.start()
        if starts == "playerO":
            game.active_player = -1
        schedule_timeout(game_id)

        emit("game_started", {
            "gameId": game_id,
            "yourPlayer": "X" if starts == "player" else "O",
            "state": game.to_dict(),
            "local": True,
        })

    def _start_bot_game(self, sid, data):
        bot_id = data.get("botId", DEFAULT_BOT_ID)
        starts = data.get("starts", "player")
        time_control = data.get("timeControl", 300)

        game = GameEngine(time_per_player=time_control)
        game_id = game.id
        games[game_id] = game

        join_room(game_id)
        player_games[sid] = game_id
        game_players[game_id] = {
            "player1_sid": sid,
            "player2_sid": None,
            "player1_num": 1 if starts == "player" else -1,
        }

        bot_player = -1 if starts == "player" else 1
        game_id_to_bot[game_id] = {"bot_id": bot_id, "player": bot_player}

        game.start()
        schedule_timeout(game_id)

        bot = AGENTS.get(bot_id)
        emit("game_started", {
            "gameId": game_id,
            "yourPlayer": "X" if starts == "player" else "O",
            "state": game.to_dict(),
            "opponent": {"type": "bot", "name": bot.name, "icon": bot.icon} if bot else None,
        })

        if starts == "bot":
            schedule_bot_move(game_id, bot_id)

    def _create_lobby(self, sid, data):
        time_control = data.get("timeControl", 300)
        game = GameEngine(time_per_player=time_control)
        game_id = game.id
        games[game_id] = game

        join_room(game_id)
        player_games[sid] = game_id
        game_players[game_id] = {
            "player1_sid": sid,
            "player2_sid": None,
            "player1_num": 1,
        }

        emit("lobby_created", {"gameId": game_id})

    def _join_lobby(self, sid, data):
        game_id = data.get("gameId")
        if not game_id or game_id not in games:
            emit("error", {"message": "Game not found"})
            return

        players = game_players.get(game_id)
        if not players or players["player2_sid"] is not None:
            emit("error", {"message": "Game is full"})
            return

        players["player2_sid"] = sid
        join_room(game_id)
        player_games[sid] = game_id

        game = games[game_id]
        game.start()
        schedule_timeout(game_id)

        socketio.emit("game_started", {
            "gameId": game_id,
            "yourPlayer": "X",
            "state": game.to_dict(),
        }, room=players["player1_sid"], namespace="/game")

        socketio.emit("game_started", {
            "gameId": game_id,
            "yourPlayer": "O",
            "state": game.to_dict(),
        }, room=sid, namespace="/game")

    def _enter_matchmaking(self, sid, data):
        global matchmaking_queue

        if any(e["sid"] == sid for e in matchmaking_queue):
            emit("error", {"message": "Already in queue"})
            return

        time_control = data.get("timeControl", 300)

        # Find opponent with same time control
        opponent = None
        for i, entry in enumerate(matchmaking_queue):
            if entry.get("timeControl") == time_control:
                opponent = matchmaking_queue.pop(i)
                break

        if opponent:
            self._create_matched_game(opponent["sid"], sid, time_control)
        else:
            matchmaking_queue.append({"sid": sid, "time": time.time(), "timeControl": time_control})
            emit("searching", {})

    def _create_matched_game(self, sid1, sid2, time_control=300):
        game = GameEngine(time_per_player=time_control)
        game_id = game.id
        games[game_id] = game

        socketio.server.enter_room(sid1, game_id, namespace="/game")
        socketio.server.enter_room(sid2, game_id, namespace="/game")
        player_games[sid1] = game_id
        player_games[sid2] = game_id

        if random.choice([True, False]):
            p1_sid, p2_sid = sid1, sid2
        else:
            p1_sid, p2_sid = sid2, sid1

        game_players[game_id] = {
            "player1_sid": p1_sid,
            "player2_sid": p2_sid,
            "player1_num": 1,
        }

        game.start()
        schedule_timeout(game_id)

        socketio.emit("game_started", {
            "gameId": game_id,
            "yourPlayer": "X",
            "state": game.to_dict(),
        }, room=p1_sid, namespace="/game")

        socketio.emit("game_started", {
            "gameId": game_id,
            "yourPlayer": "O",
            "state": game.to_dict(),
        }, room=p2_sid, namespace="/game")

    def _get_player_number(self, game_id, sid):
        players = game_players.get(game_id)
        if not players:
            return None
        if sid == players["player1_sid"]:
            return players["player1_num"]
        elif sid == players["player2_sid"]:
            return -players["player1_num"]
        return None


socketio.on_namespace(GameNamespace("/game"))
