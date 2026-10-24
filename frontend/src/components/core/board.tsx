import React, { useEffect, useRef, useState } from "react";
import WinLine from "@/components/core/win-line";
import MiniBoard from "@/components/core/miniboard";
import { motion } from "framer-motion";
import { formatMove } from "@/lib/notation";
import { ArrowLeft, Flag, ChevronUp } from "lucide-react";
import { toastNotYourTurn, toastCellOccupied } from "@/lib/toasts";
import type { GameState, GameMove } from "@/types/game";
import { useGameClock } from "@/hooks/useGameClock";
import {
  BOARD_LABELS, cellValue, computeAdvantage, deadSubBoards, formatClock, formatMoveTime,
  getMoveMetadata, getWinningLine, replayBoard, subWinners,
} from "@/lib/game-view";
import ThemeToggle from "@/components/ui/theme-toggle";

interface BoardProps {
  state: GameState;
  myPlayer: "X" | "O";
  opponent?: { type: "bot"; name: string; icon: string } | null;
  isLocal?: boolean;
  onCellClick: (a: number, b: number, c: number, d: number) => void;
  onResign: () => void;
  onExit: () => void;
}

const Board: React.FC<BoardProps> = ({ state, myPlayer, opponent, isLocal, onCellClick, onResign, onExit }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [showOverlay, setShowOverlay] = useState(true);
  const moveHistoryRef = useRef<HTMLDivElement>(null);
  const mobileHistoryRef = useRef<HTMLTableSectionElement>(null);
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

  const winners = subWinners(state);
  const disabled = deadSubBoards(state);
  const stringBoard: string[][][][] = state.board.map(row =>
    row.map(sub => sub.map(r => r.map(v => cellValue(v))))
  );

  const activeMiniBoard: [number, number] | null = state.forcedBoard
    ? [state.forcedBoard[0], state.forcedBoard[1]]
    : null;

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 1024);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  useEffect(() => {
    if (moveHistoryRef.current) {
      if (isMobile) {
        // mobile: scroll the tbody's parent (the scrollable div)
        const scrollParent = mobileHistoryRef.current?.closest(".overflow-y-auto");
        if (scrollParent) scrollParent.scrollTop = scrollParent.scrollHeight;
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

  const { remaining: displayClocks, spent: elapsed, timed: hasClock } = useGameClock(state);

  const formatClock = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const formatMoveTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s.toFixed(1)}`;
  };

  return (
    <div className="relative flex flex-col gap-2 sm:px-4 lg:flex-row lg:gap-4 lg:h-svh lg:py-4 lg:overflow-hidden">
      {/* Board column: on desktop, a grid with auto info bar + 1fr board */}
      <div className="flex flex-col items-center w-[min(calc(100vw-1rem),600px)] lg:w-auto lg:h-full lg:grid lg:grid-rows-[auto_1fr] lg:gap-4">
        {/* Info Bar */}
        <div className="flex items-center justify-between w-full px-2.5 py-2 lg:px-4 lg:py-2.5 bg-[hsl(var(--board-bg))] rounded mb-2 lg:mb-0">
          <div className="flex items-center gap-2 lg:gap-3">
            <div className={`w-8 h-8 lg:w-10 lg:h-10 flex items-center justify-center rounded-md ${
              state.activePlayer === "X" ? "bg-blue-500/20" : "bg-red-500/20"
            }`}>
              <span className={`text-lg lg:text-2xl font-bold ${
                state.activePlayer === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"
              }`}>
                {state.activePlayer}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[11px] lg:text-xs text-muted-foreground">
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
                <span className="text-xs lg:text-sm font-semibold text-green-600 dark:text-green-400">
                  {isLocal ? `Player ${state.winner} wins!` : state.winner === myPlayer ? "You win!" : "You lose"}
                </span>
              )}
              {isOver && !state.winner && (
                <span className="text-xs lg:text-sm font-semibold text-yellow-600 dark:text-yellow-400">Draw</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1.5 lg:gap-2">
            <div className="flex items-center gap-2 lg:gap-3 text-xs lg:text-sm font-mono">
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
            <div className="hidden lg:block"><ThemeToggle /></div>
          </div>
        </div>

        {/* Board: on mobile width-driven square, on desktop height-driven square */}
        <div className="relative w-full aspect-square lg:h-full lg:w-auto lg:aspect-auto lg:overflow-hidden">
          <div className="relative grid grid-cols-3 gap-1.5 sm:gap-2.5 w-full aspect-square lg:h-full lg:w-auto lg:max-h-full lg:aspect-square">
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

            <WinLine line={winningLine} />

            {/* Game over overlay */}
            {isOver && showOverlay && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8, duration: 0.4 }}
                className="absolute inset-0 flex flex-col items-center justify-center bg-background/70 backdrop-blur-sm rounded-lg z-10 cursor-pointer"
                onClick={() => setShowOverlay(false)}
              >
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 1, duration: 0.3, type: "spring", stiffness: 300, damping: 25 }}
                  className="flex flex-col items-center gap-2 p-6 sm:p-8"
                >
                  {state.winner ? (
                    <>
                      <span className={`text-5xl sm:text-7xl font-bold ${
                        state.winner === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"
                      }`}>
                        {state.winner}
                      </span>
                      <p className="text-lg sm:text-xl font-bold">
                        {isLocal ? `Player ${state.winner} wins!` : state.winner === myPlayer ? "You win!" : "You lose"}
                      </p>
                    </>
                  ) : (
                    <>
                      <span className="text-4xl sm:text-6xl font-bold text-muted-foreground">=</span>
                      <p className="text-lg sm:text-xl font-bold text-muted-foreground">Draw</p>
                    </>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">{state.moves.length} moves</p>
                  <p className="text-[10px] text-muted-foreground/50 mt-3">Tap to view board</p>
                </motion.div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Mobile bottom drawer */}
        {isMobile && (
          <div className="w-full mt-1.5 space-y-1.5">
            {/* Collapsed: advantage bar + handle */}
            <button
              onClick={() => setDrawerOpen(o => !o)}
              className="w-full p-2.5 bg-[hsl(var(--board-bg))] rounded flex flex-col gap-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {opponent ? (
                    <>
                      <span className="text-sm">{opponent.icon}</span>
                      <span className="text-[11px] font-medium">vs {opponent.name}</span>
                    </>
                  ) : (
                    <span className="text-[11px] font-medium text-muted-foreground">{isLocal ? "Local" : "Online"}</span>
                  )}
                  <span className="text-[11px] text-muted-foreground">· Move {state.moves.length}</span>
                </div>
                <ChevronUp className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${drawerOpen ? "rotate-180" : ""}`} />
              </div>
              {(() => {
                const clamped = computeAdvantage(state.moves, state.board, state.boardResults, hoveredMoveIndex, isOver, state.winner);
                return (
                  <div className="flex h-1.5 rounded-full overflow-hidden bg-surface w-full">
                    <div className="bg-blue-500 transition-all duration-500 ease-out rounded-l-full" style={{ width: `${clamped}%` }} />
                    <div className="bg-red-500 transition-all duration-500 ease-out rounded-r-full" style={{ width: `${100 - clamped}%` }} />
                  </div>
                );
              })()}
            </button>

            {/* Expanded drawer */}
            {drawerOpen && (
              <div className="w-full bg-[hsl(var(--board-bg))] rounded overflow-hidden">
                {/* Game status header */}
                <div className="flex justify-between items-center px-3 pt-2.5 pb-2 border-b border-border/30">
                  <span className={`text-[11px] font-medium ${
                    isOver
                      ? state.winner ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"
                      : "text-muted-foreground"
                  }`}>
                    {isOver ? (state.winner ? `${state.winner} wins` : "Draw") : "In progress"}
                  </span>
                  <span className="text-[11px] text-muted-foreground">
                    {state.moves.length} moves · {new Date().toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                  </span>
                </div>

                {/* Move history table */}
                <div className="max-h-48 overflow-y-auto scrollbar-thin scrollbar-thumb-muted">
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 z-10">
                      <tr className="text-[10px] text-muted-foreground bg-[hsl(var(--board-bg))]">
                        <th className="pl-3 pr-1 py-1.5 text-left w-7">#</th>
                        <th className="px-1 py-1.5 text-center">Move</th>
                        <th className="px-1 py-1.5 text-center">Sends</th>
                        <th className="px-1 py-1.5 text-center">Δ</th>
                        <th className="pl-1 pr-3 py-1.5 text-right">Time</th>
                      </tr>
                    </thead>
                    <tbody ref={mobileHistoryRef}>
                      {state.moves.map((move: GameMove, i: number) => {
                        const delta = i === 0 ? move.time : move.time - state.moves[i - 1].time;
                        const timeStr = formatMoveTime(delta);
                        const { sendsTo, delta: advDelta } = getMoveMetadata(state.moves, i, state.board, state.boardResults, isOver, state.winner);
                        return (
                          <tr
                            key={i}
                            className={`${i === state.moves.length - 1 ? "bg-surface/30" : ""}`}
                          >
                            <td className="pl-3 pr-1 py-1 text-muted-foreground">{i + 1}</td>
                            <td className="px-1 py-1 text-center">
                              <span className={`font-medium ${move.player === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"}`}>{move.player}</span>
                              <span className="ml-0.5">{formatMove(move.move as [number, number, number, number])}</span>
                            </td>
                            <td className={`px-1 py-1 text-center ${sendsTo === "Free" ? "text-yellow-500" : "text-muted-foreground"}`}>{sendsTo}</td>
                            <td className={`px-1 py-1 text-center font-mono ${advDelta.startsWith("+") ? "text-[hsl(var(--markx))]" : advDelta.startsWith("-") ? "text-[hsl(var(--marko))]" : "text-muted-foreground"}`}>{advDelta}</td>
                            <td className="pl-1 pr-3 py-1 text-right text-muted-foreground font-mono">{timeStr}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Mobile controls — always visible */}
            <div className="flex w-full gap-2">
              <button onClick={onExit} className="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-sm bg-surface-hover rounded hover:bg-surface-active transition-colors">
                <ArrowLeft className="w-3.5 h-3.5" /> Exit
              </button>
              {!isOver && (
                <button onClick={onResign} className="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-sm bg-red-600 dark:bg-red-800 text-white rounded hover:bg-red-500 dark:hover:bg-red-700 transition-colors">
                  <Flag className="w-3.5 h-3.5" /> Resign
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Desktop side panel */}
      {!isMobile && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex flex-col gap-4 w-72 lg:h-full overflow-hidden">
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
              const clamped = computeAdvantage(state.moves, state.board, state.boardResults, hoveredMoveIndex, isOver, state.winner);
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
                    <th className="p-1.5 text-center">Move</th>
                    <th className="p-1.5 text-center">Sends</th>
                    <th className="p-1.5 text-center">Δ</th>
                    <th className="p-1.5 text-right">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {state.moves.map((move: GameMove, i: number) => {
                    const delta = i === 0 ? move.time : move.time - state.moves[i - 1].time;
                    const timeStr = formatMoveTime(delta);
                    const { sendsTo, delta: advDelta } = getMoveMetadata(state.moves, i, state.board, state.boardResults, isOver, state.winner);
                    return (
                    <tr
                      key={i}
                      className={`hover:bg-surface-hover/50 cursor-pointer ${i === state.moves.length - 1 ? "bg-surface/30" : ""}`}
                      onMouseEnter={() => { setHoveredMove(move.move as [number, number, number, number]); setHoveredMoveIndex(i); }}
                      onMouseLeave={() => { setHoveredMove(null); setHoveredMoveIndex(null); }}
                    >
                      <td className="p-1.5 text-muted-foreground">{i + 1}</td>
                      <td className="p-1.5 text-center">
                        <span className={`font-medium ${move.player === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"}`}>{move.player}</span>
                        <span className="ml-1">{formatMove(move.move as [number, number, number, number])}</span>
                      </td>
                      <td className={`p-1.5 text-center ${sendsTo === "Free" ? "text-yellow-500" : "text-muted-foreground"}`}>{sendsTo}</td>
                      <td className={`p-1.5 text-center font-mono text-xs ${advDelta.startsWith("+") ? "text-[hsl(var(--markx))]" : advDelta.startsWith("-") ? "text-[hsl(var(--marko))]" : "text-muted-foreground"}`}>{advDelta}</td>
                      <td className="p-1.5 text-right text-muted-foreground font-mono">{timeStr}</td>
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
