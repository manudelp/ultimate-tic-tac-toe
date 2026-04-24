import numpy as np
import time
import uuid
from utils import get_board_results, get_winner


def _is_won(board):
    """Check if a 3x3 board is won. Returns 1, -1, or 0."""
    for i in range(3):
        if board[i, 0] == board[i, 1] == board[i, 2] != 0:
            return int(board[i, 0])
        if board[0, i] == board[1, i] == board[2, i] != 0:
            return int(board[0, i])
    if board[0, 0] == board[1, 1] == board[2, 2] != 0:
        return int(board[0, 0])
    if board[0, 2] == board[1, 1] == board[2, 0] != 0:
        return int(board[0, 2])
    return 0


def _is_full(board):
    return np.all(board != 0)


def _is_playable(board):
    return not _is_full(board) and _is_won(board) == 0


class GameEngine:
    """Server-authoritative Ultimate Tic-Tac-Toe game."""

    def __init__(self, time_per_player=300):
        self.id = str(uuid.uuid4())[:8]
        self.board = np.zeros((3, 3, 3, 3), dtype=int)
        self.active_player = 1  # 1 = X, -1 = O
        self.forced_board = None  # (row, col) or None = free choice
        self.status = "ongoing"  # ongoing | won | draw
        self.winner = None
        self.moves = []
        self.clocks = {1: time_per_player, -1: time_per_player}
        self.last_move_time = None
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
                "X": round(self.clocks[1], 1),
                "O": round(self.clocks[-1], 1),
            },
            "boardResults": self._board_results().tolist(),
        }

    def start(self):
        """Start the clock."""
        self.last_move_time = time.time()

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
        if not _is_playable(sub):
            return False, "Board is not playable"

        # Validate cell is empty
        if self.board[a, b, c, d] != 0:
            return False, "Cell is occupied"

        # Update clock
        now = time.time()
        if self.last_move_time:
            elapsed = now - self.last_move_time
            self.clocks[player] -= elapsed
            if self.clocks[player] <= 0:
                self.clocks[player] = 0
                self.status = "won"
                self.winner = -player  # opponent wins on timeout
                return False, "Time expired"
        self.last_move_time = now

        # Apply move
        self.board[a, b, c, d] = player
        self.moves.append({
            "player": "X" if player == 1 else "O",
            "move": [a, b, c, d],
            "time": round(now - self.created_at, 2),
        })

        # Compute next forced board
        target = self.board[c, d]
        if _is_playable(target):
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
                    if _is_playable(self.board[a, b]):
                        sub = self.board[a, b]
                        for c in range(3):
                            for d in range(3):
                                if sub[c, d] == 0:
                                    moves.append((a, b, c, d))
        return moves

    def check_timeout(self):
        """Check if current player has timed out."""
        if self.status != "ongoing" or not self.last_move_time:
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
                results[i, j] = _is_won(self.board[i, j])
        return results

    def _is_draw(self):
        for a in range(3):
            for b in range(3):
                if _is_playable(self.board[a, b]):
                    return False
        return True
