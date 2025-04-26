import React, { useState, useEffect, useRef, useMemo } from "react";
import { Link } from "react-router-dom";
import dynamic from "next/dynamic";
import Button from "@/app/components/ui/button";
import Share from "@/app/components/ui/share";
import { getBots, loadBot } from "@/api";
import Loader from "@/app/components/ui/loader";
import { toast } from "sonner";

const Board = dynamic(() => import("@/app/components/core/board"), {
  ssr: false,
  loading: () => <Loader />,
});

// Types
type BotListResponse = {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
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

interface DashboardProps {
  isBackendConnected: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ isBackendConnected }) => {
  // Core
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [starts, setStarts] = useState<string | null>(null);

  // Online
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  // Bots
  const [bots, setBots] = useState<BotListResponse[] | null>(null);
  const [selectedBot, setSelectedBot] = useState<BotListResponse | null>(null);
  const [bot, setBot] = useState<BotListResponse | null>(null);
  const [botsLoaded, setBotsLoaded] = useState<boolean[]>([]);

  // Board visibility
  const isBoardVisible =
    gameMode &&
    (gameMode !== "player-vs-bot" || starts) &&
    (gameMode !== "player-vs-player" || isOnline === false) &&
    (gameMode !== "online" || isOnline === true);

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
        "wit",
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
    setIsOnline(null);
    setBot(null);
    setStarts(null);
  };

  const handleExitGame = () => {
    setGameMode(null);
    setIsOnline(null);
    setBot(null);
    setStarts(null);
  };

  const updateBotsLoaded = (id: number) => {
    setBotsLoaded((prev) => {
      const updated = [...prev];
      updated[id] = true;
      return updated;
    });
  };

  // Bot selection
  useEffect(() => {
    if (gameMode === "player-vs-bot" && !bots) {
      getBots().then((bots) => {
        console.log(bots); // Debugging
        setBots(
          bots.map((bot: BotListResponse) => ({
            ...bot,
            description: bot.description || "",
          }))
        );
      });
    }
  }, [gameMode, bots]);

  useEffect(() => {
    if (bots) {
      bots.forEach((bot) => {
        loadBot(bot.id).then(() => {
          updateBotsLoaded(bot.id);
        });
      });
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
    <div className="flex flex-col items-center justify-center p-4 text-white min-h-svh sm:p-8">
      <div className="text-center">
        {!isBoardVisible && (
          <>
            {/* Title */}
            {!gameMode ? (
              <h1 className="mb-8 text-3xl font-bold sm:text-4xl">
                <small>Welcome to the</small>
                <br />
                <span className="relative">Ultimate Tic-Tac-Toe,</span>
                <br />
                <small>
                  a game of <span id="type" ref={typeRef}></span>.
                </small>
              </h1>
            ) : gameMode === "player-vs-player" ? (
              isOnline ? (
                <h1 className="text-2xl font-bold sm:mt-auto sm:text-4xl">
                  Find your rival
                </h1>
              ) : (
                <h1 className="text-2xl font-bold sm:mt-auto sm:text-4xl">
                  Ready to play?
                </h1>
              )
            ) : (
              <h1 className="mt-20 text-2xl font-bold sm:mt-auto sm:text-4xl">
                So you dare to face us...
              </h1>
            )}

            {/* Choose Game Mode */}
            {gameMode === null && (
              <div className="flex flex-col flex-wrap justify-center gap-6 sm:flex-row">
                <Button
                  text="Fight someone"
                  className="text-lg font-medium hover:bg-green-700 hover:animate-pulse"
                  onClick={() => selectMode("player-vs-player")}
                />
                <Button
                  text="Fight us"
                  className={`text-lg font-medium ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-red-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  } hover:animate-pulse`}
                  onClick={() =>
                    isBackendConnected
                      ? selectMode("player-vs-bot")
                      : toast.warning("Server is offline", {
                          description:
                            "The server is currently offline. Please try again later.",
                          action: {
                            label: "Reload",
                            onClick: () => window.location.reload(),
                          },
                        })
                  }
                />
              </div>
            )}

            {/* Local or Online */}
            {gameMode === "player-vs-player" && !isOnline && (
              <div className="mt-8 text-center">
                <h2 className="mb-4 text-xl font-semibold sm:text-2xl">How?</h2>
                <div className="flex flex-col justify-center gap-6 sm:flex-row">
                  <Button text="Local" onClick={() => setIsOnline(false)} />
                  <Button text="Online" onClick={() => setIsOnline(true)} />
                </div>
                <Button
                  text="Go Back"
                  className="mt-6 sm:!w-48"
                  variant="danger"
                  onClick={() => handleExitGame()}
                />
              </div>
            )}

            {gameMode === "player-vs-player" && isOnline && (
              <div className="mt-8 text-center">
                <h2 className="mb-4 text-xl font-semibold sm:text-2xl">
                  Select your option
                </h2>
                <div className="flex flex-col justify-center gap-6 sm:flex-row">
                  <Link to="/lobby">
                    <Button text="Share a link" />
                  </Link>
                  <Link to="/matchmaking">
                    <Button text="Search for players" />
                  </Link>
                </div>
                <Button
                  text="Go Back"
                  className="mt-6 sm:!w-48"
                  variant="danger"
                  onClick={() => handleExitGame()}
                />
              </div>
            )}
            {/* Choose Bot */}
            {gameMode === "player-vs-bot" && !bot && (
              <div className="max-w-4xl px-2 mx-auto mt-4 sm:px-4">
                <h2 className="mb-6 text-xl font-bold text-center sm:text-2xl">
                  Choose your opponent
                </h2>

                <div
                  className={`grid ${
                    selectedBot ? "sm:grid-cols-[2fr_1fr]" : "grid-cols-1"
                  } gap-4`}
                >
                  <div className="grid grid-cols-2 gap-4 sm:grid-cols-2">
                    {bots?.map((botOption) => (
                      <div
                        key={botOption.id}
                        className={`relative bg-gray-800 rounded-lg overflow-hidden transition-all duration-200 ring-2 ${
                          !botsLoaded[botOption.id] && "opacity-60"
                        } ${
                          selectedBot?.id === botOption.id
                            ? "ring-red-500"
                            : "ring-transparent"
                        }`}
                      >
                        <button
                          className="flex flex-col items-center w-full h-full p-4 text-left"
                          disabled={!botsLoaded[botOption.id]}
                          onClick={() => {
                            setSelectedBot(botOption);
                            if (window.innerWidth <= 768) {
                              setTimeout(() => {
                                const selectedBotMenu =
                                  document.getElementById("selectedBotMenu");
                                if (selectedBotMenu) {
                                  selectedBotMenu.scrollIntoView({
                                    behavior: "smooth",
                                    block: "start",
                                  });
                                }
                              }, 100);
                            }
                          }}
                        >
                          {/* Bot avatar */}
                          <div
                            className={`relative rounded-full text-4xl w-20 h-20 grid place-items-center mb-3 ${
                              botOption.id === -1 ? "bg-black" : "bg-gray-700"
                            }`}
                            style={
                              botOption.id === -1
                                ? { backgroundImage: `url('/fire.gif')` }
                                : undefined
                            }
                          >
                            {botOption.icon}
                          </div>

                          {/* Bot info */}
                          <div className="w-full text-center">
                            <h3 className="mb-1 text-lg font-bold">
                              {botOption.name}
                            </h3>

                            {/* Difficulty rating */}
                            <div className="flex justify-center mb-2">
                              {Array(5)
                                .fill(0)
                                .map((_, i) => (
                                  <span key={i} className="mx-0.5">
                                    {i < botOption.difficulty ? "🔥" : "⚪"}
                                  </span>
                                ))}
                            </div>
                          </div>

                          {/* Loading indicator */}
                          {!botsLoaded[botOption.id] && (
                            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-70">
                              <Loader />
                            </div>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Full description panel - appears below on mobile, side panel on desktop */}
                  {selectedBot && (
                    <div
                      id="selectedBotMenu"
                      className="flex flex-col justify-between p-4 mt-6 bg-gray-800 rounded-lg shadow-lg sm:mt-0"
                    >
                      <div className="flex items-center gap-4 mb-4">
                        <div className="flex items-center justify-center w-16 h-16 text-4xl bg-gray-700 rounded-full">
                          {selectedBot.icon}
                        </div>
                        <div className="flex flex-col items-start justify-center">
                          <h3 className="text-xl font-bold">
                            {selectedBot.name}
                          </h3>
                          <div className="flex">
                            {Array(selectedBot.difficulty)
                              .fill("🔥")
                              .map((fire, i) => (
                                <span key={i}>{fire}</span>
                              ))}
                          </div>
                        </div>
                      </div>

                      <p className="mb-4 text-gray-300">
                        {selectedBot.description || "No description available."}
                      </p>

                      <div className="flex gap-4">
                        <Button
                          text="Play Now"
                          variant="success"
                          className="!w-full !h-12 text-sm !p-0"
                          onClick={() => setBot(selectedBot)}
                        />
                        <Button
                          text="Go Back"
                          variant="danger"
                          className="!w-32 !h-12 text-sm !p-0 !px-2"
                          onClick={() => {
                            setSelectedBot(null);
                            handleExitGame();
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Only show this button when no bot is selected */}
                {!selectedBot && (
                  <Button
                    text="Go Back"
                    variant="danger"
                    className="mx-auto mt-6 sm:!w-48"
                    onClick={() => {
                      setSelectedBot(null);
                      handleExitGame();
                    }}
                  />
                )}
              </div>
            )}

            {/* Who Starts (player-vs-bot) */}
            {gameMode === "player-vs-bot" && bot && !starts && (
              <div className="mt-8 text-center">
                <h2 className="mb-4 text-2xl font-semibold">Who starts?</h2>
                <div className="flex flex-col justify-center gap-6 sm:flex-row">
                  <button
                    className="px-6 py-4 transition-colors bg-gray-800 sm:w-64 hover:bg-gray-700"
                    onClick={() => setStarts("player")}
                  >
                    Player Starts
                  </button>
                  <button
                    className="px-6 py-4 transition-colors bg-gray-800 sm:w-64 hover:bg-gray-700"
                    onClick={() => setStarts("bot")}
                  >
                    Bot Starts
                  </button>
                </div>
                <button
                  className="block w-full px-6 py-3 mx-auto mt-6 bg-gray-700 rounded sm:w-48 hover:bg-gray-600"
                  onClick={() => handleExitGame()}
                >
                  Go Back
                </button>
              </div>
            )}

            <Share />
          </>
        )}
      </div>

      {/* Game Board */}
      {isBoardVisible && (
        <Board
          gameMode={gameMode}
          bot={bot}
          starts={starts}
          onExit={handleExitGame}
        />
      )}
    </div>
  );
};

export default Dashboard;
