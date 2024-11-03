// src/app/components/layout/dashboard.tsx
import React, { useState } from "react";
import Board from "@/app/components/core/board";

const Dashboard: React.FC = () => {
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [starts, setStarts] = useState<string | null>(null);
  const [totalGames, setTotalGames] = useState<number | null>(null);
  const [resetBoard, setResetBoard] = useState<boolean>(false);

  const selectMode = (mode: string) => {
    setGameMode(mode);
    setResetBoard(true);
    setStarts(null);
    setTotalGames(null);
  };

  const handleBoardReset = () => {
    setResetBoard(false);
  };

  const handleExitGame = () => {
    setGameMode(null);
    setResetBoard(true);
    setStarts(null);
    setTotalGames(null);
  };

  const isBoardVisible =
    gameMode &&
    (gameMode !== "player-vs-bot" || starts) &&
    (gameMode !== "bot-vs-bot" || totalGames);

  return (
    <>
      <div>
        {!isBoardVisible && (
          <>
            {/* CHOOSE GAME MODE */}
            {gameMode === null && (
              <div className="flex flex-col items-center sm:flex-row gap-4">
                <button
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => selectMode("player-vs-player")}
                >
                  🧍🆚🧍
                </button>
                <button
                  disabled
                  className="px-4 py-2 bg-blue-500 text-white rounded opacity-50"
                  onClick={() => selectMode("online")}
                >
                  💻🆚💻
                </button>
                <button
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => selectMode("player-vs-bot")}
                >
                  🧍🆚🤖
                </button>
                <button
                  className="px-4 py-2 bg-blue-500 text-white rounded"
                  onClick={() => selectMode("bot-vs-bot")}
                >
                  🤖🆚🤖
                </button>
              </div>
            )}

            {/* WHO STARTS */}
            {gameMode === "player-vs-bot" && !starts && (
              <>
                <div className="flex flex-col items-center sm:flex-row gap-4">
                  <button
                    className="px-4 py-2 bg-red-500 text-white rounded"
                    onClick={() => handleExitGame()}
                  >
                    Go back
                  </button>

                  <button
                    className="px-4 py-2 bg-green-500 text-white rounded"
                    onClick={() => setStarts("player")}
                  >
                    🧍 Starts
                  </button>
                  <button
                    className="px-4 py-2 bg-green-500 text-white rounded"
                    onClick={() => setStarts("bot")}
                  >
                    🤖 Starts
                  </button>
                </div>
              </>
            )}

            {/* NUMBER OF GAMES */}
            {gameMode === "bot-vs-bot" && !totalGames && (
              <div className="flex flex-col items-center sm:flex-row gap-4">
                <button
                  className="px-4 py-2 bg-red-500 text-white rounded"
                  onClick={() => handleExitGame()}
                >
                  Go back
                </button>
                <div className="flex flex-col items-center sm:flex-row gap-4">
                  <button
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    onClick={() => setTotalGames(1)}
                  >
                    1️⃣
                  </button>
                  <button
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    onClick={() => setTotalGames(10)}
                  >
                    🔟
                  </button>
                  <button
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    onClick={() => setTotalGames(100)}
                  >
                    💯
                  </button>
                </div>
                <form
                  className="flex flex-col items-center sm:flex-row gap-4"
                  onSubmit={(e) => {
                    e.preventDefault(); // Prevent page refresh
                    const input = (e.target as HTMLFormElement).querySelector(
                      "input"
                    );
                    if (input) {
                      const games = parseInt(input.value, 10);
                      setTotalGames(games);
                    }
                  }}
                >
                  <input
                    className="px-4 py-2 border rounded text-black"
                    type="number"
                    name="games"
                    id="games"
                    autoComplete="off"
                    placeholder="Enter number of games"
                  />
                  <button
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    type="submit"
                  >
                    Submit
                  </button>
                </form>
              </div>
            )}
          </>
        )}
      </div>

      {/* GAME BOARD */}
      {isBoardVisible && (
        <>
          <button
            className="px-4 py-2 bg-red-500 text-white rounded"
            onClick={() => handleExitGame()}
          >
            Exit game
          </button>
          <div>
            {starts === "bot" && (
              <p className="text-red-500">
                *Bot starts isn&apos;t working. Sorry for the inconvenience. :/
              </p>
            )}

            <Board
              gameMode={gameMode}
              starts={starts}
              totalGames={totalGames}
              resetBoard={resetBoard}
              onReset={handleBoardReset}
            />
          </div>
        </>
      )}
    </>
  );
};

export default Dashboard;
