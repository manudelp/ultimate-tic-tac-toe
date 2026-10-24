"""A position a bot is asked to move in.

Stones are absolute throughout: +1 is X, -1 is O. The position knows whose turn
it is, so nothing outside has to flip a board to hand it over. Agents that want
to think in "my stones are +1" ask for `mover_board()`, and that flip has one
implementation, here.

State is the nine base-3 sub-board indexes of core.rules, which makes playing a
move and asking who has won a table lookup rather than a scan.
"""
from core import rules
from core.rules import OVER, P3


class Position:
    """Immutable. `play` returns a new one."""

    __slots__ = ("subs", "mover", "forced", "_status", "_winner")

    def __init__(self, subs, mover, forced):
        self.subs = tuple(subs)
        self.mover = mover
        self.forced = forced
        self._status, self._winner = rules.outcome(self.subs)

    # ---- building ----

    @classmethod
    def from_engine(cls, engine):
        """The position the engine is waiting on.

        Once a game is over the engine leaves active_player on whoever played the
        last stone. A Position always names the side that would move next, so
        `mover` keeps the same meaning whether it came from an engine or `play`.
        """
        forced = (
            None if engine.forced_board is None
            else engine.forced_board[0] * 3 + engine.forced_board[1]
        )
        mover = engine.active_player if engine.status == "ongoing" else -engine.active_player
        return cls(rules.board_indexes(engine.board), mover, forced)

    @classmethod
    def from_board(cls, board, mover, forced_board=None):
        """From a 3x3x3x3 board of absolute stones plus whose turn it is.

        `forced_board` is (row, col) or None, matching GameEngine.forced_board.
        """
        forced = None if forced_board is None else forced_board[0] * 3 + forced_board[1]
        return cls(rules.board_indexes(board), mover, forced)

    # ---- asking ----

    @property
    def status(self):
        """ongoing, won, or draw."""
        return self._status

    @property
    def winner(self):
        """+1, -1, or None."""
        return self._winner

    @property
    def forced_board(self):
        """The forced sub-board as (row, col), or None. GameEngine's spelling."""
        return None if self.forced is None else divmod(self.forced, 3)

    @property
    def ply(self):
        """How many stones are on the board."""
        return 81 - sum(len(rules.EMPTIES[sub]) for sub in self.subs)

    def is_empty(self):
        return all(sub == 0 for sub in self.subs)

    def legal_moves(self):
        """Legal (sub, cell) pairs, both 0..8. Empty once the game is over."""
        if self._status != "ongoing":
            return []
        return rules.legal_cells(self.subs, self.forced)

    def mover_board(self):
        """A 3x3x3x3 board with the mover's own stones as +1.

        The one place the board is flipped for a bot's point of view.
        """
        import numpy as np

        board = np.zeros((3, 3, 3, 3), dtype=int)
        flat = board.reshape(9, 9)
        for sub in range(9):
            index = self.subs[sub]
            for cell in range(9):
                digit = (index // P3[cell]) % 3
                if digit:
                    flat[sub, cell] = self.mover if digit == 1 else -self.mover
        return board

    # ---- moving ----

    def play(self, sub, cell):
        """The position after the mover plays `cell` in sub-board `sub`."""
        subs = list(self.subs)
        subs[sub] += (1 if self.mover == 1 else 2) * P3[cell]
        return Position(subs, -self.mover, None if OVER[subs[cell]] else cell)

    def __repr__(self):
        side = "X" if self.mover == 1 else "O"
        where = "free" if self.forced is None else f"board {self.forced_board}"
        return f"<Position {side} to move, {where}, ply {self.ply}, {self._status}>"
