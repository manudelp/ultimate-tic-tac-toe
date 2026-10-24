"""Play random games on our engine and on uttt.ai's engine. They must agree."""
import random
import sys

import numpy as np

from arena.codec import engine_to_state, features_from_state, move_to_index
from arena.paths import UTTTAI_ROOT
from core.engine import GameEngine


def _oracle():
    if not (UTTTAI_ROOT / "utttpy").is_dir():
        raise SystemExit(
            f"Missing {UTTTAI_ROOT}. Run scripts/fetch_utttai.sh first."
        )
    root = str(UTTTAI_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    from utttpy.game.action import Action
    from utttpy.game.helpers import get_state_ndarray_4x9x9
    from utttpy.game.ultimate_tic_tac_toe import UltimateTicTacToe

    return UltimateTicTacToe, Action, get_state_ndarray_4x9x9


def verify(games=200, seed=0):
    UltimateTicTacToe, Action, get_state_ndarray_4x9x9 = _oracle()
    rng = random.Random(seed)
    for game_index in range(games):
        ours = GameEngine(time_per_player=None)
        his = UltimateTicTacToe()
        moves = []
        while True:
            _assert_same(ours, his, get_state_ndarray_4x9x9, moves)
            if ours.status != "ongoing":
                break
            legal = ours.get_legal_moves()
            if not legal:
                raise AssertionError(f"no legal moves in an ongoing game after {moves}")
            move = legal[rng.randrange(len(legal))]
            moves.append(move)
            symbol = 1 if ours.active_player == 1 else 2
            ok, err = ours.make_move(ours.active_player, *move)
            if not ok:
                raise AssertionError(f"our engine rejected {move}: {err}")
            his.execute(Action(symbol=symbol, index=move_to_index(*move)))
        if (game_index + 1) % 50 == 0:
            print(f"rules agree through {game_index + 1} games")
    print(f"{games} random games matched uttt.ai, including the 4x9x9 features")
    return games


def _assert_same(ours, his, get_state_ndarray_4x9x9, moves):
    state = engine_to_state(ours)
    if state != his.state:
        raise AssertionError(
            f"state diverged after {moves}\nours={list(state)}\nhis ={list(his.state)}"
        )
    our_legal = {move_to_index(*move) for move in ours.get_legal_moves()}
    his_legal = set(his.get_legal_indexes())
    if our_legal != his_legal:
        raise AssertionError(
            f"legal moves diverged after {moves}\nours={sorted(our_legal)}\nhis={sorted(his_legal)}"
        )
    our_features = features_from_state(state)
    his_features = get_state_ndarray_4x9x9(his)
    if not np.array_equal(our_features, his_features):
        raise AssertionError(f"feature planes diverged after {moves}")
    if ours.status == "ongoing" and his.is_terminated():
        raise AssertionError(f"he finished and we did not, after {moves}")
    if ours.status != "ongoing" and not his.is_terminated():
        raise AssertionError(f"we finished and he did not, after {moves}")
    if ours.status == "won":
        expected = 1 if ours.winner == 1 else 2
        if his.result != expected:
            raise AssertionError(f"winner mismatch after {moves}: {ours.winner} vs {his.result}")
    elif ours.status == "draw" and not his.is_result_draw():
        raise AssertionError(f"draw mismatch after {moves}")
