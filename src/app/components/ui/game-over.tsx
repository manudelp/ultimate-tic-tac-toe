import React from "react";

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}

interface GameOverModalProps {
  gameWinner: string | null;
  gameMode: string;
  bot: BotListResponse | null;
  starts: string | null;
  closeModal: boolean;
  setCloseModal: () => void;
  playAgain: () => void;
  onExit: () => void;
}

const GameOverModal: React.FC<GameOverModalProps> = ({
  gameWinner,
  gameMode,
  bot,
  starts,
  closeModal,
  setCloseModal,
  playAgain,
  onExit,
}) => {
  if (closeModal) return null;

  const isDraw = gameWinner === null;
  const isPlayerWinner =
    (starts === "player" && gameWinner === "X") ||
    (starts !== "player" && gameWinner === "O");

  const getResultMessage = () => {
    if (isDraw) return "It's a draw!";

    if (gameMode === "player-vs-bot") {
      return isPlayerWinner
        ? "🎉 You win the game!"
        : `💀 ${bot?.icon} ${bot?.name} wins! Better luck next time.`;
    }

    return gameWinner === "X"
      ? "Player X wins the match!"
      : "Player O wins the match!";
  };

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-gray-900/80 p-4 animate-fade-in">
      <div className="bg-gray-900 border border-gray-800 rounded-xl shadow-xl w-full max-w-md text-center p-6 space-y-6">
        {/* Header */}
        <div className="text-2xl sm:text-3xl font-bold text-white">
          {getResultMessage()}
        </div>

        {/* Summary (optional) */}
        {gameMode === "player-vs-bot" && (
          <div className="text-sm text-gray-400">
            Game:{" "}
            <strong>
              You vs {bot?.name} {bot?.icon}
            </strong>
          </div>
        )}

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row justify-center gap-3">
          <button
            onClick={setCloseModal}
            className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 text-gray-100 rounded-md transition"
          >
            See Board
          </button>
          <button
            onClick={playAgain}
            className="px-4 py-2 text-sm bg-green-600 hover:bg-green-500 text-white rounded-md transition font-medium"
          >
            Play Again
          </button>
          <button
            onClick={onExit}
            className="px-4 py-2 text-sm bg-red-600 hover:bg-red-500 text-white rounded-md transition font-medium"
          >
            Exit
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOverModal;
