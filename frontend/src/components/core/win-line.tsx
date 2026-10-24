import React from "react";
import type { WinningLine } from "@/lib/game-view";

/** The green stroke drawn through a won big board. Fills its positioned parent. */
const WinLine: React.FC<{ line: WinningLine | null }> = ({ line }) => {
  if (!line) return null;
  const offset = `${(100 / 3) * line.index + 50 / 3}%`;
  return (
    <div className="absolute inset-0 pointer-events-none">
      {line.type === "row" && (
        <div
          className="absolute left-[2.5%] w-[95%] h-[5px] bg-green-500 rounded-full"
          style={{ top: offset, animation: "winLineRow 0.5s ease-out forwards" }}
        />
      )}
      {line.type === "col" && (
        <div
          className="absolute top-[2.5%] h-[95%] w-[5px] bg-green-500 rounded-full"
          style={{ left: offset, animation: "winLineCol 0.5s ease-out forwards" }}
        />
      )}
      {line.type === "diag" && (
        <div
          className="absolute w-[130%] h-[5px] bg-green-500 rounded-full"
          style={{
            top: "50%",
            left: "50%",
            animation: `winLineDiag${line.index} 0.5s ease-out forwards`,
          }}
        />
      )}
    </div>
  );
};

export default WinLine;
