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
    <div>
      <div>
        {!isBoardVisible && (
          <>
            <div>
              <div>
                <div>
                  {/* CHOOSE GAME MODE */}
                  {gameMode === null && (
                    <div>
                      <button
                        className="game-mode-button"
                        onClick={() => selectMode("player-vs-player")}
                      >
                        🧍🆚🧍
                      </button>
                      <button
                        className="game-mode-button"
                        onClick={() => selectMode("online")}
                      >
                        💻🆚💻
                      </button>
                      <button
                        className="game-mode-button"
                        onClick={() => selectMode("player-vs-bot")}
                      >
                        🧍🆚🤖
                      </button>
                      <button
                        className="game-mode-button"
                        onClick={() => selectMode("bot-vs-bot")}
                      >
                        🤖🆚🤖
                      </button>
                    </div>
                  )}

                  {/* WHO STARTS */}
                  {gameMode === "player-vs-bot" && !starts && (
                    <div>
                      <button
                        className="start-button"
                        onClick={() => setStarts("player")}
                      >
                        🧍 Starts
                      </button>
                      <button
                        className="start-button"
                        onClick={() => setStarts("bot")}
                      >
                        🤖 Starts
                      </button>
                    </div>
                  )}

                  {/* NUMBER OF GAMES */}
                  {gameMode === "bot-vs-bot" && !botMatch && (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault(); // Prevent page refresh
                        const input = (
                          e.target as HTMLFormElement
                        ).querySelector("input");
                        if (input) {
                          setBotMatch(parseInt(input.value, 10));
                        }
                      }}
                    >
                      <input
                        type="number"
                        name="games"
                        id="games"
                        autoComplete="off"
                        placeholder="Enter number of games"
                      />
                      <button className="submit-button" type="submit">
                        Submit
                      </button>
                    </form>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* GAME BOARD */}
      {isBoardVisible && (
        <>
          <button onClick={() => handleExitGame()}>Exit game</button>

          <div>
            <div>
              {starts === "bot" && (
                <p>
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
