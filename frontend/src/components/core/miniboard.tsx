import React, { useState } from "react";

interface MiniBoardProps {
  miniBoard: string[][];
  localRowIndex: number;
  localColIndex: number;
  winners: (string | null)[][];
  disabled: boolean[][];
  activeMiniBoard: [number, number] | null;
  activePlayer: "X" | "O";
  lastMove: [number, number, number, number] | null;
  gameOver: boolean;
  hoveredMove: [number, number, number, number] | null;
  handleCellClick: (a: number, b: number, c: number, d: number) => void;
}

const MiniBoard: React.FC<MiniBoardProps> = ({
  miniBoard, localRowIndex, localColIndex, winners, disabled,
  activeMiniBoard, activePlayer, lastMove, gameOver, hoveredMove, handleCellClick,
}) => {
  const [hovered, setHovered] = useState(false);
  const winner = winners?.[localRowIndex]?.[localColIndex];

  const isInactive =
    !gameOver &&
    (disabled?.[localRowIndex]?.[localColIndex] ||
      (activeMiniBoard !== null &&
        (activeMiniBoard[0] !== localRowIndex || activeMiniBoard[1] !== localColIndex)));

  const isActive = !isInactive && !gameOver;

  const revealCells = hovered ||
    (hoveredMove !== null &&
      hoveredMove[0] === localRowIndex && hoveredMove[1] === localColIndex);

  // Board state → structure + contrast, never opacity
  const boardClasses = isActive
    ? activePlayer === "X"
      ? "bg-blue-500/10 ring-2 ring-blue-500/40"
      : "bg-red-500/10 ring-2 ring-red-500/40"
    : "bg-[hsl(var(--board-bg))]";

  return (
    <div
      className={`relative rounded-md p-0.5 sm:p-1 transition-colors duration-300 ${boardClasses} ${
        isInactive ? "pointer-events-none" : ""
      }`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Grid: gap reveals board bg as grid lines — always visible */}
      <div className={`grid grid-cols-3 gap-px transition-opacity duration-300 ${
        winner && !revealCells ? "opacity-0" : "opacity-100"
      }`}>
        {miniBoard.map((row, rowIndex) =>
          row.map((cell, cellIndex) => {
            const isMoveHovered = hoveredMove &&
              hoveredMove[0] === localRowIndex && hoveredMove[1] === localColIndex &&
              hoveredMove[2] === rowIndex && hoveredMove[3] === cellIndex;

            const isLastMove = lastMove &&
              lastMove[0] === localRowIndex && lastMove[1] === localColIndex &&
              lastMove[2] === rowIndex && lastMove[3] === cellIndex;

            return (
              <div
                key={`${rowIndex}-${cellIndex}`}
                onClick={() => handleCellClick(localRowIndex, localColIndex, rowIndex, cellIndex)}
                className={`aspect-square rounded-sm flex items-center justify-center cursor-pointer transition-colors duration-200 ${
                  isMoveHovered ? "bg-green-500/20"
                    : isLastMove ? (cell === "X" ? "bg-blue-500/20" : "bg-red-500/20")
                    : isActive ? "bg-[hsl(var(--board-cell))] hover:bg-[hsl(var(--board-cell-hover))]" : "bg-[hsl(var(--board-cell))]"
                }`}
              >
                {cell && (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    strokeWidth="1"
                    stroke="currentColor"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className={`w-[65%] h-[65%] ${
                      cell === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"
                    }`}
                  >
                    {cell === "X" ? (
                      <><path d="M18 6l-12 12" /><path d="M6 6l12 12" /></>
                    ) : (
                      <circle cx="12" cy="12" r="7.5" />
                    )}
                  </svg>
                )}
              </div>
            );
          })
        )}
      </div>

      {winner && (
        <div
          className={`absolute inset-0 flex items-center justify-center transition-opacity duration-300 pointer-events-none ${
            revealCells ? "opacity-0" : "opacity-100"
          }`}
        >
          {winner === "draw" ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
              fill="none"
              strokeLinecap="round"
              className="w-3/5 h-3/5 text-muted-foreground"
            >
              <path d="M5 12h14" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              className={`w-3/5 h-3/5 ${
                winner === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"
              }`}
            >
              {winner === "X" ? (
                <><path d="M18 6l-12 12" /><path d="M6 6l12 12" /></>
              ) : (
                <circle cx="12" cy="12" r="7.5" />
              )}
            </svg>
          )}
        </div>
      )}
    </div>
  );
};

export default MiniBoard;
