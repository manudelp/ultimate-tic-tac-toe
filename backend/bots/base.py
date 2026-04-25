"""Base class for all bot agents."""


class BaseAgent:
    id: int = -1
    name: str = "Unnamed"
    icon: str = "?"
    description: str = ""
    difficulty: int = 0

    def __init__(self):
        self.moveNumber = 0
        self.loaded_up = False

    def __str__(self):
        return f"{self.name}{self.icon}"

    def reset(self):
        self.moveNumber = 0

    def load(self):
        print(f"Loading {self.name}...")
        self.moveNumber = 0
        self.loaded_up = True

    def action(self, board, board_to_play=None):
        raise NotImplementedError
