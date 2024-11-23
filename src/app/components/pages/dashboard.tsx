import React, { useState, useEffect, useRef, useMemo } from "react";
import { checkConnection, getBots } from "@/api";
import Board from "@/app/components/core/board";

// Types
type BotListResponse = {
  id: number;
  name: string;
  icon: string;
};

// Utility function to shuffle an array
const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
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

  // Board visibility
  const isBoardVisible = gameMode && (gameMode !== "player-vs-bot" || starts);

  // Ref for the typing effect
  const typeRef = useRef<HTMLSpanElement>(null);

  // Typing Words and Colors
  const shuffledWords = useMemo(
    () =>
      shuffleArray([
        "strategy",
        "skill",
        "luck",
        "tactics",
        "planning",
        "execution",
        "decision-making",
        "expertise",
        "chance",
        "probability",
        "preparation",
        "risk",
        "adaptability",
      ]),
    []
  );

  const shuffledColors = useMemo(
    () =>
      shuffleArray([
        "#FFD700",
        "#FF4500",
        "#00FF00",
        "#1E90FF",
        "#FF69B4",
        "#8A2BE2",
        "#00CED1",
        "#FFA500",
        "#7FFF00",
        "#DC143C",
        "#4682B4",
        "#D2691E",
        "#808080",
      ]),
    []
  );

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
  };

  // Check backend connection
  useEffect(() => {
    const checkBackendConnection = async () => {
      const isConnected = await checkConnection();
      setIsBackendConnected(isConnected);
      console.log("Backend connection:", isConnected);
    };

    checkBackendConnection();
  }, []);

  // Bot selection
  useEffect(() => {
    if (gameMode === "player-vs-bot" && !bots) {
      getBots().then((bots) => setBots(bots));
    }
  }, [gameMode, bots]);

  // Words effect
  useEffect(() => {
    if (!typeRef.current) return;

    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let animationFrame: number;

    const type = () => {
      const currentWord = shuffledWords[wordIndex];

      // Update text content
      if (typeRef.current) {
        typeRef.current.textContent = isDeleting
          ? currentWord.substring(0, charIndex--)
          : currentWord.substring(0, charIndex++);
        typeRef.current.style.color = shuffledColors[wordIndex];
      }

      // Handle typing/deleting transitions
      if (!isDeleting && charIndex === currentWord.length + 1) {
        // Pause when the full word is typed
        setTimeout(() => {
          isDeleting = true;
          animationFrame = requestAnimationFrame(type);
        }, 1000); // Pause before starting deletion
      } else if (isDeleting && charIndex === 0) {
        // Switch to the next word when deletion is complete
        isDeleting = false;
        wordIndex = (wordIndex + 1) % shuffledWords.length;
        animationFrame = requestAnimationFrame(type);
      } else {
        // Adjust typing speed based on state
        const speed = isDeleting ? 50 : 100;
        setTimeout(() => {
          animationFrame = requestAnimationFrame(type);
        }, speed);
      }
    };

    // Start typing
    animationFrame = requestAnimationFrame(type);

    // Cleanup
    return () => cancelAnimationFrame(animationFrame);
  }, [shuffledWords, shuffledColors]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 sm:p-8 text-white">
      <div className="text-center">
        {!isBoardVisible && (
          <>
            {/* Title */}
            {!gameMode && (
              <h1 className="text-4xl font-bold mb-8">
                <small>Welcome to the</small>
                <br />
                Ultimate Tic-Tac-Toe,
                <br />
                <small>
                  a game of <span id="type" ref={typeRef}></span>.
                </small>
              </h1>
            )}

            {gameMode && (
              <h1 className="text-4xl font-bold mb-8">
                So you fighting us, huh?
              </h1>
            )}

            {/* Choose Game Mode */}
            {gameMode === null && (
              <div className="flex flex-wrap flex-col sm:flex-row justify-center gap-6">
                <button
                  className="sm:w-64 py-4 bg-gray-800 hover:bg-green-700 transition-colors font-medium text-lg"
                  onClick={() => selectMode("player-vs-player")}
                >
                  Fight a friend
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-red-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() =>
                    isBackendConnected && selectMode("player-vs-bot")
                  }
                  disabled={!isBackendConnected}
                >
                  Fight us
                </button>
              </div>
            )}

            {/* Choose Bot */}
            {gameMode === "player-vs-bot" && !bot && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">
                  Choose your opponent
                </h2>
                <div className="flex flex-wrap justify-center gap-4">
                  {bots?.map((bot) => (
                    <button
                      key={bot.id}
                      className="w-64 flex justify-center items-center gap-2 p-4 bg-gray-800 hover:bg-gray-700 transition-colors"
                      onClick={() => setBot(bot)}
                    >
                      <div className="bg-gray-700 rounded-md text-4xl w-12 h-12 grid place-items-center">
                        {bot.icon}
                      </div>
                      <p className="w-full">{bot.name}</p>
                    </button>
                  ))}
                </div>
                <button
                  className="mt-4 px-6 py-3 bg-red-500 hover:bg-red-400 transition-colors"
                  onClick={() => handleExitGame()}
                >
                  Go Back
                </button>
              </div>
            )}

            {/* Who Starts */}
            {gameMode === "player-vs-bot" && bot && !starts && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Who starts?</h2>
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
          </>
        )}
      </div>

      {/* Game Board */}
      {isBoardVisible && (
        <Board
          gameMode={gameMode}
          bot={bot}
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
