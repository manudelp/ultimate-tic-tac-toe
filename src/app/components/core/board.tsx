import React, { useState } from "react";
import MiniBoard from "@/app/components/core/miniboard";
import GameOverModal from "../ui/game-over";
import { useGame } from "../../hooks/useGame";
import { motion } from "framer-motion";

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}
interface BoardProps {
  gameMode: string;
  bot: BotListResponse | null;
  starts: string | null;
  onExit: () => void;
}

const Board: React.FC<BoardProps> = ({ gameMode, bot, starts, onExit }) => {
  bot = bot || { id: 0, name: "", icon: "" };

  const [closeModal, setCloseModal] = useState(false);

  const {
    board,
    turn,
    lastMove,
    activeMiniBoard,
    winners,
    disabled,
    winningLine,
    gameWinner,
    isBotThinking,
    moveNumber,
    timeToMove,
    gameOver,
    handleCellClick,
    makeMove,
    resetGame,
  } = useGame(gameMode, bot, starts || "player");

  const handlePlayAgain = () => {
    setCloseModal(true);
    setTimeout(() => {
      resetGame();
      setCloseModal(false);
    }, 0);
  };

  return (
    <div className="relative w-full sm:w-[600px]">
      <div className="flex items-center justify-between">
        <div className="flex gap-2 cursor-pointer">
          <div title="Exit Game" onClick={onExit}>
            <svg
              className={`${gameOver && "stroke-green-300 animate-pulse"}`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="24"
              height="24"
              strokeWidth="2"
            >
              <path d="M13 12v.01"></path>
              <path d="M3 21h18"></path>
              <path d="M5 21v-16a2 2 0 0 1 2 -2h7.5m2.5 10.5v7.5"></path>
              <path d="M14 7h7m-3 -3l3 3l-3 3"></path>
            </svg>
          </div>
          {gameMode === "player-vs-bot" && (
            <div title={bot?.icon + " " + bot?.name}>
              {window.innerWidth > 768 ? bot?.icon + bot?.name : bot?.icon}
            </div>
          )}
          <div title="Move number">{moveNumber}</div>
        </div>
        <div
          title="Game Mode"
          className="w-fit absolute inset-x-0 m-auto text-center cursor-default"
        >
          {gameMode === "player-vs-player" && (
            <h2 className="bg-blue-500 px-2 rounded-full text-sm uppercase">
              PvP
            </h2>
          )}
          {gameMode === "player-vs-bot" && (
            <h2 className="bg-green-500 px-2 rounded-full text-sm uppercase">
              Fighting us
            </h2>
          )}
        </div>
        <div className="flex gap-2">
          {isBotThinking && (
            <div
              title="Bot's move time"
              style={{
                // TODO: Remove this before final release
                color:
                  timeToMove >= 10
                    ? "red"
                    : timeToMove >= 5
                    ? "yellow"
                    : "inherit",
              }}
            >
              {timeToMove.toFixed(2)}s
            </div>
          )}
          <div
            title="Player"
            className="truncate sm:max-w-[150px] text-end overflow-hidden"
          >
            {gameMode === "player-vs-player" && "Player"}
            {gameMode === "player-vs-bot" &&
              (turn === "X"
                ? starts === "player"
                  ? "You"
                  : bot?.name
                : starts === "player"
                ? bot?.name
                : "You")}
          </div>
          <div title="Turn">{turn}</div>
        </div>
      </div>
      <div className="flex flex-wrap gap-4 text-white">
        {/* BOARD */}
        <div className="w-full sm:w-[600px] h-full sm:h-[600px] aspect-square flex flex-wrap relative">
          {board.map((miniBoardRow: string[][][], localRowIndex: number) =>
            miniBoardRow.map((miniBoard: string[][], localColIndex) => (
              <MiniBoard
                key={`${localRowIndex}-${localColIndex}`}
                miniBoard={miniBoard}
                localRowIndex={localRowIndex}
                localColIndex={localColIndex}
                winners={winners}
                disabled={disabled}
                activeMiniBoard={activeMiniBoard}
                lastMove={lastMove}
                gameOver={gameOver}
                handleCellClick={handleCellClick}
                makeMove={makeMove}
              />
            ))
          )}
          {winningLine && (
            <div
              className="absolute w-full h-full pointer-events-none"
              style={{
                top: 0,
                left: 0,
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              {winningLine.type === "row" && (
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "95%" }}
                  transition={{ duration: 0.5 }}
                  className="absolute w-[95%] h-2 bg-red-500 rounded-full"
                  style={{ top: `${(winningLine.index + 0.5) * 33.33}%` }}
                />
              )}
              {winningLine.type === "col" && (
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: "95%" }}
                  transition={{ duration: 0.5 }}
                  className="absolute h-[95%] w-2 bg-red-500 rounded-full"
                  style={{ left: `${(winningLine.index + 0.5) * 33.33}%` }}
                />
              )}
              {winningLine.type === "diag" && winningLine.index === 0 && (
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 0.5 }}
                  className="absolute w-full h-2 bg-red-500 rounded-full"
                  style={{
                    transform: "rotate(45deg)",
                    width: "120%",
                    top: "50%",
                    left: "-10%",
                  }}
                />
              )}
              {winningLine.type === "diag" && winningLine.index === 1 && (
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 0.5 }}
                  className="absolute w-full h-2 bg-red-500 rounded-full"
                  style={{
                    transform: "rotate(-45deg)",
                    width: "120%",
                    top: "50%",
                    left: "-10%",
                  }}
                />
              )}
            </div>
          )}
        </div>
      </div>

      {/* GAME INFO */}
      <div className="flex items-center justify-between">
        {/* MATCH INFO - PLAYER VS BOT */}
        {gameMode === "player-vs-bot" && starts && !gameOver && !lastMove && (
          <h2>{starts === "player" ? "You start" : bot?.name + " starts"}</h2>
        )}
      </div>

      {/* GAME OVER */}
      {gameOver && (
        <GameOverModal
          gameWinner={gameWinner}
          gameMode={gameMode}
          bot={bot}
          starts={starts}
          closeModal={closeModal}
          setCloseModal={() => setCloseModal(true)}
          playAgain={handlePlayAgain}
          onExit={onExit}
        />
      )}
    </div>
  );
};

export default Board;
