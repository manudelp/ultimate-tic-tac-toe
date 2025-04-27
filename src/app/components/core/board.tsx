import React, { useState, useEffect, useRef } from "react";
import MiniBoard from "@/app/components/core/miniboard";
import GameOverModal from "../ui/game-over";
import { useGame } from "../../hooks/useGame";
import { motion } from "framer-motion"; // You'll need to install framer-motion

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
  yourLetter?: string;
  lobbyCode?: string;
}

const Board: React.FC<BoardProps> = ({
  gameMode,
  bot,
  starts,
  onExit,
  yourLetter,
  lobbyCode,
}) => {
  bot = bot || { id: 0, name: "", icon: "" };

  const [closeModal, setCloseModal] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const moveHistoryRef = useRef<HTMLDivElement>(null);
  const [hoveredMove, setHoveredMove] = useState<
    [number, number, number, number] | null
  >(null);

  // Handle hovering over a move in the history
  const handleMoveHover = (coords: [number, number, number, number] | null) => {
    setHoveredMove(coords);
  };

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
    moveHistory,
    handleCellClick,
    makeMove,
    resetGame,
  } = useGame(gameMode, bot, starts || "player", yourLetter, lobbyCode);

  const handlePlayAgain = () => {
    setCloseModal(true);
    setTimeout(() => {
      resetGame();
      setCloseModal(false);
    }, 0);
  };

  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkIfMobile();
    window.addEventListener("resize", checkIfMobile);

    return () => window.removeEventListener("resize", checkIfMobile);
  }, []);

  useEffect(() => {
    if (moveHistoryRef.current) {
      if (isMobile) {
        moveHistoryRef.current.scrollLeft = moveHistoryRef.current.scrollWidth;
      } else {
        moveHistoryRef.current.scrollTop = moveHistoryRef.current.scrollHeight;
      }
    }
  }, [moveHistory, isMobile]);

  return (
    <div className="relative flex flex-col w-full gap-6 px-4 mx-auto max-w-7xl md:flex-row">
      {/* Game Board Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center flex-1"
      >
        {/* Game Info Bar */}
        <div className="w-full p-4 mb-4 bg-gray-800 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            {/* Player/Game Info */}
            <div className="flex items-center gap-3">
              {gameMode === "player-vs-bot" && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-10 h-10 text-3xl bg-gray-700 rounded-full">
                    {bot?.icon}
                  </div>
                  <div>
                    <p className="font-medium text-gray-200">{bot?.name}</p>
                    <p className="text-xs text-gray-400">
                      {isBotThinking ? (
                        <span className="flex items-center">
                          Thinking
                          <span className="flex ml-1">
                            <span className="animate-bounce mx-[1px] h-1 w-1 rounded-full bg-gray-400"></span>
                            <span className="animate-bounce mx-[1px] h-1 w-1 rounded-full bg-gray-400 animation-delay-100"></span>
                            <span className="animate-bounce mx-[1px] h-1 w-1 rounded-full bg-gray-400 animation-delay-200"></span>
                          </span>
                        </span>
                      ) : (
                        "Your turn"
                      )}
                    </p>
                  </div>
                </div>
              )}
              {gameMode === "online" && (
                <div className="flex items-center gap-2">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center
                  ${
                    yourLetter === "X" ? "bg-blue-500" : "bg-red-500"
                  } shadow-lg`}
                  >
                    {yourLetter}
                  </div>
                  <div>
                    <p className="font-medium text-gray-200">You</p>
                    <p
                      className={`text-xs ${
                        turn === yourLetter
                          ? "font-bold text-green-400"
                          : "text-gray-400"
                      }`}
                    >
                      {turn === yourLetter ? "Your turn" : "Your Letter"}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {gameMode === "online" ? (
              <div className="flex items-center gap-2">
                <div>
                  <p
                    className={`text-right text-xs ${
                      turn === yourLetter
                        ? "text-gray-400"
                        : "font-bold text-green-400"
                    }`}
                  >
                    {turn === yourLetter
                      ? "Playing against"
                      : "Opponent's turn"}
                  </p>
                  <p className="font-medium text-right text-gray-200">
                    Opponent
                  </p>
                </div>
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center
                ${yourLetter === "X" ? "bg-red-500" : "bg-blue-500"} shadow-lg`}
                >
                  {yourLetter === "X" ? "O" : "X"}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-xs text-gray-400">Current Turn</p>
                  {gameMode === "online" ? (
                    <p className="font-bold text-green-400">
                      {turn === yourLetter ? "Your Turn" : "Opponent's Turn"}
                    </p>
                  ) : (
                    <p className="font-bold text-green-400">{turn}</p>
                  )}
                </div>
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center
            ${turn === "X" ? "bg-blue-500" : "bg-red-500"} shadow-lg`}
                >
                  {turn}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Game Board */}
        <motion.div
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          className="relative w-full max-w-[min(calc(100vw-2rem),600px)] aspect-square"
        >
          <div className="absolute inset-0 bg-gray-700 rounded-lg shadow-xl -z-10"></div>

          <div className="relative flex flex-wrap w-full p-2 aspect-square">
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
                  hoveredMove={hoveredMove}
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
                  <div
                    className="absolute w-[95%] h-3 bg-gradient-to-r from-red-500 to-orange-500 rounded-full"
                    style={{ top: `${(winningLine.index + 0.5) * 33.33}%` }}
                  />
                )}
                {winningLine.type === "col" && (
                  <div
                    className="absolute h-[95%] w-3 bg-gradient-to-r from-red-500 to-orange-500 rounded-full"
                    style={{ left: `${(winningLine.index + 0.5) * 33.33}%` }}
                  />
                )}
                {winningLine.type === "diag" && winningLine.index === 0 && (
                  <div
                    className="absolute w-[140%] h-3 bg-gradient-to-r from-red-500 to-orange-500 rounded-full"
                    style={{
                      transform: "rotate(45deg)",
                      top: "50%",
                      left: "-19%",
                    }}
                  />
                )}
                {winningLine.type === "diag" && winningLine.index === 1 && (
                  <div
                    className="absolute w-[140%] h-3 bg-gradient-to-r from-red-500 to-orange-500 rounded-full"
                    style={{
                      transform: "rotate(-45deg)",
                      top: "50%",
                      left: "-19%",
                    }}
                  />
                )}
              </div>
            )}
          </div>
        </motion.div>

        {/* Mobile Move History */}
        {isMobile && (
          <div className="w-full mt-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400">
                Move History
              </h3>
              <div className="text-xs text-gray-500">
                Move #{moveNumber + 1}
              </div>
            </div>
            <div
              ref={moveHistoryRef}
              className="w-full px-1 py-2 overflow-x-auto bg-gray-800 rounded-lg shadow-inner scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
            >
              <div className="inline-flex gap-3 px-2">
                {moveHistory.map((move, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`cursor-pointer rounded-md px-2 py-1 ${
                      index === moveHistory.length - 1
                        ? "bg-gray-700 text-green-400"
                        : "hover:bg-gray-700/50"
                    }`}
                    onMouseEnter={() =>
                      handleMoveHover([
                        move.coords[0],
                        move.coords[1],
                        move.coords[2],
                        move.coords[3],
                      ])
                    }
                    onMouseLeave={() => handleMoveHover(null)}
                  >
                    <span className="text-xs text-gray-400">{index + 1}.</span>
                    <span
                      className={
                        move.turn === "X" ? "text-blue-400" : "text-red-400"
                      }
                    >
                      {move.turn}
                    </span>
                    <span className="ml-1 text-xs">
                      ({move.coords.join(",")})
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Game Controls for Mobile */}
        {isMobile && (
          <div className="flex w-full gap-4 mt-4">
            <button
              className="flex items-center justify-center flex-1 gap-2 py-3 transition-colors bg-gray-700 rounded-lg shadow-md hover:bg-gray-600"
              onClick={onExit}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Exit Game
            </button>
            {gameOver && (
              <button
                className="flex items-center justify-center flex-1 gap-2 py-3 transition-colors bg-green-600 rounded-lg shadow-md hover:bg-green-500"
                onClick={handlePlayAgain}
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Play Again
              </button>
            )}
          </div>
        )}
      </motion.div>

      {/* Info Panel (Desktop only) */}
      {!isMobile && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex flex-col gap-4 w-80"
        >
          {/* Game Stats Card */}
          <div className="p-6 bg-gray-800 rounded-lg shadow-lg">
            <div className="relative flex flex-col gap-6">
              {/* Today's Date */}
              <div className="absolute top-0 right-0 text-xs text-right text-gray-400">
                <div>
                  {new Date().toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                  })}
                </div>
                <div>
                  {new Date().toLocaleTimeString("en-US", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>

              {/* Move Details */}
              <div>
                <div className="mb-1 text-sm text-gray-400">Move</div>
                <div className="text-3xl font-bold text-white">
                  {moveNumber + 1}
                </div>
              </div>

              {/* Game Mode */}
              <div>
                <div className="mb-1 text-sm text-gray-400">Game Mode</div>
                <div className="text-lg text-white">
                  {gameMode === "player-vs-player"
                    ? "Player vs Player"
                    : gameMode === "player-vs-bot"
                    ? `vs ${bot?.name}`
                    : "Online Match"}
                </div>
              </div>

              {/* Bot Thinking Time */}
              {gameMode === "player-vs-bot" && (
                <div>
                  <div className="mb-1 text-sm text-gray-400">
                    Bot Response Time
                  </div>
                  <div className="text-lg text-white">
                    {timeToMove.toFixed(2)}s
                  </div>
                </div>
              )}

              {/* Game Status */}
              {gameOver ? (
                <div className="p-4 text-center bg-gray-700 rounded-lg">
                  <div className="mb-1 text-sm text-gray-400">Game Result</div>
                  <div className="text-2xl font-bold text-green-400">
                    {gameWinner ? `${gameWinner} Wins!` : "Draw!"}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="mb-1 text-sm text-gray-400">Status</div>
                  <div className="text-lg text-green-400">
                    {isBotThinking ? "Bot is thinking..." : "Game in progress"}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Move History */}
          <div className="flex-1 p-4 bg-gray-800 rounded-lg shadow-lg">
            <div className="flex items-center justify-between mb-2 text-sm text-gray-400">
              <span>Move History</span>
              <span className="text-xs">{moveHistory.length} moves</span>
            </div>
            <div
              ref={moveHistoryRef}
              className="max-h-[300px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
            >
              <table className="w-full text-sm">
                <thead className="sticky top-0 z-10 bg-gray-800">
                  <tr className="text-xs text-gray-400">
                    <th className="py-2 font-normal text-left">#</th>
                    <th className="py-2 font-normal text-left">Turn</th>
                    <th className="py-2 font-normal text-left">Position</th>
                  </tr>
                </thead>
                <tbody>
                  {moveHistory.map((move, index) => (
                    <motion.tr
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.03 }}
                      className={`hover:bg-gray-700/50 transition-colors cursor-pointer ${
                        index === moveHistory.length - 1 ? "bg-gray-700/30" : ""
                      }`}
                      onMouseEnter={() =>
                        handleMoveHover([
                          move.coords[0],
                          move.coords[1],
                          move.coords[2],
                          move.coords[3],
                        ])
                      }
                      onMouseLeave={() => handleMoveHover(null)}
                    >
                      <td className="py-2">{index + 1}</td>
                      <td
                        className={`py-2 ${
                          move.turn === "X" ? "text-blue-400" : "text-red-400"
                        } font-medium`}
                      >
                        {move.turn}
                      </td>
                      <td className="py-2">({move.coords.join(",")})</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Game Controls */}
          <div className="flex gap-2">
            <button
              onClick={onExit}
              className="flex items-center justify-center flex-1 gap-2 px-4 py-3 transition-colors bg-gray-700 rounded-lg shadow-md hover:bg-gray-600"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Exit Game
            </button>
            {gameOver && (
              <button
                onClick={handlePlayAgain}
                className="flex items-center justify-center flex-1 gap-2 px-4 py-3 transition-colors bg-green-600 rounded-lg shadow-md hover:bg-green-500"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Play Again
              </button>
            )}
          </div>
        </motion.div>
      )}

      {/* Game Over Modal */}
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
