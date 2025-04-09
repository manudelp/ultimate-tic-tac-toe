import React, { useState, useEffect, useRef, useMemo } from "react";
import dynamic from "next/dynamic";
import { getBots, loadBot } from "@/api";
import Loader from "@/app/components/ui/loader";
import { toast } from "sonner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faWhatsapp,
  faXTwitter,
  faReddit,
} from "@fortawesome/free-brands-svg-icons";

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
    (gameMode !== "player-vs-player" || isOnline !== null);

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

  const shareOnWhatsApp = () => {
    const link = window.location.href;
    const message = `Think you're the ultimate strategist? Prove it! 🕹️ Play Ultimate Tic Tac Toe with me: ${link}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, "_blank");
  };

  const shareOnTwitter = () => {
    const link = window.location.href;
    const text = `Challenge your mind and your friends! 🧠🔥 Play Ultimate Tic Tac Toe:`;
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(
        text
      )}&url=${encodeURIComponent(link)}`,
      "_blank"
    );
  };

  const shareOnReddit = () => {
    const link = window.location.href;
    const title =
      "Can you outsmart the bot or your friends? 🕹️ Play Ultimate Tic Tac Toe now!";
    window.open(
      `https://www.reddit.com/submit?url=${encodeURIComponent(
        link
      )}&title=${encodeURIComponent(title)}`,
      "_blank"
    );
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
  }, [bot, bots]);

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
    <div className="flex flex-col items-center justify-center min-h-svh p-4 sm:p-8 text-white">
      <div className="text-center">
        {!isBoardVisible && (
          <>
            {/* Title */}
            {!gameMode ? (
              <h1 className="text-3xl sm:text-4xl mb-8 font-bold">
                <small>Welcome to the</small>
                <br />
                <span className="relative">Ultimate Tic-Tac-Toe,</span>
                <br />
                <small>
                  a game of <span id="type" ref={typeRef}></span>.
                </small>
              </h1>
            ) : gameMode === "player-vs-player" ? (
              <h1 className="sm:mt-auto text-2xl sm:text-4xl font-bold">
                Ready to fight?
              </h1>
            ) : (
              <h1 className="mt-20 sm:mt-auto text-2xl sm:text-4xl font-bold">
                So you dare to face us...
              </h1>
            )}

            {/* Choose Game Mode */}
            {gameMode === null && (
              <div className="flex flex-wrap flex-col sm:flex-row justify-center gap-6">
                <button
                  className="sm:w-64 py-4 bg-gray-800 hover:bg-green-700 transition-colors font-medium text-lg hover:animate-pulse"
                  onClick={() => selectMode("player-vs-player")}
                >
                  Fight a friend
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-red-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  } hover:animate-pulse`}
                  onClick={() =>
                    isBackendConnected
                      ? selectMode("player-vs-bot")
                      : toast.warning("Server is offline", {
                          description:
                            "It may take up around 1 minute to connect.",
                          action: {
                            label: "Reload",
                            onClick: () => window.location.reload(),
                          },
                        })
                  }
                >
                  Fight us
                </button>
              </div>
            )}

            {/* Local or Online */}
            {gameMode === "player-vs-player" && (
              <div className="mt-8 text-center">
                <h2 className="text-xl sm:text-2xl font-semibold mb-4">How?</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="sm:w-64 py-4 px-6 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setIsOnline(false)}
                  >
                    Local
                  </button>
                  <button
                    className="sm:w-64 py-4 px-6 bg-gray-500 opacity-70 cursor-not-allowed transition-colors"
                    onClick={() => toast.info("Coming soon!")}
                  >
                    Online
                  </button>
                </div>
                <button
                  className="mt-6 sm:w-64 py-4 px-6 bg-red-500 hover:bg-red-400 transition-colors"
                  onClick={() => handleExitGame()}
                >
                  Go Back
                </button>
              </div>
            )}

            {/* Choose Bot */}
            {gameMode === "player-vs-bot" && !bot && (
              <div className="max-w-3xl mx-auto mt-8 px-4 text-center">
                <h2 className="text-xl sm:text-2xl font-semibold mb-4">
                  Choose your opponent
                </h2>

                <div
                  className={`${
                    selectedBot
                      ? "flex flex-col sm:flex-row sm:items-start gap-4"
                      : "grid place-items-center"
                  }`}
                >
                  {/* Bot list */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
                    {bots?.map((botOption) => (
                      <button
                        key={botOption.id}
                        className={`relative flex flex-col items-center gap-2 p-4 font-bold overflow-hidden bg-gray-800 rounded-md ${
                          botsLoaded[botOption.id]
                            ? "hover:bg-gray-700"
                            : "opacity-50 cursor-not-allowed"
                        } transition-colors ${
                          selectedBot?.id === botOption.id
                            ? "ring-4 ring-red-500"
                            : ""
                        }`}
                        disabled={!botsLoaded[botOption.id]}
                        onClick={() => setSelectedBot(botOption)}
                      >
                        {botsLoaded[botOption.id] ? (
                          <>
                            <div
                              className={`relative z-10 rounded-md text-4xl w-16 h-16 grid place-items-center ${
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
                            <p className="relative z-10 text-center">
                              {botOption.name}
                            </p>
                          </>
                        ) : (
                          <Loader />
                        )}
                      </button>
                    ))}
                  </div>

                  {/* Bot description */}
                  {selectedBot && (
                    <div className="mt-4 sm:mt-0 sm:w-80 bg-gray-800 p-4 rounded-md flex flex-col items-center justify-between">
                      <div className="text-lg font-semibold mb-4 flex flex-col items-center">
                        <div className="bg-gray-700 rounded-full text-4xl w-16 h-16 flex items-center justify-center mb-2">
                          {selectedBot.icon}
                        </div>
                        <h3 className="text-center">{selectedBot.name}</h3>
                      </div>
                      <p className="text-sm text-gray-400 text-center">
                        {selectedBot.description || "No description available."}
                      </p>
                      <div className="mt-2">
                        <h3>How cooked are you? 😅</h3>
                        <p className="text-sm text-gray-400 text-center">
                          {Array(selectedBot.difficulty).fill("🔥").join(" ")}
                        </p>
                      </div>
                      <button
                        className="mt-6 w-full py-4 px-6 bg-green-500 hover:bg-green-400 transition-colors"
                        onClick={() => setBot(selectedBot)}
                      >
                        Play
                      </button>
                    </div>
                  )}
                </div>

                <button
                  className="mt-4 w-full sm:w-64 py-4 px-6 bg-red-500 hover:bg-red-400 transition-colors"
                  onClick={() => handleExitGame()}
                >
                  Go Back
                </button>
              </div>
            )}

            {/* Who Starts (player-vs-bot) */}
            {gameMode === "player-vs-bot" && bot && !starts && (
              <div className="mt-8 text-center">
                <h2 className="text-2xl font-semibold mb-4">Who starts?</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="sm:w-64 py-4 px-6 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setStarts("player")}
                  >
                    Player Starts
                  </button>
                  <button
                    className="sm:w-64 py-4 px-6 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setStarts("bot")}
                  >
                    Bot Starts
                  </button>
                </div>
                <button
                  className="mt-6 sm:w-64 py-4 px-6 bg-red-500 hover:bg-red-400 transition-colors"
                  onClick={() => handleExitGame()}
                >
                  Go Back
                </button>
              </div>
            )}

            {/* Share with friends */}
            <div className="mt-8 text-center">
              <h3 className="mb-2">Share with friends!</h3>
              <div className="flex justify-center gap-6">
                <button
                  onClick={() => {
                    shareOnWhatsApp();
                    toast.success("Thank you for sharing on WhatsApp!");
                  }}
                  className="text-3xl hover:text-green-500 transition-colors"
                >
                  <FontAwesomeIcon icon={faWhatsapp} />
                </button>
                <button
                  onClick={() => {
                    shareOnTwitter();
                    toast.success("Thank you for sharing on Twitter!");
                  }}
                  className="text-3xl hover:text-black transition-colors"
                >
                  <FontAwesomeIcon icon={faXTwitter} />
                </button>
                <button
                  onClick={() => {
                    shareOnReddit();
                    toast.success("Thank you for sharing on Reddit!");
                  }}
                  className="text-3xl hover:text-orange-600 transition-colors"
                >
                  <FontAwesomeIcon icon={faReddit} />
                </button>
              </div>
            </div>
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
