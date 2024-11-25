import React from "react";
import X from "../ui/playerx";
import O from "../ui/playero";
import Draw from "../ui/draw";

interface MiniBoardProps {
  miniBoard: string[][];
  localRowIndex: number;
  localColIndex: number;
  winners: (string | null)[][];
  disabled: boolean[][];
  activeMiniBoard: [number, number] | null;
  lastMove: [number, number, number, number] | null;
  gameOver: boolean;
  hoveredMove: [number, number, number, number] | null; // Global hover state
  handleCellClick: (
    localRowIndex: number,
    localColIndex: number,
    rowIndex: number,
    cellIndex: number
  ) => void;
  makeMove: (ooords: [number, number, number, number]) => void;
}

const MiniBoard: React.FC<MiniBoardProps> = ({
  miniBoard,
  localRowIndex,
  localColIndex,
  winners,
  disabled,
  activeMiniBoard,
  lastMove,
  gameOver,
  hoveredMove,
  handleCellClick,
}) => {
  const winner = winners?.[localRowIndex]?.[localColIndex];

  // Function to determine the line of the winning cells (row, column, diagonal)
  const getWinningLine = () => {
    if (!winner) return [];

    const winningLine: number[][] = [];

    // Check for horizontal lines
    for (let row = 0; row < 3; row++) {
      if (
        miniBoard[row][0] === winner &&
        miniBoard[row][1] === winner &&
        miniBoard[row][2] === winner
      ) {
        winningLine.push([row, 0], [row, 1], [row, 2]);
      }
    }

    // Check for vertical lines
    for (let col = 0; col < 3; col++) {
      if (
        miniBoard[0][col] === winner &&
        miniBoard[1][col] === winner &&
        miniBoard[2][col] === winner
      ) {
        winningLine.push([0, col], [1, col], [2, col]);
      }
    }

    // Check for diagonal lines
    if (
      miniBoard[0][0] === winner &&
      miniBoard[1][1] === winner &&
      miniBoard[2][2] === winner
    ) {
      winningLine.push([0, 0], [1, 1], [2, 2]);
    }

    if (
      miniBoard[0][2] === winner &&
      miniBoard[1][1] === winner &&
      miniBoard[2][0] === winner
    ) {
      winningLine.push([0, 2], [1, 1], [2, 0]);
    }

    return winningLine;
  };

  // Get the winning line for the mini-board
  const winningLine = getWinningLine();

  return (
    <div
      className={`w-1/3 h-1/3 p-2 sm:p-4 transition relative ${
        (disabled?.[localRowIndex]?.[localColIndex] ||
          (activeMiniBoard !== null &&
            (activeMiniBoard?.[0] !== localRowIndex ||
              activeMiniBoard?.[1] !== localColIndex))) &&
        !gameOver
          ? "opacity-25 pointer-events-none"
          : ""
      }`}
      style={{
        borderTop: localRowIndex === 1 ? `2px solid white` : "none",
        borderBottom: localRowIndex === 1 ? `2px solid white` : "none",
        borderLeft: localColIndex === 1 ? `2px solid white` : "none",
        borderRight: localColIndex === 1 ? `2px solid white` : "none",
        ...(window.innerWidth < 768 && {
          borderTop: localRowIndex === 1 ? `3px solid white` : "none",
          borderBottom: localRowIndex === 1 ? `3px solid white` : "none",
          borderLeft: localColIndex === 1 ? `3px solid white` : "none",
          borderRight: localColIndex === 1 ? `3px solid white` : "none",
        }),
        ...(lastMove &&
        !(
          disabled?.[localRowIndex]?.[localColIndex] ||
          (activeMiniBoard !== null &&
            (activeMiniBoard?.[0] !== localRowIndex ||
              activeMiniBoard?.[1] !== localColIndex))
        )
          ? {
              borderTop: localRowIndex === 1 ? `2px solid #4d525d` : "none",
              borderBottom: localRowIndex === 1 ? `2px solid #4d525d` : "none",
              borderLeft: localColIndex === 1 ? `2px solid #4d525d` : "none",
              borderRight: localColIndex === 1 ? `2px solid #4d525d` : "none",
            }
          : {}),
      }}
    >
      {miniBoard.map((row: string[], rowIndex: number) => (
        <div key={rowIndex} className="h-1/3 flex flex-wrap">
          {row.map((cell: string, cellIndex: number) => {
            // Apply hover effect based on global hoveredMove
            const isHovered =
              hoveredMove &&
              hoveredMove[0] === localRowIndex &&
              hoveredMove[1] === localColIndex &&
              hoveredMove[2] === rowIndex &&
              hoveredMove[3] === cellIndex;

            const isWinningCell = winningLine.some(
              (line) => line[0] === rowIndex && line[1] === cellIndex
            );

            return (
              <div
                onClick={() =>
                  handleCellClick(
                    localRowIndex,
                    localColIndex,
                    rowIndex,
                    cellIndex
                  )
                }
                key={cellIndex}
                className={`w-1/3 h-full grid place-items-center text-white text-xl cursor-pointer hover:bg-red-500 ${
                  isHovered
                    ? "bg-green-500"
                    : lastMove &&
                      lastMove[0] === localRowIndex &&
                      lastMove[1] === localColIndex &&
                      lastMove[2] === rowIndex &&
                      lastMove[3] === cellIndex
                    ? "bg-indigo-400"
                    : isWinningCell
                    ? "bg-yellow-500"
                    : disabled?.[localRowIndex]?.[localColIndex] && !gameOver
                    ? "pointer-events-none"
                    : ""
                }`}
                style={{
                  borderTop: rowIndex === 1 ? `2px solid white` : "none",
                  borderBottom: rowIndex === 1 ? `2px solid white` : "none",
                  borderLeft: cellIndex === 1 ? `2px solid white` : "none",
                  borderRight: cellIndex === 1 ? `2px solid white` : "none",
                }}
              >
                {cell === "X" && <X theme={"dark"} />}
                {cell === "O" && <O theme={"dark"} />}
              </div>
            );
          })}
        </div>
      ))}

      {winner && (
        <div
          className={`absolute inset-0 flex items-center justify-center bg-gray-900 opacity-100 hover:opacity-0 pointer-events-none transition-opacity ${
            hoveredMove &&
            hoveredMove[0] === localRowIndex &&
            hoveredMove[1] === localColIndex
              ? "opacity-10"
              : "opacity-100"
          }`}
        >
          <div className="pointer-events-auto grid place-items-center">
            {winner === "X" ? (
              <X theme={"dark"} />
            ) : winner === "O" ? (
              <O theme={"dark"} />
            ) : (
              <Draw theme={"dark"} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MiniBoard;
