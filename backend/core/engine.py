import numpy as np
import time
import uuid
from core.board_utils import is_won, is_full, is_playable
from core.hash_utils import get_board_results, get_winner


class GameEngine:
    """Server-authoritative Ultimate Tic-Tac-Toe game."""

    def __init__(self, time_per_player=300):
        self.id = uuid.uuid4().hex[:4].upper()
        self.board = np.zeros((3, 3, 3, 3), dtype=int)
        self.active_player = 1  # 1 = X, -1 = O
        self.forced_board = None  # (row, col) or None = free choice
        self.status = "ongoing"  # ongoing | won | draw
        self.winner = None
        self.moves = []
        self.time_per_player = time_per_player
        self.clocks = {1: time_per_player, -1: time_per_player} if time_per_player else None
        self.last_move_time = None
        self.clock_paused = False
        self.created_at = time.time()

    def to_dict(self):
        """Serialize full state for client."""
        return {
            "id": self.id,
            "board": self.board.tolist(),
            "activePlayer": "X" if self.active_player == 1 else "O",
            "forcedBoard": list(self.forced_board) if self.forced_board else None,
            "status": self.status,
            "winner": {1: "X", -1: "O"}.get(self.winner),
            "moves": self.moves,
            "clocks": {
                "X": round(self.clocks[1], 1) if self.clocks else None,
                "O": round(self.clocks[-1], 1) if self.clocks else None,
            },
            "boardResults": self._board_results().tolist(),
        }

    def start(self):
        """Start the clock."""
        self.last_move_time = time.time()

    def pause_clock(self):
        """Pause the clock (e.g. on disconnect). Commits elapsed time so far."""
        if not self.clocks or not self.last_move_time or self.clock_paused:
            return
        elapsed = time.time() - self.last_move_time
        self.clocks[self.active_player] = max(0, self.clocks[self.active_player] - elapsed)
        self.last_move_time = None
        self.clock_paused = True

    def resume_clock(self):
        """Resume the clock after a pause."""
        if not self.clocks or not self.clock_paused:
            return
        self.last_move_time = time.time()
        self.clock_paused = False

    def make_move(self, player, a, b, c, d):
        """
        Attempt a move. Returns (success, error_message).
        player: 1 or -1
        a, b: big board coords
        c, d: small board coords
        """
        if self.status != "ongoing":
            return False, "Game is over"

        if player != self.active_player:
            return False, "Not your turn"

        # Validate forced board
        if self.forced_board is not None:
            if (a, b) != self.forced_board:
                return False, f"Must play in board {self.forced_board}"

        # Validate board is playable
        sub = self.board[a, b]
        if not is_playable(sub):
            return False, "Board is not playable"

        # Validate cell is empty
        if self.board[a, b, c, d] != 0:
            return False, "Cell is occupied"

        # Update clock
        now = time.time()
        if self.clocks and self.last_move_time and not self.clock_paused:
            elapsed = now - self.last_move_time
            self.clocks[player] -= elapsed
            if self.clocks[player] <= 0:
                self.clocks[player] = 0
                self.status = "won"
                self.winner = -player  # opponent wins on timeout
                return False, "Time expired"
        self.last_move_time = now
        self.clock_paused = False

        # Apply move
        self.board[a, b, c, d] = player
        self.moves.append({
            "player": "X" if player == 1 else "O",
            "move": [a, b, c, d],
            "time": round(now - self.created_at, 2),
        })

        # Compute next forced board
        target = self.board[c, d]
        if is_playable(target):
            self.forced_board = (c, d)
        else:
            self.forced_board = None

        # Check game end
        results = self._board_results()
        game_winner = get_winner(results)
        if game_winner != 0:
            self.status = "won"
            self.winner = int(game_winner)
        elif self._is_draw():
            self.status = "draw"
        else:
            self.active_player = -player

        return True, None

    def get_legal_moves(self):
        """Return list of legal (a, b, c, d) tuples."""
        moves = []
        if self.forced_board:
            a, b = self.forced_board
            sub = self.board[a, b]
            for c in range(3):
                for d in range(3):
                    if sub[c, d] == 0:
                        moves.append((a, b, c, d))
        else:
            for a in range(3):
                for b in range(3):
                    if is_playable(self.board[a, b]):
                        sub = self.board[a, b]
                        for c in range(3):
                            for d in range(3):
                                if sub[c, d] == 0:
                                    moves.append((a, b, c, d))
        return moves

    def check_timeout(self):
        """Check if current player has timed out."""
        if self.status != "ongoing" or not self.last_move_time or not self.clocks or self.clock_paused:
            return False
        elapsed = time.time() - self.last_move_time
        remaining = self.clocks[self.active_player] - elapsed
        if remaining <= 0:
            self.clocks[self.active_player] = 0
            self.status = "won"
            self.winner = -self.active_player
            return True
        return False

    def _board_results(self):
        results = np.zeros((3, 3), dtype=int)
        for i in range(3):
            for j in range(3):
                results[i, j] = is_won(self.board[i, j])
        return results

    def _is_draw(self):
        for a in range(3):
            for b in range(3):
                if is_playable(self.board[a, b]):
                    return False
        return True
