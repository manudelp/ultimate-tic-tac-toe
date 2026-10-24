"""Train the policy-value net on a stage-2 directory of depth*.txt files.

This is the command for the 5080. It refuses to start a real run on CPU.

    uv run --with torch python -m train.run \\
        --dataset ../datasets/stage2-nmcts \\
        --steps 100000 \\
        --device cuda
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch

from arena.paths import DATASETS_URL, RUNS_DIR, STAGE2_DATASET
from train.batch import make_batch
from train.dataset import iter_nmcts_file, list_depth_files
from train.loss import policy_value_loss
from train.model import PolicyValueNet, parameter_count


def load_dataset(directory, max_per_depth=None):
    """One list per depth file. Sampling draws depths uniformly, as his trainer does."""
    groups = []
    total = 0
    for path in list_depth_files(directory):
        rows = []
        for datapoint in iter_nmcts_file(path):
            rows.append(datapoint)
            if max_per_depth is not None and len(rows) >= max_per_depth:
                break
        if rows:
            groups.append(rows)
            total += len(rows)
            print(f"loaded {len(rows):>8}  {path.name}")
    if not groups:
        raise SystemExit(f"no datapoints under {directory}")
    print(f"loaded {total} datapoints in {len(groups)} depth groups")
    return groups


def sample_batch(groups, batch_size, rng):
    picked = []
    for _ in range(batch_size):
        group = groups[rng.randrange(len(groups))]
        picked.append(group[rng.randrange(len(group))])
    return picked


def save_checkpoint(path, net, step):
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "step": step,
            "channels": net.channels,
            "blocks": net.blocks,
            "state_dict": net.state_dict(),
        },
        path,
    )


def main():
    parser = argparse.ArgumentParser(description="Train a policy-value net past NMCTS2")
    parser.add_argument("--dataset", type=Path, default=STAGE2_DATASET)
    parser.add_argument("--out", type=Path, default=RUNS_DIR / "nmcts3")
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--channels", type=int, default=256)
    parser.add_argument("--blocks", type=int, default=12)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--allow-cpu", action="store_true")
    parser.add_argument("--max-per-depth", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=50)
    parser.add_argument("--save-every", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit(
            "No CUDA GPU is visible. Training waits for the 5080. "
            "A one-batch CPU check is `python -m train.smoke`."
        )
    if args.device == "cpu" and not args.allow_cpu:
        raise SystemExit("Refusing a CPU training run. Pass --allow-cpu to override.")
    if not args.dataset.is_dir():
        raise SystemExit(
            f"Dataset directory not found: {args.dataset}\n"
            f"Download stage2-nmcts from {DATASETS_URL} and unpack the depth*.txt files there."
        )

    rng = random.Random(args.seed)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device(args.device)
    groups = load_dataset(args.dataset, max_per_depth=args.max_per_depth)
    net = PolicyValueNet(channels=args.channels, blocks=args.blocks).to(device)
    print(f"parameters: {parameter_count(net):,}  device: {device}")
    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler(device.type, enabled=use_amp)
    args.out.mkdir(parents=True, exist_ok=True)
    history = []
    net.train()
    started = time.time()
    for step in range(1, args.steps + 1):
        batch = make_batch(sample_batch(groups, args.batch_size, rng), device, rng)
        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast(device.type, enabled=use_amp):
            logits, action_values, state_value = net(batch["inputs"])
            loss, parts = policy_value_loss(logits, action_values, state_value, batch["targets"])
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        if step % args.log_every == 0 or step == 1:
            elapsed = time.time() - started
            loss_value = float(loss.detach())
            print(
                f"step {step}  loss {loss_value:.4f}  "
                f"policy {parts['policy']:.4f}  action {parts['action']:.4f}  "
                f"value {parts['value']:.4f}  {elapsed:.0f}s"
            )
            history.append({"step": step, "loss": loss_value, **parts})
        if step % args.save_every == 0 or step == args.steps:
            save_checkpoint(args.out / f"policy_value_net_{step}.pt", net, step)
            (args.out / "loss_history.json").write_text(json.dumps(history, indent=2))
            print(f"saved {args.out / f'policy_value_net_{step}.pt'}")


if __name__ == "__main__":
    main()
