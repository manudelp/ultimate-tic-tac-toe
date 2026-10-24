"""Masked cross-entropy on the visit distribution, plus two MSE heads."""
import torch
import torch.nn.functional as F


def policy_value_loss(
    policy_logits,
    action_values,
    state_value,
    targets,
    policy_weight=1.0,
    action_weight=1.0,
    value_weight=1.0,
):
    mask = targets["policy_mask"]
    logits = policy_logits.masked_fill(~mask, -1e9)
    log_probs = F.log_softmax(logits.flatten(1), dim=-1).view_as(policy_logits)
    policy_loss = -(targets["policy_targets"] * log_probs).sum(dim=(1, 2)).mean()

    if mask.any():
        action_loss = (action_values - targets["action_values"])[mask].pow(2).mean()
    else:
        action_loss = policy_logits.new_zeros(())
    value_loss = F.mse_loss(state_value, targets["state_value"])
    total = (
        policy_weight * policy_loss
        + action_weight * action_loss
        + value_weight * value_loss
    )
    return total, {
        "policy": float(policy_loss.detach()),
        "action": float(action_loss.detach()),
        "value": float(value_loss.detach()),
    }
