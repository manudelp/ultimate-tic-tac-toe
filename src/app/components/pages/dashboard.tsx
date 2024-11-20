import React, { useState, useEffect } from "react";
import { checkConnection, getBots } from "@/api";
import Board from "@/app/components/core/board";

// Types
type BotListResponse = {
  id: number;
  name: string;
  icon: string;
};

const Dashboard: React.FC = () => {
  // Core
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [starts, setStarts] = useState<string | null>(null);
  const [totalGames, setTotalGames] = useState<number | null>(null);
  const [resetBoard, setResetBoard] = useState<boolean>(false);

  // Backend
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);

  // Bots
  const [bots, setBots] = useState<BotListResponse[] | null>(null);
  const [bot, setBot] = useState<BotListResponse | null>(null);
  const [bot2, setBot2] = useState<BotListResponse | null>(null);

  // Board visibility
  const isBoardVisible =
    gameMode &&
    (gameMode !== "player-vs-bot" || starts) &&
    (gameMode !== "bot-vs-bot" || totalGames);

  // Functions
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
    setBot(null);
    setBot2(null);
  };

  useEffect(() => {
    const checkBackendConnection = async () => {
      const isConnected = await checkConnection();
      setIsBackendConnected(isConnected);
      console.log("Backend connection:", isConnected);
    };

    checkBackendConnection();
  }, []);

  useEffect(() => {
    if (gameMode === "player-vs-bot" && !bots) {
      getBots().then((bots) => setBots(bots));
    }
  }, [gameMode, bots]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 sm:p-8 text-white">
      <div className="text-center">
        {!isBoardVisible && (
          <>
            {/* Title */}
            <h1 className="text-4xl font-bold mb-8">Choose Your Game Mode</h1>

            {/* Choose Game Mode */}
            {gameMode === null && (
              <div className="flex flex-wrap flex-col sm:flex-row justify-center gap-6">
                <button
                  className="sm:w-64 py-4 bg-gray-800 hover:bg-gray-700 transition-colors font-medium text-lg"
                  onClick={() => selectMode("player-vs-player")}
                >
                  Player vs Player
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() =>
                    isBackendConnected && selectMode("player-vs-bot")
                  }
                  disabled={!isBackendConnected}
                >
                  Player vs Bot
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() => isBackendConnected && selectMode("bot-vs-bot")}
                  disabled={!isBackendConnected}
                >
                  Bot vs Bot
                </button>
              </div>
            )}

            {/* Choose Bot */}
            {gameMode === "player-vs-bot" && !bot && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Choose Your Bot</h2>
                <div>
                  {bots?.map((bot) => (
                    <button
                      key={bot.id}
                      className="w-64 py-4 bg-gray-800 hover:bg-gray-700 transition-colors"
                      onClick={() => setBot(bot)}
                    >
                      {bot.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Who Starts */}
            {gameMode === "player-vs-bot" && bot && !starts && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Who Starts?</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="px-6 py-3 bg-red-500 hover:bg-red-400 transition-colors"
                    onClick={() => handleExitGame()}
                  >
                    Go Back
                  </button>
                  <button
                    className="px-6 py-3 bg-green-600 hover:bg-green-500 transition-colors"
                    onClick={() => setStarts("player")}
                  >
                    Player Starts
                  </button>
                  <button
                    className="px-6 py-3 bg-green-600 hover:bg-green-500 transition-colors"
                    onClick={() => setStarts("bot")}
                  >
                    Bot Starts
                  </button>
                </div>
              </div>
            )}

            {/* Bots selection */}
            {gameMode === "bot-vs-bot" && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">
                  Choose Your Bots
                </h2>
                <div>
                  {bots?.map((bot) => (
                    <button
                      key={bot.id}
                      className="w-64 py-4 bg-gray-800 hover:bg-gray-700 transition-colors"
                      onClick={() => setBot(bot)}
                    >
                      {bot.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Choose Bot 2 */}
            {gameMode === "bot-vs-bot" && bot && !bot2 && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">
                  Choose Your Bot 2
                </h2>
                <div>
                  {bots?.map((bot) => (
                    <button
                      key={bot.id}
                      className="w-64 py-4 bg-gray-800 hover:bg-gray-700 transition-colors"
                      onClick={() => setBot2(bot)}
                    >
                      {bot.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Number of Games */}
            {gameMode === "bot-vs-bot" && bot && bot2 && !totalGames && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Number of Games</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="px-6 py-3 bg-red-500 hover:bg-red-400 transition-colors"
                    onClick={() => handleExitGame()}
                  >
                    Go Back
                  </button>
                  <button
                    className="px-6 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setTotalGames(1)}
                  >
                    1 Game
                  </button>
                  <button
                    className="px-6 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setTotalGames(10)}
                  >
                    10 Games
                  </button>
                  <button
                    className="px-6 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setTotalGames(100)}
                  >
                    100 Games
                  </button>
                  <form
                    className="flex gap-2"
                    onSubmit={(e) => {
                      e.preventDefault();
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
                      className="w-full sm:w-24 px-3 py-2 border-b border-gray-500 bg-gray-900 focus:outline-none focus:border-gray-700 transition-colors"
                      type="number"
                      name="games"
                      placeholder="Custom"
                      min={1}
                    />
                    <button
                      className="w-1/2 sm:w-auto px-4 py-2 bg-gray-800 hover:bg-gray-700 transition-colors"
                      type="submit"
                    >
                      Set
                    </button>
                  </form>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Game Board */}
      {isBoardVisible && (
        <Board
          gameMode={gameMode}
          bot={bot}
          bot2={bot2}
          starts={starts}
          totalGames={totalGames}
          resetBoard={resetBoard}
          onReset={handleBoardReset}
          onExit={handleExitGame}
        />
      )}
    </div>
  );
};

export default Dashboard;
