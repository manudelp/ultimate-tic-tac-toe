"""The /game socket namespace: receive an event, ask the store, emit a snapshot.

Game state lives in core.store. What is here is transport and scheduling, the
two things that need a live server: bot moves on a worker so search does not
block the hub, and a greenlet per game that ends it when a clock runs out.
"""
import random

import gevent
from gevent.threadpool import ThreadPoolExecutor
from flask import request
from flask_socketio import Namespace, emit, join_room

from core.socketio import socketio
from core.position import Position
from core.store import store
from bots import AGENTS

DEFAULT_BOT_ID = 1   # Greedy as default fallback
ABANDON_GRACE = 300  # seconds a disconnected game is kept for a rejoin
_bot_executor = ThreadPoolExecutor(max_workers=2)


def get_bot_move(game, bot_id):
    """Get a move from a bot agent for the current game state."""
    bot = AGENTS.get(bot_id) or AGENTS.get(DEFAULT_BOT_ID)
    move = bot.choose(Position.from_engine(game.engine))
    return int(move[0]), int(move[1]), int(move[2]), int(move[3])


def broadcast(game):
    socketio.emit("game_state", game.engine.to_dict(), room=game.id, namespace="/game")


def schedule_bot_move(game_id, delay=0.5):
    """Schedule a bot move after a short delay for natural feel."""
    def _do_bot_move():
        gevent.sleep(delay)
        game = store.get(game_id)
        if not game or game.engine.status != "ongoing":
            return

        try:
            a, b, c, d = _bot_executor.submit(get_bot_move, game, game.bot_id).result()
            success, _ = game.engine.make_move(game.engine.active_player, a, b, c, d)
            if not success:
                return
            broadcast(game)
            if game.engine.status == "ongoing" and game.engine.active_player == game.bot_player:
                schedule_bot_move(game_id)
        except Exception as e:
            print(f"Bot move error: {e}")

    gevent.spawn(_do_bot_move)


def cancel_timeout(game):
    if game.timer is not None:
        game.timer.kill()
        game.timer = None


def schedule_timeout(game):
    """End the game when the active player's clock expires."""
    engine = game.engine
    if not engine.clocks or engine.status != "ongoing":
        return
    remaining = engine.clocks[engine.active_player]
    if remaining <= 0:
        return

    cancel_timeout(game)

    def _on_timeout():
        gevent.sleep(remaining)
        current = store.get(game.id)
        if not current or current.engine.status != "ongoing":
            return
        if current.engine.check_timeout():
            broadcast(current)
        current.timer = None

    game.timer = gevent.spawn(_on_timeout)


def advance(game):
    """After a successful move: broadcast, re-arm the clock, let a bot reply."""
    broadcast(game)
    if game.engine.status != "ongoing":
        return
    schedule_timeout(game)
    if game.has_bot and game.engine.active_player == game.bot_player:
        schedule_bot_move(game.id)


def started_payload(game, seat):
    bot = AGENTS.get(game.bot_id) if game.has_bot else None
    return {
        "gameId": game.id,
        "yourPlayer": game.symbol_at(seat),
        "state": game.engine.to_dict(),
        "opponent": {"type": "bot", "name": bot.name, "icon": bot.icon} if bot else None,
        "local": game.is_local or None,
    }


class GameNamespace(Namespace):

    def on_connect(self):
        print(f"Client {request.sid} connected to /game")

    def on_disconnect(self):
        sid = request.sid
        game = store.release(sid)
        if game and game.engine.status == "ongoing":
            game.engine.pause_clock()
            cancel_timeout(game)
            if game.is_pvp:
                emit("opponent_left", {}, room=game.id, include_self=False)
            broadcast(game)
        if game:
            gevent.spawn_later(ABANDON_GRACE, self._abandon, game.id)
        print(f"Client {sid} disconnected from /game")

    def _abandon(self, game_id):
        game = store.forget(game_id)
        if game:
            cancel_timeout(game)

    def on_rejoin_game(self, data):
        sid = request.sid
        game = store.get(data.get("gameId"))
        if not game:
            emit("rejoin_failed", {})
            return

        connected = set(socketio.server.manager.get_participants("/game", game.id))
        seat = store.reseat(game, sid, data.get("myPlayer"), connected)
        join_room(game.id)

        if game.engine.status == "ongoing":
            game.engine.resume_clock()
            schedule_timeout(game)

        if game.is_pvp:
            socketio.emit("opponent_rejoined", {}, room=game.id, namespace="/game", skip_sid=sid)

        emit("game_started", started_payload(game, seat))

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
        game = store.game_for(request.sid)
        if not game:
            emit("error", {"message": "No active game"})
            return

        # On a shared screen whoever is to move is the one clicking.
        player = game.engine.active_player if game.is_local else game.player_of(request.sid)
        if player is None:
            emit("error", {"message": "Not a player in this game"})
            return

        a, b, c, d = data.get("a"), data.get("b"), data.get("c"), data.get("d")
        if any(v is None for v in (a, b, c, d)):
            emit("error", {"message": "Invalid move format"})
            return

        success, err = game.engine.make_move(player, int(a), int(b), int(c), int(d))
        if not success:
            if err == "Time expired":
                broadcast(game)
            emit("error", {"message": err})
            return

        advance(game)

    def on_resign(self, data):
        game = store.game_for(request.sid)
        if not game or game.engine.status != "ongoing":
            return

        player = game.engine.active_player if game.is_local else game.player_of(request.sid)
        if player is None:
            return

        game.engine.status = "won"
        game.engine.winner = -player
        cancel_timeout(game)
        broadcast(game)

    # ── Private methods ──

    def _start_local_game(self, sid, data):
        starts = 1 if data.get("starts", "player") == "player" else -1
        game = store.open_local(sid, starts, data.get("timeControl", 300))
        join_room(game.id)
        schedule_timeout(game)
        emit("game_started", started_payload(game, 0))

    def _start_bot_game(self, sid, data):
        human_starts = data.get("starts", "player") == "player"
        game = store.open_vs_bot(
            sid,
            data.get("botId", DEFAULT_BOT_ID),
            1 if human_starts else -1,
            data.get("timeControl", 300),
        )
        join_room(game.id)
        schedule_timeout(game)
        emit("game_started", started_payload(game, 0))
        if not human_starts:
            schedule_bot_move(game.id)

    def _create_lobby(self, sid, data):
        game = store.open_lobby(sid, data.get("timeControl", 300))
        join_room(game.id)
        emit("lobby_created", {"gameId": game.id})

    def _join_lobby(self, sid, data):
        try:
            game = store.join_lobby(sid, data.get("gameId"))
        except (LookupError, ValueError) as e:
            emit("error", {"message": str(e)})
            return

        join_room(game.id)
        schedule_timeout(game)
        for seat in (0, 1):
            socketio.emit(
                "game_started", started_payload(game, seat),
                room=game.seats[seat], namespace="/game",
            )

    def _enter_matchmaking(self, sid, data):
        if store.is_queued(sid):
            emit("error", {"message": "Already in queue"})
            return

        time_control = data.get("timeControl", 300)
        waiting = store.take_waiting(time_control)
        if waiting is None:
            store.join_queue(sid, time_control)
            emit("searching", {})
            return

        first, second = (waiting, sid) if random.choice([True, False]) else (sid, waiting)
        game = store.open_matched(first, second, time_control)
        socketio.server.enter_room(first, game.id, namespace="/game")
        socketio.server.enter_room(second, game.id, namespace="/game")
        schedule_timeout(game)
        for seat in (0, 1):
            socketio.emit(
                "game_started", started_payload(game, seat),
                room=game.seats[seat], namespace="/game",
            )


socketio.on_namespace(GameNamespace("/game"))
