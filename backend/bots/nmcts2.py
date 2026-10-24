"""Arky: NMCTS2, the network Arkadiusz Nowaczyński deploys on uttt.ai.

Apache License 2.0. See backend/NOTICE and backend/licenses/utttai-Apache-2.0.txt.
The search follows his NeuralMonteCarloTreeSearch: PUCT with exploration 2.0,
priors floored at 0.01, softmax over legal logits, values negated on the way
up, and the most-visited root move. Children are only materialized when the
search first walks into them, and network outputs are cached by position.

Boards are 9 base-3 sub-board indexes in absolute colors: digit 1 is X,
digit 2 is O. Side to move is 1 (X) or 2 (O).
"""
import math
import os
import random
import time

import numpy as np

from bots.base import BaseAgent
from core import rules
from core.rules import OVER, P3 as _P3

_WEIGHTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "weights",
    "policy_value_net_stage2.onnx",
)
_CACHE_LIMIT = 200_000

_planes = None


def _load_planes():
    """Per sub-board index: 3x3 masks of X stones, O stones, and empty cells."""
    global _planes
    if _planes is None:
        size = 3 ** 9
        digits = np.array([[(i // _P3[c]) % 3 for c in range(9)] for i in range(size)], dtype=np.int8)
        digits = digits.reshape(size, 3, 3)
        _planes = (
            (digits == 1).astype(np.float32),
            (digits == 2).astype(np.float32),
            (digits == 0).astype(np.float32),
        )
    return _planes


class _Node:
    __slots__ = ("subs", "side", "btp", "terminal", "moves", "priors", "children", "visits", "value_sum")

    def __init__(self, subs, side, btp, terminal):
        self.subs = subs
        self.side = side
        self.btp = btp
        self.terminal = terminal
        self.moves = None
        self.priors = None
        self.children = None
        self.visits = 0
        self.value_sum = 0.0


class Nmcts2Agent(BaseAgent):
    id = 4
    name = "Arky"
    icon = "🦊"
    description = "Arky plays Arkadiusz Nowaczyński's NMCTS2, the network behind uttt.ai."
    difficulty = 5

    def __init__(self):
        super().__init__()
        self.max_sims = 1000
        self.time_limit = 2.0
        self.exploration = 2.0
        self.threads = 2
        self._session = None
        self._cache = {}

    def load(self):
        super().load()
        if not os.path.isfile(_WEIGHTS):
            raise FileNotFoundError(
                f"NMCTS2 weights not found at {_WEIGHTS}. "
                "Download https://uttt.ai/policy_value_net_stage2.onnx to that path."
            )
        import onnxruntime as ort

        options = ort.SessionOptions()
        options.intra_op_num_threads = self.threads
        options.inter_op_num_threads = 1
        self._session = ort.InferenceSession(_WEIGHTS, options, providers=["CPUExecutionProvider"])
        self._input = self._session.get_inputs()[0].name
        self._planes = _load_planes()

    def reset(self):
        """Drop the evaluation cache; a new game rarely revisits the old one."""
        self._cache.clear()

    def choose(self, position):
        if self._session is None:
            self.load()
        started = time.perf_counter()
        root = self._root(position)
        if root.terminal is not None:
            raise RuntimeError("Arky was asked to move in a finished game")
        deadline = started + self.time_limit
        sims = 0
        while sims < 2 or (sims < self.max_sims and time.perf_counter() < deadline):
            self._simulate(root)
            sims += 1

        top = 0
        best = []
        for i, child in enumerate(root.children):
            visits = child.visits if child is not None else 0
            if visits > top:
                top = visits
                best = [i]
            elif visits == top:
                best.append(i)
        sub, cell = root.moves[random.choice(best)]
        move = (sub // 3, sub % 3, cell // 3, cell % 3)
        elapsed = time.perf_counter() - started
        print(f"Arky {sims} sims in {elapsed:.2f}s -> {move}")
        return move

    def _root(self, position):
        """core.rules and Arky agree on the encoding: digit 1 is X, digit 2 is O.

        Only the side to move is spelled differently, +1/-1 against 1/2.
        """
        side = 1 if position.mover == 1 else 2
        return _Node(position.subs, side, position.forced, self._result(position.subs))

    def _result(self, subs):
        """None while the game is on, 0 for a draw, 1 or 2 for the winner's digit.

        core.rules speaks in +1/-1; Arky's states are absolute, so X is 1 and O is 2.
        """
        status, winner = rules.outcome(subs)
        if status == "ongoing":
            return None
        if status == "draw":
            return 0
        return 1 if winner == 1 else 2

    def _legal(self, node):
        return rules.legal_cells(node.subs, node.btp)

    def _child(self, node, index):
        sub, cell = node.moves[index]
        subs = list(node.subs)
        subs[sub] += node.side * _P3[cell]
        btp = rules.forced_sub_after(subs, cell)
        child = _Node(tuple(subs), 3 - node.side, btp, self._result(subs))
        node.children[index] = child
        return child

    def _simulate(self, root):
        path = [root]
        node = root
        while node.children is not None:
            sqrt_parent = math.sqrt(node.visits)
            c = self.exploration
            top = -math.inf
            choices = []
            for i, child in enumerate(node.children):
                prior = node.priors[i]
                if prior < 0.01:
                    prior = 0.01
                if child is None:
                    score = c * prior * sqrt_parent
                else:
                    q = -child.value_sum / child.visits if child.visits else 0.0
                    score = q + c * prior * sqrt_parent / (child.visits + 1)
                if score > top:
                    top = score
                    choices = [i]
                elif score == top:
                    choices.append(i)
            i = random.choice(choices)
            child = node.children[i]
            if child is None:
                child = self._child(node, i)
            node = child
            path.append(node)

        if node.terminal is None:
            value = self._expand(node)
        elif node.terminal == 0:
            value = 0.0
        else:
            value = -1.0

        for item in reversed(path):
            item.visits += 1
            item.value_sum += value
            value = -value

    def _expand(self, node):
        key = (node.subs, node.side, node.btp)
        cached = self._cache.get(key)
        if cached is None:
            moves = self._legal(node)
            logits, value = self._evaluate(node)
            scores = np.array(
                [logits[3 * (sub // 3) + cell // 3, 3 * (sub % 3) + cell % 3] for sub, cell in moves],
                dtype=np.float64,
            )
            scores -= scores.max()
            priors = np.exp(scores)
            priors /= priors.sum()
            cached = (moves, priors.tolist(), value)
            if len(self._cache) >= _CACHE_LIMIT:
                self._cache.clear()
            self._cache[key] = cached
        moves, priors, value = cached
        node.moves = moves
        node.priors = priors
        node.children = [None] * len(moves)
        return value

    def _evaluate(self, node):
        x_mask, o_mask, empty_mask = self._planes
        own, other = (x_mask, o_mask) if node.side == 1 else (o_mask, x_mask)
        features = np.zeros((1, 4, 9, 9), dtype=np.float32)
        features[0, 2] = 1.0 if node.side == 1 else -1.0
        over = OVER
        for sub in range(9):
            index = node.subs[sub]
            r = 3 * (sub // 3)
            c = 3 * (sub % 3)
            features[0, 0, r:r + 3, c:c + 3] = own[index]
            features[0, 1, r:r + 3, c:c + 3] = other[index]
            if (node.btp == sub) or (node.btp is None and not over[index]):
                features[0, 3, r:r + 3, c:c + 3] = empty_mask[index]
        logits, value = self._session.run(None, {self._input: features})
        return logits[0], float(np.asarray(value).reshape(-1)[0])
