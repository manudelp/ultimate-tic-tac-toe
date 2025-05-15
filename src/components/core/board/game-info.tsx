import PlayerO from "@/components/ui/playero";
import PlayerX from "@/components/ui/playerx";

interface GameInfoProps {
  gameMode: "player-vs-player" | "player-vs-bot" | "online";
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
  // Helper function to get player name based on game mode
  const getPlayerName = (letter: string) => {
    if (gameMode === "online" && yourLetter === letter) {
      return "You";
    }
    
    if (gameMode === "player-vs-bot") {
      return letter === "X" ? "You" : bot?.name;
    }
    
    return `Player ${letter}`;
  };

  // Get game mode display text
  const getGameModeText = () => {
    switch (gameMode) {
      case "player-vs-player": return "Local Match";
      case "player-vs-bot": return "VS Computer";
      case "online": return "Online Match";
      default: return "";
    }
  };
  // Get player avatar based on game mode and player
  const getPlayerAvatar = (letter: string) => {
    if (letter === "X") {
      return <PlayerX />;
    } else {
      if (gameMode === "player-vs-bot") {
        return (
          <div className="flex items-center justify-center text-base">
            {bot?.icon}
          </div>
        );
      } else {
        return <PlayerO />;
      }
    }
  };

  return (
    <div className="w-full mb-2">
      <div className="bg-gray-700 rounded-lg px-3 py-1.5 flex items-center justify-between shadow-md">
        {/* Left side: Game mode */}
        <span className="text-xs font-medium text-gray-300">
          {getGameModeText()}
        </span>

        {/* Player indicators */}
        <div className="flex items-center space-x-2">
          {/* Active player indicator */}
          <span className="text-[10px] text-gray-400 mr-1">Turn:</span>
          
          {/* Player X */}
          <div className={`flex items-center ${turn !== "X" ? "opacity-60" : ""}`}>
            <div className={`w-5 h-5 rounded-full ${turn === "X" ? "bg-blue-500 ring-1 ring-blue-300" : "bg-gray-600"} flex items-center justify-center`}>
              <PlayerX />
            </div>
            <span className={`text-xs font-medium ml-1 ${turn === "X" ? "text-blue-400" : "text-gray-400"}`}>
              {getPlayerName("X")}
            </span>
          </div>
          
          {/* Separator */}
          <span className="text-gray-500">|</span>
          
          {/* Player O */}
          <div className={`flex items-center ${turn !== "O" ? "opacity-60" : ""}`}>
            <span className={`text-xs font-medium mr-1 ${turn === "O" ? "text-red-400" : "text-gray-400"}`}>
              {gameMode === "player-vs-bot" && isBotThinking && turn === "O" ? (
                <span className="flex items-center">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse mr-1"></span>
                  <span>{getPlayerName("O")}</span>
                </span>
              ) : (
                getPlayerName("O")
              )}
            </span>
            <div className={`w-5 h-5 rounded-full ${turn === "O" ? "bg-red-500 ring-1 ring-red-300" : "bg-gray-600"} flex items-center justify-center`}>
              {getPlayerAvatar("O")}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
