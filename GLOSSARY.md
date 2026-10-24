# Glossary

The words this codebase uses for Ultimate Tic-Tac-Toe, and where each one lives.
Use these names in code and in conversation; prefer them over synonyms.

## The game

**Sub-board** — one of the nine 3×3 grids. _Not_: mini board, local board, small board.
A sub-board is **over** when it is won or full, and **playable** otherwise.

**Big board** — the 3×3 arrangement of sub-board results. Winning three sub-boards
in a line wins the game.

**Cell** — one of the nine squares inside a sub-board.

**Forced sub-board** — the sub-board the player to move must play in, decided by
the cell the opponent last played. `None` when that sub-board is over and the
mover may choose freely. _Not_: active board, constraint.

**Mover** — the side to move, `+1` for X and `-1` for O. Stones are stored with
the same signs, so the board is always read in absolute colours.

**Ply** — one stone placed. A game is at most 81 plies.

## How a position is written down

**Sub-board index** — a sub-board encoded as one base-3 integer: digit `r*3+c`
carries cell `(r, c)`, where `0` is empty, `1` is `+1` and `2` is `-1`. This makes
every rule question a table lookup. Lives in `core/rules.py`.

**Position** — a whole position: the nine sub-board indexes, the mover, and the
forced sub-board. Immutable; `play` returns a new one. This is what a bot is
handed, which is why no caller flips a board. Lives in `core/position.py`.

**Mover board** — a 3×3×3×3 board rewritten so the mover's own stones read `+1`.
Agents that think in "my stones are positive" ask a Position for it. The flip has
exactly one implementation, `Position.mover_board`.

**State** — Arkadiusz Nowaczyński's 93-byte encoding, used for his network and his
datasets: 81 cells, 9 sub-board results, side to move, forced sub-board, result.
Converted in `arena/codec.py`. Only use "state" for that format.

**Feature planes** — the 4×9×9 stack his policy-value network consumes: the
mover's stones, the opponent's stones, `+1`/`-1` for whether X is to move, and
the legal cells.

## Playing

**Agent** — a bot. Answers `choose(position)` with a move. Agents hold no
per-game state, so one instance serves every game. Lives in `bots/`.

**Live game** — a game in progress: the engine, who sits in each **seat**, and the
bot if there is one. Lives in `core/store.py`, which also holds the matchmaking
queue. Knows nothing about sockets.

**Seat** — one of the two places a connection can occupy in a live game. A seat
holds a token identifying the connection, so a player who reconnects can be put
back in the seat they had.

**Arena** — offline bot-against-bot play, used to measure strength against
uttt.ai. Lives in `backend/arena/`. An **opening** is one of the 50 fixed
positions his evaluation plays from, each played twice with colours swapped.
