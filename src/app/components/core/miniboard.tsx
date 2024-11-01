import React from "react";
import X from "../ui/playerx";
import O from "../ui/playero";

interface MiniBoardProps {
  miniBoard: string[][];
  localRowIndex: number;
  localColIndex: number;
  winners: (string | null)[][];
  disabled: boolean[][];
  activeMiniBoard: [number, number] | null;
  lastMove: [number, number, number, number] | null;
  handleCellClick: (
    localRowIndex: number,
    localColIndex: number,
    rowIndex: number,
    cellIndex: number
  ) => void;
}

const MiniBoard: React.FC<MiniBoardProps> = ({
  miniBoard,
  localRowIndex,
  localColIndex,
  winners,
  disabled,
  activeMiniBoard,
  lastMove,
  handleCellClick,
}) => {
  const winner = winners?.[localRowIndex]?.[localColIndex];
  return (
    <div
      className={`w-1/3 h-1/3 p-4 transition ${
        disabled?.[localRowIndex]?.[localColIndex] ||
        (activeMiniBoard !== null &&
          (activeMiniBoard?.[0] !== localRowIndex ||
            activeMiniBoard?.[1] !== localColIndex))
          ? "opacity-50 pointer-events-none"
          : ""
      } ${
        winner === "X"
          ? "bg-green-500"
          : winner === "O"
          ? "bg-blue-500"
          : winner === "Draw"
          ? "bg-red-500"
          : "bg-transparent"
      }`}
      style={{
        borderTop: localRowIndex < 1 ? "none" : `1px solid white`,
        borderBottom: localRowIndex >= 2 ? "none" : `1px solid white`,
        borderLeft: localColIndex % 3 === 0 ? "none" : `1px solid white`,
        borderRight: localColIndex % 3 === 2 ? "none" : `1px solid white`,
      }}
    >
      {miniBoard.map((row, rowIndex) => (
        <div key={rowIndex} className="h-1/3 flex flex-wrap">
          {row.map((cell, cellIndex) => (
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
              className={`w-1/3 h-full grid place-items-center text-white text-xl border border-red-700 cursor-pointer hover:bg-red-500 ${
                lastMove &&
                lastMove[0] === localRowIndex &&
                lastMove[1] === localColIndex &&
                lastMove[2] === rowIndex &&
                lastMove[3] === cellIndex
                  ? "bg-indigo-400"
                  : ""
              } ${
                disabled?.[localRowIndex]?.[localColIndex]
                  ? "pointer-events-none"
                  : ""
              }`}
              style={{
                borderTop: rowIndex === 0 ? "none" : `1px solid white`,
                borderBottom: rowIndex === 2 ? "none" : `1px solid white`,
                borderLeft: cellIndex === 0 ? "none" : `1px solid white`,
                borderRight: cellIndex === 2 ? "none" : `1px solid white`,
              }}
            >
              {cell === "X" && <X theme={"dark"} />}
              {cell === "O" && <O theme={"dark"} />}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

interface MiniBoardProps {
  miniBoard: string[][];
  localRowIndex: number;
  localColIndex: number;
  winners: (string | null)[][];
  disabled: boolean[][];
  activeMiniBoard: [number, number] | null;
  lastMove: [number, number, number, number] | null;
  handleCellClick: (a: number, b: number, c: number, d: number) => void;
  makeMove: (coords: [number, number, number, number]) => void;
}

export default MiniBoard;
