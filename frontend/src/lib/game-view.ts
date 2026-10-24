/**
 * Turns a GameState into everything the board needs to draw.
 *
 * Pure: no React, no effects. The server is authoritative on the rules, so
 * anything here is presentation — replaying history for the move list, scoring
 * the advantage bar, and naming squares.
 */
import type { GameState, GameMove } from "@/types/game";

export type WinningLine = { type: "row" | "col" | "diag"; index: number };
export type SubWinner = "X" | "O" | "draw" | null;

export const BOARD_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];

const LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
];

/** How many big-board winning lines pass through each board position. */
const POS_WEIGHT = [3, 2, 3, 2, 4, 2, 3, 2, 3];

export function cellValue(v: number): string {
  if (v === 1) return "X";
  if (v === -1) return "O";
  return "";
}

/** Winner of nine values in cell order, as 1, -1 or 0. */
export function lineWinner(flat: number[]): number {
  for (const [a, b, c] of LINES) {
    if (flat[a] !== 0 && flat[a] === flat[b] && flat[b] === flat[c]) return flat[a];
  }
  return 0;
}

export function checkSubWinner(sub: number[][]): number {
  return lineWinner(sub.flat());
}

export function getWinningLine(results: number[][]): WinningLine | null {
  const flat = results.flat();
  for (const [a, b, c] of LINES) {
    if (flat[a] === 0 || flat[a] !== flat[b] || flat[b] !== flat[c]) continue;
    if (a === 0 && c === 2) return { type: "row", index: 0 };
    if (a === 3) return { type: "row", index: 1 };
    if (a === 6 && c === 8) return { type: "row", index: 2 };
    if (a === 0 && c === 6) return { type: "col", index: 0 };
    if (a === 1) return { type: "col", index: 1 };
    if (a === 2 && c === 8) return { type: "col", index: 2 };
    if (a === 0 && c === 8) return { type: "diag", index: 0 };
    return { type: "diag", index: 1 };
  }
  return null;
}

export function isSubFull(sub: number[][]): boolean {
  return sub.every(row => row.every(v => v !== 0));
}

export function replayBoard(moves: GameMove[], upTo: number): number[][][][] {
  const board = Array.from({ length: 3 }, () =>
    Array.from({ length: 3 }, () => Array.from({ length: 3 }, () => [0, 0, 0]))
  );
  for (let i = 0; i <= upTo; i++) {
    const [a, b, c, d] = moves[i].move;
    board[a][b][c][d] = moves[i].player === "X" ? 1 : -1;
  }
  return board;
}

export function replayBoardResults(moves: GameMove[], upTo: number): number[][] {
  return replayBoard(moves, upTo).map(row => row.map(sub => checkSubWinner(sub)));
}

/** Per sub-board: who holds it, "draw" when full and unclaimed, else null. */
export function subWinners(state: GameState): SubWinner[][] {
  return state.boardResults.map((row, a) =>
    row.map((v, b) => {
      if (v === 1) return "X";
      if (v === -1) return "O";
      return isSubFull(state.board[a][b]) ? "draw" : null;
    })
  );
}

/** Sub-boards that cannot be played in: already claimed, or full. */
export function deadSubBoards(state: GameState): boolean[][] {
  return state.board.map((row, a) =>
    row.map((sub, b) => state.boardResults[a][b] !== 0 || isSubFull(sub))
  );
}

function evaluateMiniBoard(sub: number[][]): number {
  const flat = sub.flat();
  let score = 0;
  for (const line of LINES) {
    const vals = line.map(i => flat[i]);
    const x = vals.filter(v => v === 1).length;
    const o = vals.filter(v => v === -1).length;
    if (x > 0 && o > 0) continue; // dead line
    if (x === 2) score += 6;
    else if (x === 1) score += 1;
    if (o === 2) score -= 6;
    else if (o === 1) score -= 1;
  }
  if (flat[4] === 1) score += 2;
  else if (flat[4] === -1) score -= 2;
  return score;
}

/** 0 means O is winning, 100 means X is, 50 is even. */
export function computeAdvantage(
  moves: GameMove[], board: number[][][][], boardResults: number[][],
  hoveredMoveIndex: number | null, isOver: boolean, winner: string | null | undefined,
): number {
  const r = hoveredMoveIndex != null ? replayBoardResults(moves, hoveredMoveIndex) : boardResults;
  const hoveredOver = hoveredMoveIndex != null && hoveredMoveIndex < moves.length - 1;
  const rBoard = hoveredMoveIndex != null ? replayBoard(moves, hoveredMoveIndex) : board;

  if (isOver && !hoveredOver) {
    if (winner === "X") return 100;
    if (winner === "O") return 0;
    return 50;
  }

  const flat = r.flat(); // 9 values: 1 = X holds, -1 = O holds, 0 = open
  const boardDead: boolean[] = [];
  for (let a = 0; a < 3; a++) {
    for (let b = 0; b < 3; b++) {
      const idx = a * 3 + b;
      boardDead.push(flat[idx] !== 0 ? true : isSubFull(rBoard[a][b]));
    }
  }

  let score = 0;

  for (const line of LINES) {
    const vals = line.map(i => flat[i]);
    const xWon = vals.filter(v => v === 1).length;
    const oWon = vals.filter(v => v === -1).length;
    if (xWon > 0 && oWon > 0) continue;
    const blocked = line.filter(i => flat[i] === 0 && boardDead[i]).length;

    if (oWon === 0 && blocked === 0) {
      if (xWon === 3) score += 1000;
      else if (xWon === 2) score += 40;
      else if (xWon === 1) score += 8;
      else score += 1;
    }
    if (xWon === 0 && blocked === 0) {
      if (oWon === 3) score -= 1000;
      else if (oWon === 2) score -= 40;
      else if (oWon === 1) score -= 8;
      else score -= 1;
    }
    if (oWon === 0 && blocked > 0 && xWon > 0) score += xWon === 2 ? 10 : 2;
    if (xWon === 0 && blocked > 0 && oWon > 0) score -= oWon === 2 ? 10 : 2;
  }

  for (let i = 0; i < 9; i++) {
    if (flat[i] === 1) score += 15 * POS_WEIGHT[i];
    else if (flat[i] === -1) score -= 15 * POS_WEIGHT[i];
  }

  for (let a = 0; a < 3; a++) {
    for (let b = 0; b < 3; b++) {
      const idx = a * 3 + b;
      if (flat[idx] !== 0 || boardDead[idx]) continue;
      score += evaluateMiniBoard(rBoard[a][b]) * POS_WEIGHT[idx] * 0.3;
    }
  }

  // Empirically the score lands within roughly -300..+300.
  return Math.max(5, Math.min(95, Math.round(50 + score / 6)));
}

/** Where a move sent the opponent, and how it moved the advantage bar. */
export function getMoveMetadata(
  moves: GameMove[], index: number, board: number[][][][], boardResults: number[][],
  isOver: boolean, winner: string | null | undefined,
): { sendsTo: string; delta: string } {
  const [, , c, d] = moves[index].move;
  const targetBoard = c * 3 + d;

  let sendsTo: string;
  if (index === moves.length - 1 && isOver) {
    sendsTo = "—";
  } else {
    const boardAfter = replayBoard(moves, index);
    const sub = boardAfter[c][d];
    const taken = checkSubWinner(sub) !== 0 || isSubFull(sub);
    sendsTo = taken ? "Free" : BOARD_LABELS[targetBoard];
  }

  let delta = "";
  if (index > 0) {
    const prev = computeAdvantage(moves, board, boardResults, index - 1, false, null);
    const curr = computeAdvantage(moves, board, boardResults, index, isOver, winner);
    const diff = curr - prev;
    if (diff > 0) delta = `+${diff}`;
    else if (diff < 0) delta = `${diff}`;
  }

  return { sendsTo, delta };
}

export function formatClock(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? "0" : ""}${s}`;
}

export function formatMoveTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s.toFixed(1)}`;
}
