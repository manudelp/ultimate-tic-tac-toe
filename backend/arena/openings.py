"""The 50 positions uttt.ai uses to score two engines."""
import sys

from arena.codec import engine_from_state, engine_to_state
from arena.paths import UTTTAI_ROOT


def evaluation_states():
    root = str(UTTTAI_ROOT)
    if not (UTTTAI_ROOT / "utttpy").is_dir():
        raise SystemExit(f"Missing {UTTTAI_ROOT}. Run scripts/fetch_utttai.sh first.")
    if root not in sys.path:
        sys.path.insert(0, root)
    from utttpy.selfplay.evaluation_uttt_states import EVALUATION_UTTT_STATES

    return list(EVALUATION_UTTT_STATES)


def check_evaluation_states():
    """Every published opening must survive a trip through our engine."""
    for index, digits in enumerate(evaluation_states()):
        raw = bytearray(map(int, digits))
        encoded = engine_to_state(engine_from_state(digits))
        if encoded != raw:
            raise AssertionError(
                f"opening {index} diverged\nours={list(encoded)}\nhis ={list(raw)}"
            )
    return len(evaluation_states())
