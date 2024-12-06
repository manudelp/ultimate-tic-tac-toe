import React, { useState, useEffect, useRef, useMemo } from "react";
import dynamic from "next/dynamic";
import { getBots } from "@/api";
import Image from "next/image";
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
  const [bot, setBot] = useState<BotListResponse | null>(null);

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

  // SNOWING EFFECT LOGIC BELOW

  useEffect(() => {
    class Snowflake {
      x: number;
      y: number;
      radius: number;
      speedX: number;
      speedY: number;
      opacity: number;

      constructor(width: number, height: number) {
        const isBackground = Math.random() > 0.5; // 50% chance of being a background snowflake
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.radius = Math.random() * 4 + 3; // Small radius for a snowflake
        this.speedX = Math.random() * 0.16 + (-0.25 + Math.random() * 2) * 0.15; // Horizontal drift
        this.speedY = Math.random() * 0.16 + 0.25; // Falling speed
        this.opacity = isBackground
          ? Math.random() * 0.3 + 0.2
          : Math.random() * 0.5 + 0.5;
      }

      update(width: number, height: number) {
        this.x += this.speedX;
        this.y += this.speedY;

        // Respawn snowflake at the top if it goes out of bounds
        if (this.y > height) {
          this.y = 0;
          this.x = Math.random() * width;
        }
      }

      draw(ctx: CanvasRenderingContext2D) {
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
          ctx.moveTo(this.x, this.y);
          ctx.lineTo(
            this.x + this.radius * Math.cos((i * Math.PI) / 3),
            this.y + this.radius * Math.sin((i * Math.PI) / 3)
          );
        }
        ctx.strokeStyle = "white";
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.globalAlpha = 1;
      }
    }

    function snowingEffect() {
      const canvas = document.getElementById("snowCanvas") as HTMLCanvasElement;
      const ctx = canvas?.getContext("2d");
      if (!ctx) return;

      const snowflakes: Snowflake[] = [];
      const maxSnowflakes = 270;

      function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }

      resizeCanvas();
      window.addEventListener("resize", resizeCanvas);

      // Create initial snowflakes
      for (let i = 0; i < maxSnowflakes; i++) {
        snowflakes.push(new Snowflake(canvas.width, canvas.height));
      }

      function animate() {
        ctx?.clearRect(0, 0, canvas.width, canvas.height);

        for (const snowflake of snowflakes) {
          snowflake.update(canvas.width, canvas.height);
          if (ctx) {
            snowflake.draw(ctx);
          }
        }

        requestAnimationFrame(animate);
      }

      animate();
    }

    snowingEffect();

    return () => {
      window.removeEventListener("resize", () => {});
    };
  }, [isBoardVisible]);

  const [isMusicPlaying, setIsMusicPlaying] = useState(false);

  useEffect(() => {
    const bgMusic = new Audio("/assets/sounds/bg_xmas.mp3");
    bgMusic.loop = true;
    bgMusic.volume = 0.1;

    const playAudio = () => {
      bgMusic
        .play()
        .then(() => {
          console.log("Audio iniciado");
          setIsMusicPlaying(true);
        })
        .catch((err) => console.error("Error al reproducir audio:", err));
    };

    // Añade el evento solo tras la interacción del usuario
    document.addEventListener("click", playAudio, { once: true });

    return () => {
      document.removeEventListener("click", playAudio);
      bgMusic.pause();
      bgMusic.currentTime = 0;
      setIsMusicPlaying(false);
    };
  }, []);

  // SNOWING EFFECT LOGIC ABOVE

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
                <span className="relative">
                  Ultimate Tic-Tac-Toe,{" "}
                  <Image
                    className="absolute -top-0 -left-3 hover:animate-bounce"
                    src="/assets/img/santa.png"
                    alt="Hat"
                    width={25}
                    height={25}
                  />
                </span>
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
                So you fighting us, huh?
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
                            "It may take up to 50 seconds to connect.",
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
              <div className="mt-8 text-center">
                <h2 className="text-xl sm:text-2xl font-semibold mb-4">
                  Choose your opponent
                </h2>
                <div className="flex flex-wrap justify-center gap-4">
                  {bots?.map((bot) =>
                    // Foo Finder
                    bot.id === -1 ? (
                      <button
                        key={bot.id}
                        className="relative w-64 flex justify-center items-center gap-2 p-4 font-bold overflow-hidden bg-black"
                        onClick={() => setBot(bot)}
                      >
                        <div
                          className="absolute inset-0 bg-cover bg-center opacity-40"
                          style={{ backgroundImage: `url('/fire.gif')` }}
                        ></div>
                        <div className="relative z-10 rounded-md text-4xl w-12 h-12 grid place-items-center">
                          {bot.icon}
                        </div>
                        <p className="relative z-10 w-full">{bot.name}</p>
                      </button>
                    ) : (
                      // All bots
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
                    )
                  )}
                </div>
                <button
                  className="mt-4 sm:w-64 py-4 px-6 bg-red-500 hover:bg-red-400 transition-colors"
                  onClick={() => handleExitGame()}
                >
                  Go Back
                </button>
              </div>
            )}

            {/* Who Starts */}
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

      {!isBoardVisible && (
        <>
          <canvas
            id="snowCanvas"
            className="fixed inset-0 w-full h-full pointer-events-none z-10"
          ></canvas>
          {!isMusicPlaying && (
            <div className="absolute bottom-2 py-2 px-4 text-center rounded-xl bg-black bg-opacity-25 backdrop-blur z-[100] pointer-events-none">
              🎧 Click anywhere to start the music! 👆
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;
