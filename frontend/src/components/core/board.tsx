import React, { useEffect, useRef, useState } from "react";
import MiniBoard from "@/components/core/miniboard";
import { motion } from "framer-motion";
import { formatMove } from "@/lib/notation";
import { ArrowLeft, Flag } from "lucide-react";
import { toastNotYourTurn, toastCellOccupied } from "@/lib/toasts";
import type { GameState, GameMove } from "@/types/game";
import ThemeToggle from "@/components/ui/theme-toggle";

type WinningLine = { type: "row" | "col" | "diag"; index: number };

interface BoardProps {
  state: GameState;
  myPlayer: "X" | "O";
  opponent?: { type: "bot"; name: string; icon: string } | null;
  isLocal?: boolean;
  onCellClick: (a: number, b: number, c: number, d: number) => void;
  onResign: () => void;
  onExit: () => void;
}

function cellValue(v: number): string {
  if (v === 1) return "X";
  if (v === -1) return "O";
  return "";
}

function boardResultStr(v: number): string | null {
  if (v === 1) return "X";
  if (v === -1) return "O";
  return null;
}

function getWinningLine(results: number[][]): { type: "row" | "col" | "diag"; index: number } | null {
  for (let i = 0; i < 3; i++) {
    if (results[i][0] !== 0 && results[i][0] === results[i][1] && results[i][1] === results[i][2])
      return { type: "row", index: i };
    if (results[0][i] !== 0 && results[0][i] === results[1][i] && results[1][i] === results[2][i])
      return { type: "col", index: i };
  }
  if (results[0][0] !== 0 && results[0][0] === results[1][1] && results[1][1] === results[2][2])
    return { type: "diag", index: 0 };
  if (results[0][2] !== 0 && results[0][2] === results[1][1] && results[1][1] === results[2][0])
    return { type: "diag", index: 1 };
  return null;
}

function checkSubWinner(sub: number[][]): number {
  for (let i = 0; i < 3; i++) {
    if (sub[i][0] !== 0 && sub[i][0] === sub[i][1] && sub[i][1] === sub[i][2]) return sub[i][0];
    if (sub[0][i] !== 0 && sub[0][i] === sub[1][i] && sub[1][i] === sub[2][i]) return sub[0][i];
  }
  if (sub[0][0] !== 0 && sub[0][0] === sub[1][1] && sub[1][1] === sub[2][2]) return sub[0][0];
  if (sub[0][2] !== 0 && sub[0][2] === sub[1][1] && sub[1][1] === sub[2][0]) return sub[0][2];
  return 0;
}

function replayBoard(moves: GameMove[], upTo: number): number[][][][] {
  const board = Array.from({ length: 3 }, () =>
    Array.from({ length: 3 }, () =>
      Array.from({ length: 3 }, () => [0, 0, 0])
    )
  );
  for (let i = 0; i <= upTo; i++) {
    const [a, b, c, d] = moves[i].move;
    board[a][b][c][d] = moves[i].player === "X" ? 1 : -1;
  }
  return board;
}

function replayBoardResults(moves: GameMove[], upTo: number): number[][] {
  const board = replayBoard(moves, upTo);
  return board.map(row => row.map(sub => checkSubWinner(sub)));
}

const Board: React.FC<BoardProps> = ({ state, myPlayer, opponent, isLocal, onCellClick, onResign, onExit }) => {
  const [isMobile, setIsMobile] = useState(false);
  const moveHistoryRef = useRef<HTMLDivElement>(null);
  const [hoveredMove, setHoveredMove] = useState<[number, number, number, number] | null>(null);
  const [hoveredMoveIndex, setHoveredMoveIndex] = useState<number | null>(null);

  const tapRef = useRef<HTMLAudioElement | null>(null);
  const winRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    tapRef.current = new Audio("/assets/sounds/tap.mp3");
    winRef.current = new Audio("/assets/sounds/win.mp3");
  }, []);

  useEffect(() => {
    if (state.moves.length > 0) tapRef.current?.play().catch(() => {});
  }, [state.moves.length]);

  useEffect(() => {
    if (state.status !== "ongoing" && state.winner) winRef.current?.play().catch(() => {});
  }, [state.status, state.winner]);

  const isMyTurn = isLocal || state.activePlayer === myPlayer;
  const isOver = state.status !== "ongoing";
  const lastMove = state.moves.length > 0 ? state.moves[state.moves.length - 1].move as [number, number, number, number] : null;
  const winningLine = isOver && state.winner ? getWinningLine(state.boardResults) : null;

  const winners: (string | null)[][] = state.boardResults.map((row, a) =>
    row.map((v, b) => {
      if (v === 1) return "X";
      if (v === -1) return "O";
      if (v === 0) {
        const sub = state.board[a][b];
        const isFull = sub.every((r: number[]) => r.every((c: number) => c !== 0));
        if (isFull) return "draw";
      }
      return null;
    })
  );

  const disabled: boolean[][] = state.board.map((row, a) =>
    row.map((sub, b) => {
      if (state.boardResults[a][b] !== 0) return true;
      for (let c = 0; c < 3; c++)
        for (let d = 0; d < 3; d++)
          if (sub[c][d] === 0) return false;
      return true;
    })
  );

  const stringBoard: string[][][][] = state.board.map(row =>
    row.map(sub =>
      sub.map(r => r.map(v => cellValue(v)))
    )
  );

  const activeMiniBoard: [number, number] | null = state.forcedBoard
    ? [state.forcedBoard[0], state.forcedBoard[1]]
    : null;

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  useEffect(() => {
    if (moveHistoryRef.current) {
      if (isMobile) {
        moveHistoryRef.current.scrollLeft = moveHistoryRef.current.scrollWidth;
      } else {
        moveHistoryRef.current.scrollTop = moveHistoryRef.current.scrollHeight;
      }
    }
  }, [state.moves, isMobile]);

  const handleCellClick = (a: number, b: number, c: number, d: number) => {
    if (isOver) return;
    if (!isMyTurn) {
      toastNotYourTurn();
      return;
    }
    if (state.board[a][b][c][d] !== 0) {
      toastCellOccupied();
      return;
    }
    onCellClick(a, b, c, d);
  };

  const [displayClocks, setDisplayClocks] = useState(state.clocks);
  const hasClock = displayClocks.X != null && displayClocks.O != null;

  const [elapsed, setElapsed] = useState({ X: 0, O: 0 });

  useEffect(() => {
    setDisplayClocks(state.clocks);
  }, [state.clocks]);

  useEffect(() => {
    if (hasClock) return;
    let x = 0, o = 0;
    for (let i = 0; i < state.moves.length; i++) {
      const delta = i === 0 ? state.moves[i].time : state.moves[i].time - state.moves[i - 1].time;
      if (state.moves[i].player === "X") x += delta; else o += delta;
    }
    setElapsed({ X: x, O: o });
  }, [state.moves, hasClock]);

  useEffect(() => {
    if (isOver || hasClock) return;
    const interval = setInterval(() => {
      setElapsed((prev) => ({
        ...prev,
        [state.activePlayer]: prev[state.activePlayer] + 0.1,
      }));
    }, 100);
    return () => clearInterval(interval);
  }, [state.activePlayer, isOver, hasClock]);

  useEffect(() => {
    if (isOver || !hasClock) return;
    const interval = setInterval(() => {
      setDisplayClocks((prev) => ({
        ...prev,
        [state.activePlayer]: Math.max(0, (prev[state.activePlayer] ?? 0) - 0.1),
      }));
    }, 100);
    return () => clearInterval(interval);
  }, [state.activePlayer, isOver, hasClock]);

  const formatClock = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="relative flex flex-col gap-6 sm:px-4 md:flex-row md:items-start md:h-svh md:py-8">
      <div className="flex flex-col items-center md:h-full md:justify-center w-[min(calc(100vw-2rem),600px)] md:w-[min(calc(100svh-8rem),600px)]">
        {/* Info Bar + Board */}
        <div className="w-full">
        <div className="flex items-center justify-between w-full px-4 py-3 mb-4 bg-[hsl(var(--board-bg))] rounded">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 flex items-center justify-center rounded-md ${
              state.activePlayer === "X" ? "bg-blue-500/20" : "bg-red-500/20"
            }`}>
              <span className={`text-2xl font-bold ${
                state.activePlayer === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"
              }`}>
                {state.activePlayer}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground">
                {isOver
                  ? "Game Over"
                  : isLocal
                    ? `Player ${state.activePlayer}'s turn`
                    : isMyTurn
                      ? "Your turn"
                      : opponent
                        ? `${opponent.icon} ${opponent.name}'s turn`
                        : "Opponent's turn"}
              </span>
              {isOver && state.winner && (
                <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                  {isLocal ? `Player ${state.winner} wins!` : state.winner === myPlayer ? "You win!" : "You lose"}
                </span>
              )}
              {isOver && !state.winner && (
                <span className="text-sm font-semibold text-yellow-600 dark:text-yellow-400">Draw</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-3 text-sm font-mono">
              {hasClock ? (
                <>
                  <span className={state.activePlayer === "X" ? "text-[hsl(var(--markx))]" : "text-muted-foreground"}>
                    {formatClock(displayClocks.X!)}
                  </span>
                  <span className="text-subtle">|</span>
                  <span className={state.activePlayer === "O" ? "text-[hsl(var(--marko))]" : "text-muted-foreground"}>
                    {formatClock(displayClocks.O!)}
                  </span>
                </>
              ) : (
                <>
                  <span className={state.activePlayer === "X" ? "text-[hsl(var(--markx))]" : "text-muted-foreground"}>
                    {formatClock(elapsed.X)}
                  </span>
                  <span className="text-subtle">|</span>
                  <span className={state.activePlayer === "O" ? "text-[hsl(var(--marko))]" : "text-muted-foreground"}>
                    {formatClock(elapsed.O)}
                  </span>
                </>
              )}
            </div>
            <ThemeToggle />
          </div>
        </div>

        {/* Board */}
        <div className="relative w-full aspect-square">
          <div className="relative grid grid-cols-3 gap-1.5 sm:gap-2.5 w-full aspect-square">
            {stringBoard.map((miniBoardRow, a) =>
              miniBoardRow.map((miniBoard, b) => (
                <MiniBoard
                  key={`${a}-${b}`}
                  miniBoard={miniBoard}
                  localRowIndex={a}
                  localColIndex={b}
                  winners={winners}
                  disabled={disabled}
                  activeMiniBoard={activeMiniBoard}
                  activePlayer={state.activePlayer}
                  lastMove={lastMove}
                  gameOver={isOver}
                  hoveredMove={hoveredMove}
                  handleCellClick={handleCellClick}
                />
              ))
            )}

            {winningLine && (
              <div className="absolute inset-0 pointer-events-none">
                {winningLine.type === "row" && (
                  <div
                    className="absolute left-[2.5%] w-[95%] h-[5px] bg-green-500 rounded-full"
                    style={{ top: `${(100 / 3) * winningLine.index + 50 / 3}%`, animation: "winLineRow 0.5s ease-out forwards" }}
                  />
                )}
                {winningLine.type === "col" && (
                  <div
                    className="absolute top-[2.5%] h-[95%] w-[5px] bg-green-500 rounded-full"
                    style={{ left: `${(100 / 3) * winningLine.index + 50 / 3}%`, animation: "winLineCol 0.5s ease-out forwards" }}
                  />
                )}
                {winningLine.type === "diag" && winningLine.index === 0 && (
                  <div
                    className="absolute w-[130%] h-[5px] bg-green-500 rounded-full"
                    style={{ top: "50%", left: "50%", animation: "winLineDiag0 0.5s ease-out forwards" }}
                  />
                )}
                {winningLine.type === "diag" && winningLine.index === 1 && (
                  <div
                    className="absolute w-[130%] h-[5px] bg-green-500 rounded-full"
                    style={{ top: "50%", left: "50%", animation: "winLineDiag1 0.5s ease-out forwards" }}
                  />
                )}
              </div>
            )}
          </div>
        </div>
        </div>

        {/* Mobile move history */}
        {isMobile && state.moves.length > 0 && (
          <div className="w-full mt-4">
            <div ref={moveHistoryRef} className="w-full px-1 py-2 overflow-x-auto bg-card rounded scrollbar-thin scrollbar-thumb-muted">
              <div className="inline-flex gap-2 px-2">
                {state.moves.map((move: GameMove, i: number) => (
                  <div
                    key={i}
                    className={`cursor-pointer rounded-md px-2 py-1 text-xs ${
                      i === state.moves.length - 1 ? "bg-surface-active" : "hover:bg-surface-hover/50"
                    }`}
                    onMouseEnter={() => { setHoveredMove(move.move as [number, number, number, number]); setHoveredMoveIndex(i); }}
                    onMouseLeave={() => { setHoveredMove(null); setHoveredMoveIndex(null); }}
                  >
                    <span className="text-muted-foreground">{i + 1}.</span>
                    <span className={move.player === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"}>
                      {move.player}
                    </span>
                    <span className="ml-1">{formatMove(move.move as [number, number, number, number])}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Mobile controls */}
        {isMobile && (
          <div className="flex w-full gap-3 mt-4">
            <button onClick={onExit} className="flex-1 flex items-center justify-center gap-2 py-3 bg-surface-hover rounded hover:bg-surface-active transition-colors">
              <ArrowLeft className="w-4 h-4" /> Exit
            </button>
            {!isOver && (
              <button onClick={onResign} className="flex-1 flex items-center justify-center gap-2 py-3 bg-red-600 dark:bg-red-800 text-white rounded hover:bg-red-500 dark:hover:bg-red-700 transition-colors">
                <Flag className="w-4 h-4" /> Resign
              </button>
            )}
          </div>
        )}
      </div>

      {/* Desktop side panel */}
      {!isMobile && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex flex-col gap-4 w-72 h-[calc(100svh-4rem)] overflow-hidden">
          {/* Game Info */}
          <div className="p-4 bg-[hsl(var(--board-bg))] rounded space-y-3">
            <div className="flex justify-between items-start">
              {opponent ? (
                <div className="flex items-center gap-2">
                  <span className="text-lg">{opponent.icon}</span>
                  <span className="text-sm font-medium">vs {opponent.name}</span>
                </div>
              ) : (
                <span className="text-sm font-medium text-muted-foreground">{isLocal ? "Local Game" : "Online Game"}</span>
              )}
              <div className="flex flex-col items-end">
                <span className="text-[11px] text-muted-foreground">{new Date().toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</span>
                <span className="text-[11px] text-muted-foreground">{new Date().toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}</span>
              </div>
            </div>

            {/* Advantage Bar */}
            {(() => {
              const r = hoveredMoveIndex != null ? replayBoardResults(state.moves, hoveredMoveIndex) : state.boardResults;
              const hoveredOver = hoveredMoveIndex != null && hoveredMoveIndex < state.moves.length - 1;
              const LINES = [
                [[0,0],[0,1],[0,2]], [[1,0],[1,1],[1,2]], [[2,0],[2,1],[2,2]],
                [[0,0],[1,0],[2,0]], [[0,1],[1,1],[2,1]], [[0,2],[1,2],[2,2]],
                [[0,0],[1,1],[2,2]], [[0,2],[1,1],[2,0]],
              ];
              const rBoard = hoveredMoveIndex != null ? replayBoard(state.moves, hoveredMoveIndex) : state.board;
              const rDisabled: boolean[][] = rBoard.map((row, a) =>
                row.map((sub, b) => {
                  if (r[a][b] !== 0) return true;
                  for (let c = 0; c < 3; c++)
                    for (let d = 0; d < 3; d++)
                      if (sub[c][d] === 0) return false;
                  return true;
                })
              );
              const rWinners: (string | null)[][] = r.map((row, a) =>
                row.map((v, b) => {
                  if (v === 1) return "X";
                  if (v === -1) return "O";
                  if (v === 0 && rDisabled[a][b]) return "draw";
                  return null;
                })
              );
              let xScore = 0, oScore = 0;
              for (const line of LINES) {
                const vals = line.map(([a, b]) => r[a][b]);
                const x = vals.filter(v => v === 1).length;
                const o = vals.filter(v => v === -1).length;
                const d = vals.filter(v => {
                  if (v !== 0) return false;
                  const [a, b] = line[vals.indexOf(v)];
                  return rDisabled[a][b] && rWinners[a][b] === "draw";
                }).length;
                if (o === 0 && d === 0) { if (x === 1) xScore += 1; if (x === 2) xScore += 4; }
                if (x === 0 && d === 0) { if (o === 1) oScore += 1; if (o === 2) oScore += 4; }
              }
              const total = xScore + oScore || 1;
              const showOver = isOver && !hoveredOver;
              const xPct = showOver
                ? (state.winner === "X" ? 100 : state.winner === "O" ? 0 : 50)
                : Math.round(50 + ((xScore - oScore) / total) * 50);
              const clamped = showOver ? xPct : Math.max(5, Math.min(95, xPct));
              return (
                <div className="space-y-1.5">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-[hsl(var(--markx))] font-medium">X</span>
                    <span className="text-muted-foreground">Advantage</span>
                    <span className="text-[hsl(var(--marko))] font-medium">O</span>
                  </div>
                  <div className="flex h-2 rounded-full overflow-hidden bg-surface">
                    <div
                      className="bg-blue-500 transition-all duration-500 ease-out rounded-l-full"
                      style={{ width: `${clamped}%` }}
                    />
                    <div
                      className="bg-red-500 transition-all duration-500 ease-out rounded-r-full"
                      style={{ width: `${100 - clamped}%` }}
                    />
                  </div>
                </div>
              );
            })()}

            {/* Details */}
            <div className="flex justify-between items-center pt-2 border-t border-border">
              <span className="text-xs text-muted-foreground">Move {state.moves.length + 1}</span>
              <span className={`text-xs font-medium ${
                isOver
                  ? state.winner ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"
                  : "text-muted-foreground"
              }`}>
                {isOver ? (state.winner ? `${state.winner} wins` : "Draw") : "In progress"}
              </span>
            </div>
          </div>

          {/* Move history */}
          <div className="flex-1 min-h-0 flex flex-col p-4 bg-[hsl(var(--board-bg))] rounded">
            <div className="flex justify-between mb-2 text-sm text-muted-foreground">
              <span>Moves</span>
              <span className="text-xs">{state.moves.length}</span>
            </div>
            <div ref={moveHistoryRef} className="flex-1 min-h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-muted">
              <table className="w-full text-sm">
                <thead className="sticky top-0 z-10">
                  <tr className="text-xs text-muted-foreground bg-[hsl(var(--board-bg))]">
                    <th className="p-1.5 text-left w-8">#</th>
                    <th className="p-1.5 text-center w-10">Player</th>
                    <th className="p-1.5 text-right">Move</th>
                    <th className="p-1.5 text-right">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {state.moves.map((move: GameMove, i: number) => {
                    const delta = i === 0 ? move.time : move.time - state.moves[i - 1].time;
                    const timeStr = delta < 60 ? `${delta.toFixed(2)}s` : `${Math.floor(delta / 60)}m ${Math.floor(delta % 60)}s`;
                    return (
                    <tr
                      key={i}
                      className={`hover:bg-surface-hover/50 cursor-pointer ${i === state.moves.length - 1 ? "bg-surface/30" : ""}`}
                      onMouseEnter={() => { setHoveredMove(move.move as [number, number, number, number]); setHoveredMoveIndex(i); }}
                      onMouseLeave={() => { setHoveredMove(null); setHoveredMoveIndex(null); }}
                    >
                      <td className="p-1.5 text-muted-foreground">{i + 1}</td>
                      <td className={`p-1.5 text-center font-medium ${move.player === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"}`}>
                        {move.player}
                      </td>
                      <td className="p-1.5 text-right">{formatMove(move.move as [number, number, number, number])}</td>
                      <td className="p-1.5 text-right text-muted-foreground">{timeStr}</td>
                    </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Controls */}
          <div className="flex gap-2">
            <button onClick={onExit} className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-surface-hover rounded hover:bg-surface-active transition-colors">
              <ArrowLeft className="w-4 h-4" /> Exit
            </button>
            {!isOver && (
              <button onClick={onResign} className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-600 dark:bg-red-800 text-white rounded hover:bg-red-500 dark:hover:bg-red-700 transition-colors">
                <Flag className="w-4 h-4" /> Resign
              </button>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Board;
