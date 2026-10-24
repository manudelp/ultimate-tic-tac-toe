"""Translate our 3x3x3x3 board into the 93-byte state uttt.ai trains on.

Layout, matching arnowaczynski/utttai (Apache-2.0):

- bytes 0..80: cells, row-major inside row-major sub-boards. 0 empty, 1 X, 2 O
- bytes 81..89: sub-board results. 0 open, 1 X, 2 O, 3 draw
- byte 90: side to move. 1 X, 2 O
- byte 91: forced sub-board 0..8, or 9 when the mover may choose
- byte 92: game result. 0 ongoing, 1 X won, 2 O won, 3 draw

The 4x9x9 feature stack is the one his policy-value net consumes:

- plane 0: side to move
- plane 1: the other side
- plane 2: +1 if X is to move, -1 if O is to move
- plane 3: legal cells
"""
import numpy as np

from core.position import Position
from core.rules import FULL, P3, WINNER

STATE_SIZE = 93
NEXT_SYMBOL = 90
CONSTRAINT = 91
RESULT = 92
X = 1
O = 2
DRAW = 3
UNCONSTRAINED = 9


def move_to_index(a, b, c, d):
    return (a * 3 + b) * 9 + c * 3 + d


def index_to_move(index):
    sub = index // 9
    cell = index % 9
    return sub // 3, sub % 3, cell // 3, cell % 3


def row_index(index):
    """Row on the flat 9x9 board."""
    return 3 * (index // 27) + (index % 9) // 3


def col_index(index):
    """Column on the flat 9x9 board."""
    return 3 * ((index // 9) % 3) + index % 3


def state_from_position(position):
    """Encode a Position as uttt.ai's 93-byte state."""
    state = bytearray(STATE_SIZE)
    for sub in range(9):
        index = position.subs[sub]
        base = sub * 9
        for cell in range(9):
            digit = (index // P3[cell]) % 3
            if digit:
                state[base + cell] = X if digit == 1 else O
        winner = WINNER[index]
        meta = 81 + sub
        if winner == 1:
            state[meta] = X
        elif winner == -1:
            state[meta] = O
        elif FULL[index]:
            state[meta] = DRAW

    state[NEXT_SYMBOL] = X if position.mover == 1 else O
    state[CONSTRAINT] = UNCONSTRAINED if position.forced is None else position.forced

    if position.status == "won":
        state[RESULT] = X if position.winner == 1 else O
    elif position.status == "draw":
        state[RESULT] = DRAW
    return state


def engine_to_state(engine):
    """Encode a GameEngine position as uttt.ai's 93-byte state."""
    return state_from_position(Position.from_engine(engine))


def _raw(state):
    raw = bytearray(map(int, state)) if isinstance(state, str) else bytearray(state)
    if len(raw) != STATE_SIZE:
        raise ValueError(f"state length {len(raw)}, expected {STATE_SIZE}")
    return raw


def position_from_state(state):
    """Read a 93-digit or 93-byte uttt.ai state as a Position."""
    raw = _raw(state)
    subs = [0] * 9
    for index in range(81):
        value = raw[index]
        if value:
            subs[index // 9] += (1 if value == X else 2) * P3[index % 9]
    mover = 1 if raw[NEXT_SYMBOL] == X else -1
    forced = None if raw[CONSTRAINT] == UNCONSTRAINED else raw[CONSTRAINT]
    return Position(subs, mover, forced)


def features_from_position(position):
    """The 4x9x9 stack his policy-value net consumes."""
    return features_from_state(state_from_position(position))


def engine_from_state(state):
    """Load a 93-digit uttt.ai state into a fresh GameEngine."""
    from core.engine import GameEngine

    raw = _raw(state)
    engine = GameEngine(time_per_player=None)
    for index in range(81):
        if raw[index] == 0:
            continue
        a, b, c, d = index_to_move(index)
        engine.board[a, b, c, d] = 1 if raw[index] == X else -1
    if raw[RESULT] == X:
        engine.status = "won"
        engine.winner = 1
        engine.active_player = -1 if raw[NEXT_SYMBOL] == X else 1
    elif raw[RESULT] == O:
        engine.status = "won"
        engine.winner = -1
        engine.active_player = -1 if raw[NEXT_SYMBOL] == X else 1
    elif raw[RESULT] == DRAW:
        engine.status = "draw"
        engine.active_player = -1 if raw[NEXT_SYMBOL] == X else 1
    else:
        engine.active_player = 1 if raw[NEXT_SYMBOL] == X else -1
    if raw[CONSTRAINT] == UNCONSTRAINED:
        engine.forced_board = None
    else:
        sub = raw[CONSTRAINT]
        engine.forced_board = (sub // 3, sub % 3)
    return engine


def features_from_state(state):
    """4x9x9 int8 stack. Same planes as utttpy.game.helpers.get_state_ndarray_4x9x9."""
    array = np.zeros((4, 9, 9), dtype=np.int8)
    next_is_x = state[NEXT_SYMBOL] == X
    own, other = (0, 1) if next_is_x else (1, 0)
    for index, value in enumerate(state[:81]):
        r, c = row_index(index), col_index(index)
        if value == X:
            array[own, r, c] = 1
        elif value == O:
            array[other, r, c] = 1
    array[2].fill(1 if next_is_x else -1)
    if state[RESULT] == 0:
        for index in legal_indexes(state):
            array[3, row_index(index), col_index(index)] = 1
    return array


def legal_indexes(state):
    if state[RESULT]:
        return []
    if state[CONSTRAINT] == UNCONSTRAINED:
        indexes = []
        for sub in range(9):
            if state[81 + sub]:
                continue
            base = sub * 9
            indexes.extend(base + cell for cell in range(9) if state[base + cell] == 0)
        return indexes
    sub = state[CONSTRAINT]
    base = sub * 9
    return [base + cell for cell in range(9) if state[base + cell] == 0]
