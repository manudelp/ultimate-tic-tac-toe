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
  handleCellClick,
}) => {
  const winner = winners?.[localRowIndex]?.[localColIndex];
  return (
    <div
      className={`w-1/3 h-1/3 p-2 sm:p-4 transition relative ${
        disabled?.[localRowIndex]?.[localColIndex] ||
        (activeMiniBoard !== null &&
          (activeMiniBoard?.[0] !== localRowIndex ||
            activeMiniBoard?.[1] !== localColIndex))
          ? "opacity-25 pointer-events-none"
          : ""
      }`}
      style={{
        borderTop: localRowIndex === 1 ? `2px solid white` : "none",
        borderBottom: localRowIndex === 1 ? `2px solid white` : "none",
        borderLeft: localColIndex === 1 ? `2px solid white` : "none",
        borderRight: localColIndex === 1 ? `2px solid white` : "none",
        ...(window.innerWidth < 768 && {
          borderTop: localRowIndex === 1 ? `2px solid white` : "none",
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
          {row.map((cell: string, cellIndex: number) => (
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
                borderTop: rowIndex === 1 ? `2px solid white` : "none",
                borderBottom: rowIndex === 1 ? `2px solid white` : "none",
                borderLeft: cellIndex === 1 ? `2px solid white` : "none",
                borderRight: cellIndex === 1 ? `2px solid white` : "none",
                ...(window.innerWidth < 768 && {
                  borderTop: rowIndex === 1 ? `1px solid white` : "none",
                  borderBottom: rowIndex === 1 ? `1px solid white` : "none",
                  borderLeft: cellIndex === 1 ? `1px solid white` : "none",
                  borderRight: cellIndex === 1 ? `1px solid white` : "none",
                }),
              }}
            >
              {cell === "X" && <X theme={"dark"} />}
              {cell === "O" && <O theme={"dark"} />}
            </div>
          ))}
        </div>
      ))}

      {winner && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 opacity-100 hover:opacity-0 pointer-events-none transition-opacity">
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
