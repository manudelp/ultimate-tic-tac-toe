"""The games currently being played.

A LiveGame holds everything about one game in progress: the engine, who sits in
each seat, and the bot if there is one. The store maps connections to games and
runs the matchmaking queue. Nothing here knows about sockets or greenlets, so a
game's whole lifecycle can be driven in a plain test.

A seat token identifies one connection. Callers pass whatever they use for that;
the store only compares them.
"""
import time

from core.engine import GameEngine

X = 1
O = -1


class LiveGame:
    """One game in progress. `seats[0]` is the player shown as `first_seat_player`."""

    __slots__ = ("engine", "seats", "first_seat_player", "bot_id", "bot_player", "is_local", "timer")

    def __init__(self, engine, first_seat_player=X, is_local=False):
        self.engine = engine
        self.seats = [None, None]
        self.first_seat_player = first_seat_player
        self.bot_id = None
        self.bot_player = None
        self.is_local = is_local
        self.timer = None  # whatever the caller uses to cancel a scheduled timeout

    @property
    def id(self):
        return self.engine.id

    @property
    def has_bot(self):
        return self.bot_id is not None

    @property
    def is_pvp(self):
        """True only for games where a human opponent can be notified."""
        return not self.is_local and not self.has_bot

    def player_at(self, seat):
        return self.first_seat_player if seat == 0 else -self.first_seat_player

    def seat_of(self, token):
        """Which seat this connection holds, or None."""
        for seat, held in enumerate(self.seats):
            if held is not None and held == token:
                return seat
        return None

    def player_of(self, token):
        """Which side this connection plays, +1 or -1, or None if not seated."""
        seat = self.seat_of(token)
        return None if seat is None else self.player_at(seat)

    def symbol_at(self, seat):
        return "X" if self.player_at(seat) == X else "O"

    def seat_for_symbol(self, symbol):
        """The seat that plays this symbol, or None if it names neither."""
        for seat in (0, 1):
            if self.symbol_at(seat) == symbol:
                return seat
        return None

    def is_waiting(self):
        """A lobby game nobody has joined yet."""
        return self.seats[1] is None and self.is_pvp


class GameStore:
    """Games in progress, who is connected to them, and who is waiting for one."""

    def __init__(self):
        self._games = {}       # game_id -> LiveGame
        self._by_token = {}    # seat token -> game_id
        self._queue = []       # [{"token", "time", "timeControl"}]

    # ---- looking things up ----

    def get(self, game_id):
        return self._games.get(game_id)

    def game_for(self, token):
        """The game this connection is seated in, or None."""
        return self._games.get(self._by_token.get(token))

    def waiting_counts(self):
        """How many are queued, by time control."""
        counts = {}
        for entry in self._queue:
            counts[entry["timeControl"]] = counts.get(entry["timeControl"], 0) + 1
        return counts

    # ---- opening games ----

    def open_local(self, token, starts_player, time_control):
        """Both sides played from one client. `starts_player` is +1 or -1."""
        game = self._open(token, time_control, first_seat_player=starts_player, is_local=True)
        game.engine.active_player = starts_player
        game.engine.start()
        return game

    def open_vs_bot(self, token, bot_id, human_player, time_control):
        """`human_player` is the side the person plays, +1 or -1."""
        game = self._open(token, time_control, first_seat_player=human_player)
        game.bot_id = bot_id
        game.bot_player = -human_player
        game.engine.start()
        return game

    def open_lobby(self, token, time_control):
        """A game waiting for someone to join by id. The clock starts on join."""
        return self._open(token, time_control)

    def join_lobby(self, token, game_id):
        """Seat a second player. Returns the game, or raises LookupError/ValueError."""
        game = self._games.get(game_id)
        if game is None:
            raise LookupError("Game not found")
        if game.seats[1] is not None:
            raise ValueError("Game is full")
        game.seats[1] = token
        self._by_token[token] = game_id
        game.engine.start()
        return game

    def open_matched(self, first_token, second_token, time_control):
        """A matchmade game. The caller decides who takes the first seat."""
        game = self._open(first_token, time_control)
        game.seats[1] = second_token
        self._by_token[second_token] = game.id
        game.engine.start()
        return game

    def _open(self, token, time_control, first_seat_player=X, is_local=False):
        game = LiveGame(GameEngine(time_per_player=time_control), first_seat_player, is_local)
        game.seats[0] = token
        self._games[game.id] = game
        self._by_token[token] = game.id
        return game

    # ---- connections coming and going ----

    def reseat(self, game, token, claimed_symbol, still_connected=()):
        """Put a reconnecting player back in their seat. Returns the seat.

        Trusts the symbol the client reports; falls back to whichever seat has no
        live connection.
        """
        seat = game.seat_for_symbol(claimed_symbol)
        if seat is None:
            seat = 0 if game.seats[0] not in still_connected else 1
        game.seats[seat] = token
        self._by_token[token] = game.id
        return seat

    def release(self, token):
        """Forget a connection. Returns the game it was seated in, or None."""
        game_id = self._by_token.pop(token, None)
        self.leave_queue(token)
        return self._games.get(game_id) if game_id else None

    def forget(self, game_id):
        """Drop a finished or abandoned game."""
        game = self._games.pop(game_id, None)
        if game:
            for token in game.seats:
                if token is not None and self._by_token.get(token) == game_id:
                    del self._by_token[token]
        return game

    # ---- matchmaking ----

    def is_queued(self, token):
        return any(entry["token"] == token for entry in self._queue)

    def join_queue(self, token, time_control):
        self._queue.append({"token": token, "time": time.time(), "timeControl": time_control})

    def leave_queue(self, token):
        self._queue = [entry for entry in self._queue if entry["token"] != token]

    def take_waiting(self, time_control):
        """Pull someone off the queue who wants the same time control, or None."""
        for i, entry in enumerate(self._queue):
            if entry["timeControl"] == time_control:
                return self._queue.pop(i)["token"]
        return None


store = GameStore()
