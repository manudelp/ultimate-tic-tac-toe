"""Players the arena can seat."""
import importlib

import numpy as np

from arena.codec import engine_to_state, index_to_move
from core.position import Position
from arena.paths import (
    NMCTS2_ONNX,
    NMCTS2_ONNX_URL,
    NMCTS2_WEIGHTS,
    UTTTAI_ROOT,
    WEIGHTS_URL,
)


_BOTS = {
    "randy": ("bots.randy", "RandomAgent"),
    "0": ("bots.randy", "RandomAgent"),
    "greedy": ("bots.greedy", "GreedyAgent"),
    "1": ("bots.greedy", "GreedyAgent"),
    "jardinerito": ("bots.jardito", "JardineritoAgent"),
    "2": ("bots.jardito", "JardineritoAgent"),
    "arky": ("bots.nmcts2", "Nmcts2Agent"),
    "4": ("bots.nmcts2", "Nmcts2Agent"),
    "jardinero": ("bots.jardishow", "JardiShowAgent"),
    "3": ("bots.jardishow", "JardiShowAgent"),
}


class BotPlayer:
    def __init__(self, agent):
        self.agent = agent
        self.name = agent.name

    def reset(self):
        self.agent.reset()

    def move(self, engine):
        a, b, c, d = self.agent.choose(Position.from_engine(engine))
        return int(a), int(b), int(c), int(d)


class Nmcts2Player:
    """The network deployed on uttt.ai, searched with his Python MCTS.

    Uses the ONNX file from the site when it is present. A PyTorch state
    dict at backend/weights/nmcts2.pt is the fallback.
    """

    name = "NMCTS2"

    def __init__(self, weights=None, simulations=1000, device="cpu", exploration=2.0):
        self.weights = weights
        self.simulations = simulations
        self.device_name = device
        self.exploration = exploration
        self._net = None
        self._search = None

    def reset(self):
        self._search = None

    def load(self):
        if self._net is not None:
            return
        if not (UTTTAI_ROOT / "utttpy").is_dir():
            raise FileNotFoundError(
                f"Missing {UTTTAI_ROOT}. Run scripts/fetch_utttai.sh first."
            )
        onnx_path = self.weights if self.weights and str(self.weights).endswith(".onnx") else NMCTS2_ONNX
        pt_path = self.weights if self.weights and not str(self.weights).endswith(".onnx") else NMCTS2_WEIGHTS
        if onnx_path.is_file():
            from arena.onnx_net import OnnxPolicyValue

            self._net = OnnxPolicyValue(onnx_path)
            self._net.eval()
            return
        if not pt_path.is_file():
            raise FileNotFoundError(
                "NMCTS2 weights are missing. Either download "
                f"{NMCTS2_ONNX_URL} to {NMCTS2_ONNX}, or save a stage-2 state dict "
                f"from {WEIGHTS_URL} at {NMCTS2_WEIGHTS}."
            )
        import torch
        import sys

        root_str = str(UTTTAI_ROOT)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        from utttpy.selfplay.policy_value_network import PolicyValueNetwork

        if self.device_name == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested for NMCTS2 and no GPU is visible.")
        device = torch.device(self.device_name)
        net = PolicyValueNetwork()
        net.to(device)
        try:
            state = torch.load(pt_path, map_location=device, weights_only=True)
        except TypeError:
            state = torch.load(pt_path, map_location=device)
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        net.load_state_dict(state)
        net.eval()
        self._net = net

    def move(self, engine):
        self.load()
        import sys
        root_str = str(UTTTAI_ROOT)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        from utttpy.game.ultimate_tic_tac_toe import UltimateTicTacToe
        from utttpy.selfplay.neural_monte_carlo_tree_search import (
            NeuralMonteCarloTreeSearch,
        )

        uttt = UltimateTicTacToe(state=engine_to_state(engine))
        if self._search is None:
            self._search = NeuralMonteCarloTreeSearch(
                uttt=uttt,
                num_simulations=self.simulations,
                exploration_strength=self.exploration,
                policy_value_net=self._net,
            )
        else:
            self._search.synchronize(uttt)
        self._search.run(progress_bar=False)
        selected = self._search.select_action(self._search.get_evaluated_actions(), "argmax")
        return index_to_move(selected.index)


def make_player(name, simulations=1000, device="cpu"):
    key = name.lower()
    if key in {"nmcts2", "uttt"}:
        player = Nmcts2Player(simulations=simulations, device=device)
        player.load()
        return player
    if key not in _BOTS:
        known = "randy, greedy, jardinerito, jardinero, arky, nmcts2"
        raise SystemExit(f"Unknown player {name!r}. Known: {known}")
    module_name, class_name = _BOTS[key]
    module = importlib.import_module(module_name)
    agent = getattr(module, class_name)()
    agent.load()
    return BotPlayer(agent)
