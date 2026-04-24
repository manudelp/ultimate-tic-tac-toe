import React, { useEffect, useRef, useState } from "react";
import MiniBoard from "@/components/core/miniboard";
import { motion } from "framer-motion";
import { formatMove } from "@/lib/notation";
import { ArrowLeft, Flag } from "lucide-react";
import type { GameState, GameMove } from "@/types/game";

interface BoardProps {
  state: GameState;
  myPlayer: "X" | "O";
  opponent?: { type: "bot"; name: string; icon: string } | null;
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

const Board: React.FC<BoardProps> = ({ state, myPlayer, opponent, onCellClick, onResign, onExit }) => {
  const [isMobile, setIsMobile] = useState(false);
  const moveHistoryRef = useRef<HTMLDivElement>(null);
  const [hoveredMove, setHoveredMove] = useState<[number, number, number, number] | null>(null);

  const isMyTurn = state.activePlayer === myPlayer;
  const isOver = state.status !== "ongoing";
  const lastMove = state.moves.length > 0 ? state.moves[state.moves.length - 1].move as [number, number, number, number] : null;
  const winningLine = isOver && state.winner ? getWinningLine(state.boardResults) : null;

  // Derive winners and disabled from server boardResults
  const winners: (string | null)[][] = state.boardResults.map(row =>
    row.map(v => boardResultStr(v))
  );

  // A board is disabled if it has a result OR if it's full
  const disabled: boolean[][] = state.board.map((row, a) =>
    row.map((sub, b) => {
      if (state.boardResults[a][b] !== 0) return true;
      // Check if full
      for (let c = 0; c < 3; c++)
        for (let d = 0; d < 3; d++)
          if (sub[c][d] === 0) return false;
      return true;
    })
  );

  // Convert numeric board to string board for MiniBoard
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
    if (!isMyTurn) return;
    onCellClick(a, b, c, d);
  };

  // Local clock ticker — visual only, server is authoritative
  const [displayClocks, setDisplayClocks] = useState(state.clocks);

  useEffect(() => {
    setDisplayClocks(state.clocks);
  }, [state.clocks]);

  useEffect(() => {
    if (isOver) return;
    const interval = setInterval(() => {
      setDisplayClocks((prev) => ({
        ...prev,
        [state.activePlayer]: Math.max(0, prev[state.activePlayer] - 0.1),
      }));
    }, 100);
    return () => clearInterval(interval);
  }, [state.activePlayer, isOver]);

  const formatClock = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="relative flex flex-col w-full gap-6 mx-auto sm:px-4 max-w-7xl md:flex-row">
      <div className="flex flex-col items-center flex-1">
        {/* Info Bar */}
        <div className="flex items-center justify-between w-full px-4 py-3 mb-4 bg-gray-800 rounded">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 flex items-center justify-center rounded-md ${
              state.activePlayer === "X" ? "bg-blue-500/20" : "bg-red-500/20"
            }`}>
              <span className={`text-2xl font-bold ${
                state.activePlayer === "X" ? "text-blue-400" : "text-red-400"
              }`}>
                {state.activePlayer}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-gray-400">
                {isOver ? "Game Over" : isMyTurn ? "Your turn" : opponent ? `${opponent.icon} ${opponent.name}'s turn` : "Opponent's turn"}
              </span>
              {isOver && state.winner && (
                <span className="text-sm font-semibold text-green-400">
                  {state.winner === myPlayer ? "You win!" : "You lose"}
                </span>
              )}
              {isOver && !state.winner && (
                <span className="text-sm font-semibold text-yellow-400">Draw</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm font-mono">
            <span className={state.activePlayer === "X" ? "text-blue-400" : "text-gray-500"}>
              {formatClock(displayClocks.X)}
            </span>
            <span className="text-gray-600">|</span>
            <span className={state.activePlayer === "O" ? "text-red-400" : "text-gray-500"}>
              {formatClock(displayClocks.O)}
            </span>
          </div>
        </div>

        {/* Board */}
        <div className="relative w-full max-w-[min(calc(100vw-2rem),600px)] aspect-square">
          <div className="relative grid grid-cols-3 grid-rows-3 w-full aspect-square">
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
                  lastMove={lastMove}
                  gameOver={isOver}
                  hoveredMove={hoveredMove}
                  handleCellClick={handleCellClick}
                />
              ))
            )}

            {winningLine && (
              <div className="absolute inset-0 pointer-events-none flex justify-center items-center">
                {winningLine.type === "row" && (
                  <div className="absolute w-[95%] h-[3px] bg-gradient-to-r from-red-500 to-orange-500 rounded-full" style={{ top: `${(100 / 3) * winningLine.index + 50 / 3}%` }} />
                )}
                {winningLine.type === "col" && (
                  <div className="absolute h-[95%] w-[3px] bg-gradient-to-b from-red-500 to-orange-500 rounded-full" style={{ left: `${(100 / 3) * winningLine.index + 50 / 3}%` }} />
                )}
                {winningLine.type === "diag" && winningLine.index === 0 && (
                  <div className="absolute w-[130%] h-[3px] bg-gradient-to-r from-red-500 to-orange-500 rounded-full" style={{ transform: "rotate(45deg)" }} />
                )}
                {winningLine.type === "diag" && winningLine.index === 1 && (
                  <div className="absolute w-[130%] h-[3px] bg-gradient-to-r from-red-500 to-orange-500 rounded-full" style={{ transform: "rotate(-45deg)" }} />
                )}
              </div>
            )}
          </div>
        </div>

        {/* Mobile move history */}
        {isMobile && state.moves.length > 0 && (
          <div className="w-full mt-4">
            <div ref={moveHistoryRef} className="w-full px-1 py-2 overflow-x-auto bg-gray-800 rounded scrollbar-thin scrollbar-thumb-gray-600">
              <div className="inline-flex gap-2 px-2">
                {state.moves.map((move: GameMove, i: number) => (
                  <div
                    key={i}
                    className={`cursor-pointer rounded-md px-2 py-1 text-xs ${
                      i === state.moves.length - 1 ? "bg-gray-700" : "hover:bg-gray-700/50"
                    }`}
                    onMouseEnter={() => setHoveredMove(move.move as [number, number, number, number])}
                    onMouseLeave={() => setHoveredMove(null)}
                  >
                    <span className="text-gray-400">{i + 1}.</span>
                    <span className={move.player === "X" ? "text-blue-400" : "text-red-400"}>
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
            <button onClick={onExit} className="flex-1 flex items-center justify-center gap-2 py-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              <ArrowLeft className="w-4 h-4" /> Exit
            </button>
            {!isOver && (
              <button onClick={onResign} className="flex-1 flex items-center justify-center gap-2 py-3 bg-red-800 rounded hover:bg-red-700 transition-colors">
                <Flag className="w-4 h-4" /> Resign
              </button>
            )}
          </div>
        )}
      </div>

      {/* Desktop side panel */}
      {!isMobile && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex flex-col gap-4 w-72 h-[calc(100svh-4rem)] overflow-hidden">
          {/* Clocks */}
          <div className="p-4 bg-gray-800 rounded space-y-2">
            {opponent && (
              <div className="flex items-center gap-2 pb-2 border-b border-gray-700">
                <span className="text-lg">{opponent.icon}</span>
                <span className="text-sm font-medium">vs {opponent.name}</span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Move {state.moves.length + 1}</span>
              <span className="text-xs text-gray-500">{state.status === "ongoing" ? "In progress" : state.status}</span>
            </div>
          </div>

          {/* Move history */}
          <div className="flex-1 min-h-0 flex flex-col p-4 bg-gray-800 rounded">
            <div className="flex justify-between mb-2 text-sm text-gray-400">
              <span>Moves</span>
              <span className="text-xs">{state.moves.length}</span>
            </div>
            <div ref={moveHistoryRef} className="flex-1 min-h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-800">
                  <tr className="text-xs text-gray-400">
                    <th className="p-1.5 text-left w-8">#</th>
                    <th className="p-1.5 text-center w-10">Player</th>
                    <th className="p-1.5 text-right">Move</th>
                  </tr>
                </thead>
                <tbody>
                  {state.moves.map((move: GameMove, i: number) => (
                    <tr
                      key={i}
                      className={`hover:bg-gray-700/50 cursor-pointer ${i === state.moves.length - 1 ? "bg-gray-700/30" : ""}`}
                      onMouseEnter={() => setHoveredMove(move.move as [number, number, number, number])}
                      onMouseLeave={() => setHoveredMove(null)}
                    >
                      <td className="p-1.5 text-gray-500">{i + 1}</td>
                      <td className={`p-1.5 text-center font-medium ${move.player === "X" ? "text-blue-400" : "text-red-400"}`}>
                        {move.player}
                      </td>
                      <td className="p-1.5 text-right">{formatMove(move.move as [number, number, number, number])}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Controls */}
          <div className="flex gap-2">
            <button onClick={onExit} className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              <ArrowLeft className="w-4 h-4" /> Exit
            </button>
            {!isOver && (
              <button onClick={onResign} className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-800 rounded hover:bg-red-700 transition-colors">
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
