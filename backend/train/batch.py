"""Turn parsed datapoints into a training batch, with square symmetries."""
import random

import numpy as np
import torch

from arena.codec import col_index, features_from_state, row_index


def datapoint_to_sample(datapoint):
    indexes, probability, action_value = datapoint["actions"]
    policy_mask = np.zeros((9, 9), dtype=bool)
    policy_targets = np.zeros((9, 9), dtype=np.float32)
    action_values = np.zeros((9, 9), dtype=np.float32)
    for i, action_index in enumerate(indexes):
        r, c = row_index(int(action_index)), col_index(int(action_index))
        policy_mask[r, c] = True
        policy_targets[r, c] = probability[i]
        action_values[r, c] = action_value[i]
    return {
        "input": features_from_state(datapoint["state"]),
        "policy_mask": policy_mask,
        "policy_targets": policy_targets,
        "action_values": action_values,
        "state_value": np.float32(datapoint["value"]),
    }


def random_orientation(sample, rng):
    """Flips and a transpose. The dihedral group keeps Ultimate Tic-Tac-Toe legal."""
    if rng.randrange(2):
        _flip(sample, axis=1)
    if rng.randrange(2):
        _flip(sample, axis=2)
    if rng.randrange(2):
        sample["input"] = np.swapaxes(sample["input"], 1, 2)
        for key in ("policy_mask", "policy_targets", "action_values"):
            sample[key] = np.swapaxes(sample[key], 0, 1)


def _flip(sample, axis):
    sample["input"] = np.flip(sample["input"], axis)
    target_axis = axis - 1
    for key in ("policy_mask", "policy_targets", "action_values"):
        sample[key] = np.flip(sample[key], target_axis)


def collate(samples, device):
    inputs = torch.from_numpy(np.stack([s["input"] for s in samples]).copy()).to(device=device, dtype=torch.float32)
    return {
        "inputs": inputs,
        "targets": {
            "policy_mask": torch.from_numpy(np.stack([s["policy_mask"] for s in samples]).copy()).to(device),
            "policy_targets": torch.from_numpy(np.stack([s["policy_targets"] for s in samples]).copy()).to(device),
            "action_values": torch.from_numpy(np.stack([s["action_values"] for s in samples]).copy()).to(device),
            "state_value": torch.tensor([s["state_value"] for s in samples], dtype=torch.float32, device=device),
        },
    }


def make_batch(datapoints, device, rng=None):
    rng = rng or random.Random()
    samples = []
    for datapoint in datapoints:
        sample = datapoint_to_sample(datapoint)
        random_orientation(sample, rng)
        samples.append(sample)
    return collate(samples, device)
