import React, { useEffect, useRef, useState } from "react";
import MiniBoard from "@/components/core/miniboard";
import { motion } from "framer-motion";
import { formatMove } from "@/lib/notation";
import { ArrowLeft, Flag, ChevronUp } from "lucide-react";
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

const ADV_LINES = [
  [[0,0],[0,1],[0,2]], [[1,0],[1,1],[1,2]], [[2,0],[2,1],[2,2]],
  [[0,0],[1,0],[2,0]], [[0,1],[1,1],[2,1]], [[0,2],[1,2],[2,2]],
  [[0,0],[1,1],[2,2]], [[0,2],[1,1],[2,0]],
];

const MINI_LINES = [
  [0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6],
];

// Positional weight: how many big-board winning lines pass through each board position
const POS_WEIGHT = [
  3, 2, 3,
  2, 4, 2,
  3, 2, 3,
];

function evaluateMiniBoard(sub: number[][]): number {
  const flat = sub.flat();
  let score = 0;
  for (const line of MINI_LINES) {
    const vals = line.map(i => flat[i]);
    const x = vals.filter(v => v === 1).length;
    const o = vals.filter(v => v === -1).length;
    if (x > 0 && o > 0) continue; // dead line
    if (x === 2) score += 6;
    else if (x === 1) score += 1;
    if (o === 2) score -= 6;
    else if (o === 1) score -= 1;
  }
  // Center control bonus
  if (flat[4] === 1) score += 2;
  else if (flat[4] === -1) score -= 2;
  return score;
}

function computeAdvantage(
  moves: GameMove[], board: number[][][][], boardResults: number[][],
  hoveredMoveIndex: number | null, isOver: boolean, winner: string | null | undefined,
): number {
  const r = hoveredMoveIndex != null ? replayBoardResults(moves, hoveredMoveIndex) : boardResults;
  const hoveredOver = hoveredMoveIndex != null && hoveredMoveIndex < moves.length - 1;
  const rBoard = hoveredMoveIndex != null ? replayBoard(moves, hoveredMoveIndex) : board;

  const showOver = isOver && !hoveredOver;
  if (showOver) {
    if (winner === "X") return 100;
    if (winner === "O") return 0;
    return 50;
  }

  // Flatten board results to 1D for easier indexing
  const flat = r.flat(); // 9 values: 1=X won, -1=O won, 0=open
  const boardDead: boolean[] = [];
  for (let a = 0; a < 3; a++) {
    for (let b = 0; b < 3; b++) {
      const idx = a * 3 + b;
      if (flat[idx] !== 0) { boardDead.push(true); continue; }
      const isFull = rBoard[a][b].every(row => row.every(v => v !== 0));
      boardDead.push(isFull);
    }
  }

  let score = 0;

  // 1. Big board line analysis
  for (const line of ADV_LINES) {
    const indices = line.map(([a, b]) => a * 3 + b);
    const vals = indices.map(i => flat[i]);
    const dead = indices.map(i => boardDead[i]);

    const xWon = vals.filter(v => v === 1).length;
    const oWon = vals.filter(v => v === -1).length;
    const drawn = indices.filter(i => flat[i] === 0 && dead[indices.indexOf(i)]).length;

    // Line is dead if both players have won a board in it, or drawn boards block it
    if (xWon > 0 && oWon > 0) continue;
    const blocked = drawn;

    if (oWon === 0 && blocked === 0) {
      if (xWon === 3) score += 1000; // shouldn't happen (game over), but safety
      else if (xWon === 2) score += 40;
      else if (xWon === 1) score += 8;
      else score += 1; // open line, slight value
    }
    if (xWon === 0 && blocked === 0) {
      if (oWon === 3) score -= 1000;
      else if (oWon === 2) score -= 40;
      else if (oWon === 1) score -= 8;
      else score -= 1;
    }
    // Partially blocked lines (drawn boards reduce value)
    if (oWon === 0 && blocked > 0 && xWon > 0) {
      score += xWon === 2 ? 10 : 2;
    }
    if (xWon === 0 && blocked > 0 && oWon > 0) {
      score -= oWon === 2 ? 10 : 2;
    }
  }

  // 2. Won board bonuses (weighted by position)
  for (let i = 0; i < 9; i++) {
    if (flat[i] === 1) score += 15 * POS_WEIGHT[i];
    else if (flat[i] === -1) score -= 15 * POS_WEIGHT[i];
  }

  // 3. Mini-board internal evaluation (for contested boards only)
  for (let a = 0; a < 3; a++) {
    for (let b = 0; b < 3; b++) {
      const idx = a * 3 + b;
      if (flat[idx] !== 0 || boardDead[idx]) continue;
      const miniScore = evaluateMiniBoard(rBoard[a][b]);
      // Weight by positional importance, but less than won boards
      score += miniScore * POS_WEIGHT[idx] * 0.3;
    }
  }

  // Normalize to 5-95 range (50 = even)
  // Empirical range: score roughly -300 to +300 in extreme cases
  const normalized = 50 + (score / 6);
  return Math.max(5, Math.min(95, Math.round(normalized)));
}

const BOARD_LABELS = ["A","B","C","D","E","F","G","H","I"];

function getMoveMetadata(
  moves: GameMove[], index: number, board: number[][][][], boardResults: number[][],
  isOver: boolean, winner: string | null | undefined,
): { sendsTo: string; delta: string } {
  const [, , c, d] = moves[index].move as [number, number, number, number];
  const targetBoard = c * 3 + d;

  // Compute "sends to"
  let sendsTo: string;
  if (index === moves.length - 1 && isOver) {
    sendsTo = "—";
  } else {
    // Check if target board is won/full after this move
    const boardAfter = replayBoard(moves, index);
    const resultsAfter = boardAfter.map(row => row.map(sub => checkSubWinner(sub)));
    const targetR = Math.floor(targetBoard / 3);
    const targetC = targetBoard % 3;
    const targetWon = resultsAfter[targetR][targetC] !== 0;
    const targetFull = !targetWon && boardAfter[targetR][targetC].every(r => r.every(v => v !== 0));
    sendsTo = (targetWon || targetFull) ? "Free" : BOARD_LABELS[targetBoard];
  }

  // Compute Δ advantage
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

  const [displayClocks, setDisplayClocks] = useState(() => {
    if (!state.clocks.X || !state.clocks.O) return state.clocks;
    const drift = Date.now() / 1000 - state.serverTime;
    return {
      X: state.activePlayer === "X" ? Math.max(0, state.clocks.X - drift) : state.clocks.X,
      O: state.activePlayer === "O" ? Math.max(0, state.clocks.O - drift) : state.clocks.O,
    };
  });
  const hasClock = state.clocks.X != null && state.clocks.O != null;

  const [elapsed, setElapsed] = useState({ X: 0, O: 0 });

  useEffect(() => {
    if (!state.clocks.X || !state.clocks.O) {
      setDisplayClocks(state.clocks);
      return;
    }
    const drift = Date.now() / 1000 - state.serverTime;
    setDisplayClocks({
      X: state.activePlayer === "X" ? Math.max(0, state.clocks.X - drift) : state.clocks.X,
      O: state.activePlayer === "O" ? Math.max(0, state.clocks.O - drift) : state.clocks.O,
    });
  }, [state.clocks, state.serverTime, state.activePlayer]);

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
