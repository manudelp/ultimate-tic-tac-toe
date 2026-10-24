"""Base class for all bot agents.

A bot answers one question: given a Position, which move? The position carries
whose turn it is, so an agent never has to be told and a caller never has to
flip a board. Agents hold no per-game state, so one instance serves every game.
"""


class BaseAgent:
    id: int = -1
    name: str = "Unnamed"
    icon: str = "?"
    description: str = ""

    def __init__(self):
        self.loaded_up = False

    def __str__(self):
        return f"{self.name}{self.icon}"

    def load(self):
        """Read whatever the agent needs off disk. Safe to call twice."""
        print(f"Loading {self.name}...")
        self.loaded_up = True

    def reset(self):
        """Drop anything cached between games. Nothing to drop by default."""

    def choose(self, position):
        """Return the chosen move as (row, col, local_row, local_col)."""
        raise NotImplementedError
