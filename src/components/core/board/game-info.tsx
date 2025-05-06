import PlayerO from "@/components/ui/playero";
import PlayerX from "@/components/ui/playerx";

interface GameInfoProps {
  gameMode: "player-vs-bot" | "online";
  yourLetter?: string;
  turn: string;
  bot?: { name: string; icon: string };
  isBotThinking?: boolean;
}

export default function GameInfo({
  gameMode,
  yourLetter,
  turn,
  bot,
  isBotThinking,
}: GameInfoProps) {
  return (
    <div className="w-full p-4 mb-4 bg-gray-800 rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        {/* Left Player */}
        <div className="flex items-center gap-2">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg
                            ${turn === "X" ? "ring-2 ring-green-400" : ""}
                            ${
                              gameMode === "online" && yourLetter === "X"
                                ? "bg-blue-500"
                                : "bg-blue-500"
                            }`}
          >
            <PlayerX />
          </div>
          <div>
            <p className="font-medium text-gray-200">
              {gameMode === "online" && yourLetter === "X"
                ? "You"
                : gameMode === "player-vs-bot"
                ? "You"
                : "Opponent"}
            </p>
            <p
              className={`text-xs ${
                turn === "X" ? "font-bold text-green-400" : "text-gray-400"
              }`}
            >
              {turn === "X" ? "Current turn" : "Waiting"}
            </p>
          </div>
        </div>

        {/* Turn Indicator */}
        <div className="flex flex-col items-center">
          <p className="text-xs text-gray-400">Current Turn</p>
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center mt-1
                        ${
                          turn === "X" ? "bg-blue-500" : "bg-red-500"
                        } shadow-lg`}
          >
            {turn}
          </div>
        </div>

        {/* Right Player */}
        <div className="flex items-center gap-2">
          <div>
            <p className="font-medium text-right text-gray-200">
              {gameMode === "player-vs-bot"
                ? bot?.name
                : gameMode === "online" && yourLetter === "O"
                ? "You"
                : "Opponent"}
            </p>
            <p
              className={`text-xs text-right ${
                turn === "O" ? "font-bold text-green-400" : "text-gray-400"
              }`}
            >
              {gameMode === "player-vs-bot" && turn === "O" && isBotThinking ? (
                <span className="flex items-center justify-end">
                  Thinking
                  <span className="flex ml-1">
                    <span className="animate-bounce mx-[1px] h-1 w-1 rounded-full bg-gray-400"></span>
                    <span className="animate-bounce mx-[1px] h-1 w-1 rounded-full bg-gray-400 animation-delay-100"></span>
                    <span className="animate-bounce mx-[1px] h-1 w-1 rounded-full bg-gray-400 animation-delay-200"></span>
                  </span>
                </span>
              ) : turn === "O" ? (
                "Current turn"
              ) : (
                "Waiting"
              )}
            </p>
          </div>
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg
                            ${turn === "O" ? "ring-2 ring-green-400" : ""}
                            ${
                              gameMode === "player-vs-bot"
                                ? "flex items-center justify-center text-3xl bg-gray-700"
                                : "bg-red-500"
                            }`}
          >
            {gameMode === "player-vs-bot" ? bot?.icon : <PlayerO />}
          </div>
        </div>
      </div>
    </div>
  );
}
