import random

from bots.base import BaseAgent


class RandomAgent(BaseAgent):
    id = 0
    name = "Randy"
    icon = "🎲"
    description = "Randy is a wild card! He plays like he's throwing darts blindfolded. Don't expect strategy, just chaos and fun!"
    difficulty = 1

    def choose(self, position):
        moves = position.legal_moves()
        if not moves:
            raise ValueError("Randy was asked to move in a finished game")
        sub, cell = random.choice(moves)
        return sub // 3, sub % 3, cell // 3, cell % 3
