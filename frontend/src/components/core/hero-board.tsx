"use client";
import { useEffect, useState } from "react";

const SCRIPT: [number, number, number, number, "X" | "O"][] = [
  [2, 1, 1, 2, "X"],   [1, 2, 2, 0, "O"],   [2, 0, 0, 0, "X"],   [0, 0, 1, 2, "O"],
  [1, 2, 1, 0, "X"],   [1, 0, 0, 0, "O"],   [0, 0, 2, 2, "X"],   [2, 2, 0, 1, "O"],
  [0, 1, 0, 2, "X"],   [0, 2, 1, 1, "O"],   [1, 1, 1, 1, "X"],   [1, 1, 1, 2, "O"],
  [1, 2, 0, 0, "X"],   [0, 0, 1, 1, "O"],   [1, 1, 0, 2, "X"],   [0, 2, 2, 2, "O"],
  [2, 2, 2, 1, "X"],   [2, 1, 1, 1, "O"],   [1, 1, 2, 0, "X"],   [2, 0, 1, 0, "O"],
  [1, 0, 2, 1, "X"],   [2, 1, 1, 0, "O"],   [1, 0, 0, 1, "X"],   [0, 1, 1, 0, "O"],
  [1, 0, 1, 1, "X"],   [0, 2, 2, 1, "O"],   [2, 1, 0, 2, "X"],   [0, 2, 0, 1, "O"],
  [0, 1, 0, 0, "X"],   [0, 0, 0, 2, "O"],   [2, 0, 1, 2, "X"],   [1, 2, 1, 1, "O"],
  [2, 1, 2, 2, "X"],   [2, 2, 1, 1, "O"],   [0, 1, 0, 1, "X"],
];

const LINES = [
  [[0,0],[0,1],[0,2]], [[1,0],[1,1],[1,2]], [[2,0],[2,1],[2,2]],
  [[0,0],[1,0],[2,0]], [[0,1],[1,1],[2,1]], [[0,2],[1,2],[2,2]],
  [[0,0],[1,1],[2,2]], [[0,2],[1,1],[2,0]],
];

type Board = (string | null)[][][][];

function emptyBoard(): Board {
  return Array.from({ length: 3 }, () =>
    Array.from({ length: 3 }, () =>
      Array.from({ length: 3 }, () => Array(3).fill(null))
    )
  );
}

function checkWinner(mini: (string | null)[][]): string | null {
  for (const line of LINES) {
    const [a, b, c] = line;
    const v = mini[a[0]][a[1]];
    if (v && v === mini[b[0]][b[1]] && v === mini[c[0]][c[1]]) return v;
  }
  return null;
}

function getWinningLine(results: (string | null)[][]): { type: "row" | "col" | "diag"; index: number } | null {
  for (let i = 0; i < 3; i++) {
    if (results[i][0] && results[i][0] === results[i][1] && results[i][1] === results[i][2])
      return { type: "row", index: i };
    if (results[0][i] && results[0][i] === results[1][i] && results[1][i] === results[2][i])
      return { type: "col", index: i };
  }
  if (results[0][0] && results[0][0] === results[1][1] && results[1][1] === results[2][2])
    return { type: "diag", index: 0 };
  if (results[0][2] && results[0][2] === results[1][1] && results[1][1] === results[2][0])
    return { type: "diag", index: 1 };
  return null;
}

export default function HeroBoard() {
  const [board, setBoard] = useState<Board>(emptyBoard);
  const [moveIndex, setMoveIndex] = useState(0);
  const [lastMove, setLastMove] = useState<[number, number, number, number] | null>(null);
  const [winners, setWinners] = useState<(string | null)[][]>(
    Array.from({ length: 3 }, () => Array(3).fill(null))
  );
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    // Game finished — show winning line, then reset after delay
    if (gameOver) {
      const t = setTimeout(() => {
        setBoard(emptyBoard());
        setMoveIndex(0);
        setLastMove(null);
        setWinners(Array.from({ length: 3 }, () => Array(3).fill(null)));
        setGameOver(false);
      }, 4000);
      return () => clearTimeout(t);
    }

    if (moveIndex >= SCRIPT.length) return;

    const t = setTimeout(() => {
      const [br, bc, cr, cc, player] = SCRIPT[moveIndex];
      setBoard(prev => {
        const next = prev.map(r => r.map(b => b.map(row => [...row])));
        next[br][bc][cr][cc] = player;

        const w = checkWinner(next[br][bc]);
        if (w) {
          setWinners(prev => {
            const nw = prev.map(r => [...r]);
            nw[br][bc] = w;

            // Check if the big board is won
            if (getWinningLine(nw)) {
              setGameOver(true);
            }
            return nw;
          });
        }

        return next;
      });
      setLastMove([br, bc, cr, cc]);
      setMoveIndex(i => i + 1);
    }, 600);

    return () => clearTimeout(t);
  }, [moveIndex, gameOver]);

  // Derive forced board like the engine: if target is won/full, it's free choice (null)
  const activeBoard: [number, number] | null = (() => {
    if (!lastMove) return null;
    const [,, cr, cc] = lastMove;
    // Target board is not playable if it's won or full
    if (winners[cr][cc]) return null;
    const target = board[cr][cc];
    const isFull = target.every(row => row.every(cell => cell !== null));
    if (isFull) return null;
    return [cr, cc];
  })();
  const winningLine = gameOver ? getWinningLine(winners) : null;

  return (
    <div className="relative grid grid-cols-3 gap-1.5 sm:gap-2.5 w-[340px] sm:w-[400px] h-[340px] sm:h-[400px] select-none">
      {board.map((boardRow, br) =>
        boardRow.map((miniBoard, bc) => {
          const winner = winners[br][bc];
          const isActive = gameOver || !activeBoard || (activeBoard[0] === br && activeBoard[1] === bc);

          return (
            <div
              key={`${br}-${bc}`}
              className={`relative bg-gray-700/30 rounded-md p-0.5 sm:p-1 transition-opacity duration-500 ${
                isActive ? "opacity-100" : "opacity-30"
              }`}
            >
              <div className={`grid grid-cols-3 gap-px ${winner ? "opacity-0" : ""} transition-opacity duration-300`}>
                {miniBoard.map((row, cr) =>
                  row.map((cell, cc) => {
                    const isLast = lastMove &&
                      lastMove[0] === br && lastMove[1] === bc &&
                      lastMove[2] === cr && lastMove[3] === cc;

                    return (
                      <div
                        key={`${cr}-${cc}`}
                        className={`aspect-square rounded-sm flex items-center justify-center transition-all duration-300 ${
                          isLast
                            ? cell === "X" ? "bg-blue-500/25" : "bg-red-500/25"
                            : "bg-gray-800/50"
                        }`}
                      >
                        {cell && (
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            strokeWidth="2"
                            stroke="currentColor"
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className={`w-[65%] h-[65%] ${
                              cell === "X" ? "text-[#71a2f6]" : "text-[#f2756f]"
                            } ${isLast ? "animate-[popIn_0.3s_ease-out]" : ""}`}
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
                <div className="absolute inset-0 flex items-center justify-center animate-[popIn_0.3s_ease-out]">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className={`w-3/5 h-3/5 ${
                      winner === "X" ? "text-[#71a2f6]" : "text-[#f2756f]"
                    }`}
                  >
                    {winner === "X" ? (
                      <><path d="M18 6l-12 12" /><path d="M6 6l12 12" /></>
                    ) : (
                      <circle cx="12" cy="12" r="7.5" />
                    )}
                  </svg>
                </div>
              )}
            </div>
          );
        })
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
  );
}
