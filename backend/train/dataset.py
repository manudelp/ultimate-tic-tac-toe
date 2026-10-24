"""Read uttt.ai self-play lines.

NMCTS line, from his datasets/README:

    evaluatedState{STATE VISIT_COUNT STATE_VALUE_MEAN} evaluatedActions{SYMBOL INDEX VISIT_COUNT STATE_VALUE_MEAN, ...}

STATE is 93 digits. Action probabilities are visit counts, normalized here.
"""
import pathlib
import re

import numpy as np

_STATE = re.compile(r"evaluatedState\{(.*?)\}")
_ACTIONS = re.compile(r"evaluatedActions\{(.*?)\}")


def parse_nmcts_line(line):
    state_match = _STATE.search(line)
    action_match = _ACTIONS.search(line)
    if state_match is None or action_match is None:
        raise ValueError("not an NMCTS datapoint")
    state_fields = state_match.group(1).split(" ")
    state = bytearray(map(int, state_fields[0]))
    if len(state) != 93:
        raise ValueError(f"state length {len(state)}, expected 93")
    value = float(state_fields[2])
    parts = [part for part in action_match.group(1).split(",") if part]
    indexes = np.zeros(len(parts), dtype=np.int32)
    probability = np.zeros(len(parts), dtype=np.float32)
    action_value = np.zeros(len(parts), dtype=np.float32)
    for i, part in enumerate(parts):
        fields = part.split(" ")
        indexes[i] = int(fields[1])
        probability[i] = int(fields[2])
        action_value[i] = float(fields[3])
    total = float(probability.sum())
    if total <= 0:
        raise ValueError("action visits sum to 0")
    probability /= total
    return {
        "state": state,
        "value": value,
        "actions": (indexes, probability, action_value),
    }


def iter_nmcts_file(path):
    path = pathlib.Path(path)
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield parse_nmcts_line(line)


def list_depth_files(directory):
    directory = pathlib.Path(directory)
    files = sorted(directory.glob("depth*.txt"))
    if not files:
        raise FileNotFoundError(f"no depth*.txt under {directory}")
    return files
