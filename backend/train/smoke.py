"""CPU check that the parser, features, and one backward step hang together.

Does not train the real net. Run from backend/:

    uv run --with torch python -m train.smoke
"""
from arena.codec import features_from_state
from train.dataset import parse_nmcts_line


def synthetic_line():
    cells = ["0"] * 93
    cells[90] = "1"
    cells[91] = "9"
    state = "".join(cells)
    return (
        f"evaluatedState{{{state} 10 0.5}} "
        "evaluatedActions{1 40 8 0.25,1 41 2 -0.1}"
    )


def check_parser():
    datapoint = parse_nmcts_line(synthetic_line())
    if abs(datapoint["value"] - 0.5) > 1e-6:
        raise SystemExit(f"value parsed as {datapoint['value']}")
    indexes, probability, _ = datapoint["actions"]
    if list(indexes) != [40, 41]:
        raise SystemExit(f"indexes parsed as {list(indexes)}")
    if abs(float(probability.sum()) - 1.0) > 1e-5:
        raise SystemExit(f"probabilities sum to {probability.sum()}")
    features = features_from_state(datapoint["state"])
    if features.shape != (4, 9, 9):
        raise SystemExit(f"features shape {features.shape}")
    if int(features[3].sum()) != 81 or int(features[2, 0, 0]) != 1:
        raise SystemExit("empty-board features are wrong")
    print("parser and empty-board features ok")
    return datapoint


def check_backward(datapoint):
    import torch

    from train.batch import make_batch
    from train.loss import policy_value_loss
    from train.model import PolicyValueNet, parameter_count

    full = PolicyValueNet()
    print(f"default net parameters: {parameter_count(full):,}")
    del full

    torch.manual_seed(0)
    net = PolicyValueNet(channels=32, blocks=2)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    batch = make_batch([datapoint] * 4, device=torch.device("cpu"))
    net.train()
    losses = []
    for _ in range(2):
        opt.zero_grad()
        logits, action_values, state_value = net(batch["inputs"])
        loss, parts = policy_value_loss(logits, action_values, state_value, batch["targets"])
        if not torch.isfinite(loss):
            raise SystemExit(f"non-finite loss {loss}")
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
        print(f"smoke loss {losses[-1]:.4f}  {parts}")
    print("backward step ok")


def main():
    datapoint = check_parser()
    try:
        import torch  # noqa: F401
    except ImportError:
        print("torch is not installed. Parser is ready. The backward check waits for torch.")
        return
    check_backward(datapoint)


if __name__ == "__main__":
    main()
