"""python -m arena verify | python -m arena play --x randy --o greedy"""
import argparse

from arena.match import play_match, play_openings
from arena.openings import check_evaluation_states, evaluation_states
from arena.players import make_player
from arena.verify_rules import verify


def main():
    parser = argparse.ArgumentParser(description="Arena against our bots and uttt.ai")
    sub = parser.add_subparsers(dest="cmd", required=True)

    verify_cmd = sub.add_parser("verify", help="check our rules against uttt.ai")
    verify_cmd.add_argument("--games", type=int, default=200)
    verify_cmd.add_argument("--seed", type=int, default=0)

    play_cmd = sub.add_parser("play", help="play a match, swapping colors each game")
    play_cmd.add_argument("--x", required=True, help="randy, greedy, jardinerito, jardinero, nmcts2")
    play_cmd.add_argument("--o", required=True)
    play_cmd.add_argument("--games", type=int, default=4)
    play_cmd.add_argument(
        "--openings",
        type=int,
        default=0,
        help="play this many of uttt.ai's evaluation positions, both colors",
    )
    play_cmd.add_argument("--simulations", type=int, default=1000)
    play_cmd.add_argument("--device", default="cpu")
    play_cmd.add_argument("--seed", type=int, default=0)

    args = parser.parse_args()
    if args.cmd == "verify":
        verify(games=args.games, seed=args.seed)
        return

    player_a = make_player(args.x, simulations=args.simulations, device=args.device)
    player_b = make_player(args.o, simulations=args.simulations, device=args.device)
    if args.openings:
        found = check_evaluation_states()
        states = evaluation_states()[: args.openings]
        print(f"using {len(states)} of {found} evaluation openings, both colors")
        wins_a, wins_b, draws = play_openings(player_a, player_b, states)
        played = len(states) * 2
    else:
        wins_a, wins_b, draws = play_match(player_a, player_b, games=args.games, seed=args.seed)
        played = args.games
    print(
        f"{player_a.name} {wins_a}  {player_b.name} {wins_b}  draws {draws}  "
        f"({played} games)"
    )


if __name__ == "__main__":
    main()
