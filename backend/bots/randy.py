import random
import numpy as np
from bots.base import BaseAgent
from core.board_utils import is_playable, get_playable_boards, random_move


class RandomAgent(BaseAgent):
    id = 0
    name = "Randy"
    icon = "🎲"
    description = "Randy is a wild card! He plays like he's throwing darts blindfolded. Don't expect strategy, just chaos and fun!"
    difficulty = 1

    def action(self, board, board_to_play=None):
        board = np.array(board, dtype=int)

        if board_to_play is None:
            playable = get_playable_boards(board)
            if not playable:
                raise ValueError("Randy couldn't find a playable board!")
            i, j = random.choice(playable)
            c, d = random_move(board[i, j])
            self.moveNumber += 1
            return i, j, c, d

        a, b = board_to_play
        if not is_playable(board[a, b]):
            raise ValueError(f"Randy: Board to play ({a},{b}) is not playable!")

        c, d = random_move(board[a, b])
        self.moveNumber += 1
        return a, b, c, d
