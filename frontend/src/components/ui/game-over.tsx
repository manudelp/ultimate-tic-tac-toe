import React from "react";
import { motion } from "framer-motion";
import type { BotInfo } from "@/types/game";

interface GameOverModalProps {
  gameWinner: string | null;
  gameMode: string;
  bot: BotInfo | null;
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

  const getResultMessage = () => {
    if (gameMode === "player-vs-bot") {
      const isPlayerX = starts === "player";
      const playerSymbol = isPlayerX ? "X" : "O";
      const botSymbol = isPlayerX ? "O" : "X";

      if (gameWinner === playerSymbol) {
        return "Victory!";
      } else if (gameWinner === botSymbol) {
        return "Defeat!";
      } else {
        return "Draw!";
      }
    } else {
      if (gameWinner === "X") {
        return "Player X Wins!";
      } else if (gameWinner === "O") {
        return "Player O Wins!";
      } else {
        return "It's a Draw!";
      }
    }
  };

  const getSubtitle = () => {
    if (gameMode === "player-vs-bot" && gameWinner && gameWinner !== "Draw") {
      const isPlayerX = starts === "player";
      const playerSymbol = isPlayerX ? "X" : "O";

      return gameWinner === playerSymbol
        ? "Congratulations! You've won the game!"
        : `${bot?.icon} ${bot?.name} has defeated you this time.`;
    }
    return "Thanks for playing!";
  };

  return (
    <motion.div
      className="fixed inset-0 flex items-center justify-center z-50 bg-black/70 backdrop-blur-sm p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl border border-gray-700 shadow-2xl w-full max-w-md overflow-hidden"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ type: "spring", damping: 25 }}
      >
        <div className="p-6 sm:p-8">
          <h2 className="text-3xl font-bold text-center mb-2">
            {getResultMessage()}
          </h2>
          <p className="text-gray-300 text-center mb-8">{getSubtitle()}</p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCloseModal()}
              className="px-4 py-3 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-medium transition-colors"
            >
              See Board
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={playAgain}
              className="px-4 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-colors"
            >
              Play Again
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onExit}
              className="px-4 py-3 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium transition-colors"
            >
              Exit Game
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default GameOverModal;
