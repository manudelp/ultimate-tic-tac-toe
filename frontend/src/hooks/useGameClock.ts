/**
 * What each side's clock should read on screen.
 *
 * The server sends the reading at `serverTime` and says whether the clock is
 * running. This corrects for the trip here and ticks the side to move, so a
 * game the server has paused stays still.
 *
 * With no time control it counts up instead, deriving each side's spent time
 * from the move stamps.
 */
import { useEffect, useRef, useState } from "react";
import type { GameState } from "@/types/game";

const TICK_MS = 100;

export type GameClock = {
  /** Seconds left per side, or null when the game is untimed. */
  remaining: { X: number | null; O: number | null };
  /** Seconds spent per side. Only meaningful when untimed. */
  spent: { X: number; O: number };
  timed: boolean;
};

function elapsedFromMoves(state: GameState) {
  let X = 0;
  let O = 0;
  for (let i = 0; i < state.moves.length; i++) {
    const delta = i === 0 ? state.moves[i].time : state.moves[i].time - state.moves[i - 1].time;
    if (state.moves[i].player === "X") X += delta;
    else O += delta;
  }
  return { X, O };
}

function readingAt(state: GameState): { X: number | null; O: number | null } {
  const { X, O } = state.clocks;
  if (X == null || O == null) return state.clocks;
  if (!state.clockRunning) return { X, O };
  const sinceSend = Math.max(0, Date.now() / 1000 - state.serverTime);
  return {
    X: state.activePlayer === "X" ? Math.max(0, X - sinceSend) : X,
    O: state.activePlayer === "O" ? Math.max(0, O - sinceSend) : O,
  };
}

export function useGameClock(state: GameState): GameClock {
  const timed = state.clocks.X != null && state.clocks.O != null;
  const [remaining, setRemaining] = useState(() => readingAt(state));
  const [spent, setSpent] = useState(() => elapsedFromMoves(state));

  // Re-sync whenever a fresh snapshot lands.
  const snapshot = useRef(state.serverTime);
  useEffect(() => {
    snapshot.current = state.serverTime;
    setRemaining(readingAt(state));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.clocks, state.serverTime, state.activePlayer, state.clockRunning]);

  useEffect(() => {
    if (timed) return;
    setSpent(elapsedFromMoves(state));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.moves, timed]);

  const running = state.clockRunning && state.status === "ongoing";

  useEffect(() => {
    if (!running) return;
    const player = state.activePlayer;
    const interval = setInterval(() => {
      if (timed) {
        setRemaining(prev => ({ ...prev, [player]: Math.max(0, (prev[player] ?? 0) - TICK_MS / 1000) }));
      } else {
        setSpent(prev => ({ ...prev, [player]: prev[player] + TICK_MS / 1000 }));
      }
    }, TICK_MS);
    return () => clearInterval(interval);
  }, [running, state.activePlayer, timed]);

  return { remaining, spent, timed };
}
