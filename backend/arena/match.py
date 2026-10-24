"""Play two players through our engine. Colors swap every game."""
from arena.codec import engine_from_state
from core.engine import GameEngine


def play_game(first, second, state=None, engine=None):
    """`first` is X, `second` is O. Returns 1, -1, or 0.

    Starts from `engine` if given, else from a 93-byte `state`, else empty.
    """
    if engine is None:
        engine = GameEngine(time_per_player=None) if state is None else engine_from_state(state)
    first.reset()
    second.reset()
    seats = {1: first, -1: second}
    while engine.status == "ongoing":
        move = seats[engine.active_player].move(engine)
        ok, err = engine.make_move(engine.active_player, *move)
        if not ok:
            raise RuntimeError(f"{seats[engine.active_player].name} played {move}: {err}")
        if len(engine.moves) > 81:
            raise RuntimeError("game exceeded 81 plies")
    if engine.status == "draw":
        return 0
    return engine.winner


def play_match(player_a, player_b, games, seed=0):
    """`games` total. Player A is X on even games and O on odd games.

    Returns (wins for A, wins for B, draws).
    """
    del seed  # seating is deterministic; bots draw their own randomness
    wins_a = wins_b = draws = 0
    for game_index in range(games):
        if game_index % 2 == 0:
            winner = play_game(player_a, player_b)
            if winner == 1:
                wins_a += 1
            elif winner == -1:
                wins_b += 1
            else:
                draws += 1
        else:
            winner = play_game(player_b, player_a)
            if winner == -1:
                wins_a += 1
            elif winner == 1:
                wins_b += 1
            else:
                draws += 1
        print(
            f"game {game_index + 1}/{games}: "
            f"{player_a.name} {wins_a}  {player_b.name} {wins_b}  draws {draws}"
        )
    return wins_a, wins_b, draws


def play_openings(player_a, player_b, states):
    """Each state is played twice, with the players swapping colors.

    Returns (wins for A, wins for B, draws).
    """
    wins_a = wins_b = draws = 0
    total = len(states) * 2
    played = 0
    for state in states:
        for a_is_x in (True, False):
            played += 1
            if a_is_x:
                winner = play_game(player_a, player_b, state)
                if winner == 1:
                    wins_a += 1
                elif winner == -1:
                    wins_b += 1
                else:
                    draws += 1
            else:
                winner = play_game(player_b, player_a, state)
                if winner == -1:
                    wins_a += 1
                elif winner == 1:
                    wins_b += 1
                else:
                    draws += 1
            seat = "X" if a_is_x else "O"
            print(
                f"game {played}/{total} ({player_a.name} as {seat}): "
                f"{player_a.name} {wins_a}  {player_b.name} {wins_b}  draws {draws}"
            )
    return wins_a, wins_b, draws
