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
  hoveredMove: [number, number, number, number] | null;
  handleCellClick: (a: number, b: number, c: number, d: number) => void;
}

const MiniBoard: React.FC<MiniBoardProps> = ({
  miniBoard, localRowIndex, localColIndex, winners, disabled,
  activeMiniBoard, lastMove, gameOver, hoveredMove, handleCellClick,
}) => {
  const winner = winners?.[localRowIndex]?.[localColIndex];

  const isInactive =
    !gameOver &&
    (disabled?.[localRowIndex]?.[localColIndex] ||
      (activeMiniBoard !== null &&
        (activeMiniBoard[0] !== localRowIndex || activeMiniBoard[1] !== localColIndex)));

  const isActive = !isInactive && !gameOver;
  const hasForcedBoard = activeMiniBoard !== null;
  const outerBorderColor = hasForcedBoard ? "rgba(255,255,255,0.15)" : "white";
  const innerBorderColor = isActive ? "white" : "rgba(255,255,255,0.1)";

  return (
    <div
      className={`p-1 sm:p-2 transition relative bg-gray-900 ${isInactive ? "pointer-events-none" : ""}`}
      style={{
        borderTop: localRowIndex === 1 ? `2px solid ${outerBorderColor}` : "none",
        borderBottom: localRowIndex === 1 ? `2px solid ${outerBorderColor}` : "none",
        borderLeft: localColIndex === 1 ? `2px solid ${outerBorderColor}` : "none",
        borderRight: localColIndex === 1 ? `2px solid ${outerBorderColor}` : "none",
      }}
    >
      <div className={`w-full h-full ${isInactive ? "opacity-25" : ""}`}>
      {miniBoard.map((row, rowIndex) => (
        <div key={rowIndex} className="flex flex-wrap h-1/3">
          {row.map((cell, cellIndex) => {
            const isHovered = hoveredMove &&
              hoveredMove[0] === localRowIndex && hoveredMove[1] === localColIndex &&
              hoveredMove[2] === rowIndex && hoveredMove[3] === cellIndex;

            const isLastMove = lastMove &&
              lastMove[0] === localRowIndex && lastMove[1] === localColIndex &&
              lastMove[2] === rowIndex && lastMove[3] === cellIndex;

            const borderColor = innerBorderColor;

            return (
              <div
                key={cellIndex}
                onClick={() => handleCellClick(localRowIndex, localColIndex, rowIndex, cellIndex)}
                className={`w-1/3 h-full grid place-items-center cursor-pointer hover:bg-white/10 ${
                  isHovered ? "bg-green-500/20"
                    : isLastMove ? (cell === "X" ? "bg-indigo-400/20" : "bg-red-400/20")
                    : ""
                }`}
                style={{
                  borderTop: rowIndex === 1 ? `1px solid ${borderColor}` : "none",
                  borderBottom: rowIndex === 1 ? `1px solid ${borderColor}` : "none",
                  borderLeft: cellIndex === 1 ? `1px solid ${borderColor}` : "none",
                  borderRight: cellIndex === 1 ? `1px solid ${borderColor}` : "none",
                }}
              >
                <div className="flex items-center justify-center w-10/12 h-10/12">
                  {cell === "X" && <X className="text-[#71a2f6] w-full h-full" />}
                  {cell === "O" && <O className="text-[#f2756f] w-full h-full" />}
                </div>
              </div>
            );
          })}
        </div>
      ))}

      </div>

      {winner && (
        <div
          className={`absolute inset-0 flex items-center justify-center bg-gray-900 transition-opacity pointer-events-none ${
            hoveredMove && hoveredMove[0] === localRowIndex && hoveredMove[1] === localColIndex
              ? "opacity-0" : "opacity-100"
          }`}
        >
          <div className="grid pointer-events-auto place-items-center">
            {winner === "X" ? <X className="text-[#71a2f6]" />
              : winner === "O" ? <O className="text-[#f2756f]" />
              : <Draw />}
          </div>
        </div>
      )}
    </div>
  );
};

export default MiniBoard;
