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
  if (closeModal) {
    return null;
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 backdrop-blur-[2px] p-4 sm:p-8">
      <div className="bg-gray-900 border border-gray-800 p-4 sm:p-8 text-center w-full max-w-md">
        <div className="text-xl sm:text-2xl font-semibold mb-4 text-gray-200">
          {gameMode === "player-vs-bot"
            ? starts === "player"
              ? gameWinner === "X"
                ? "You win!"
                : gameWinner === "O"
                ? `${bot?.icon} ${bot?.name} wins! You lose!`
                : "It's a draw!"
              : gameWinner === "O"
              ? "You win!"
              : gameWinner === "X"
              ? `${bot?.icon} ${bot?.name} wins! You lose!`
              : "It's a draw!"
            : gameWinner === "X"
            ? "Player X wins!"
            : gameWinner === "O"
            ? "Player O wins!"
            : "It's a draw!"}
        </div>
        <div className="flex flex-col justify-center sm:flex-row gap-4">
          <button
            onClick={() => setCloseModal()}
            className="px-4 py-2 bg-blue-500 text-white"
          >
            See Board
          </button>
          <button
            onClick={playAgain}
            className="px-4 py-2 bg-green-500 text-white"
          >
            Play again
          </button>
          <button onClick={onExit} className="px-4 py-2 bg-red-500 text-white">
            Exit
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOverModal;
