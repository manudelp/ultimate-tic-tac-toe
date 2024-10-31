// src/app/components/layout/dashboard.tsx
import React, { useState } from "react";
import Board from "@/app/components/core/board";

const Dashboard: React.FC = () => {
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [starts, setStarts] = useState<string | null>(null);
  const [botMatch, setBotMatch] = useState<number | null>(null);
  const [resetBoard, setResetBoard] = useState<boolean>(false);

  const selectMode = (mode: string) => {
    setGameMode(mode);
    setResetBoard(true);
    setStarts(null);
    setBotMatch(null);
  };

  const handleBoardReset = () => {
    setResetBoard(false);
  };

  const handleExitGame = () => {
    setGameMode(null);
    setResetBoard(true);
    setStarts(null);
    setBotMatch(null);
  };

  const isBoardVisible =
    gameMode &&
    (gameMode !== "player-vs-bot" || starts) &&
    (gameMode !== "bot-vs-bot" || botMatch);

  return (
    <div className="p-4">
      <div>
        {!isBoardVisible && (
          <>
            {/* CHOOSE GAME MODE */}
            {gameMode === null && (
              <div className="flex gap-4">
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
              <div className="flex gap-4">
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
            )}

            {/* NUMBER OF GAMES */}
            {gameMode === "bot-vs-bot" && !botMatch && (
              <form
                className="flex gap-4"
                onSubmit={(e) => {
                  e.preventDefault(); // Prevent page refresh
                  const input = (e.target as HTMLFormElement).querySelector(
                    "input"
                  );
                  if (input) {
                    setBotMatch(parseInt(input.value, 10));
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
            <div>
              {starts === "bot" && (
                <p className="text-red-500">
                  *Bot starts isn&apos;t working. Sorry for the inconvenience.
                  :/
                </p>
              )}

              <Board
                gameMode={gameMode}
                starts={starts}
                botMatch={botMatch}
                resetBoard={resetBoard}
                onReset={handleBoardReset}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
