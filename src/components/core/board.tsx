import React, { useState, useEffect, useRef } from "react";
import MiniBoard from "@/components/core/miniboard";
import GameOverModal from "@/components/ui/game-over";
import { useGame } from "@/hooks/useGame";
import { motion } from "framer-motion"; // You'll need to install framer-motion

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}

interface BoardProps {
  gameMode: "player-vs-player" | "player-vs-bot" | "online";
  onExit: () => void;
  bot?: BotListResponse;
  starts?: string;
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
    <div className="relative flex flex-col w-full gap-6 mx-auto sm:px-4 max-w-7xl md:flex-row">
      {/* Game Board Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center flex-1"
      >
        {/* Game Info Bar */}
        <div className="flex items-center justify-between w-full px-4 py-3 mb-6 bg-gray-800 rounded top-10">
          <div className="flex items-center gap-3">
            <motion.div
              key={turn}
              initial={{ rotateY: -180 }}
              animate={{ rotateY: 0 }}
              transition={{ duration: 0.1 }}
              className={`w-10 h-10 flex items-center justify-center rounded-md ${
                turn === "X" ? "bg-blue-500/20" : "bg-red-500/20"
              }`}
              style={{ perspective: 600 }}
            >
              <span
                className={`text-2xl font-bold ${
                  turn === "X" ? "text-blue-400" : "text-red-400"
                }`}
              >
                {turn}
              </span>
            </motion.div>
            <div className="flex flex-col">
              <span className="text-xs font-medium text-gray-400">
                Current Turn
              </span>
              <span className="text-sm font-semibold text-white">
                {gameMode === "player-vs-bot" && isBotThinking
                  ? `${bot?.name + " " + bot?.icon} is thinking...`
                  : gameMode === "online" && turn !== yourLetter
                  ? "Opponent's turn"
                  : "Your turn"}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {gameMode === "online" && (
              <div className="px-2 py-1 ml-3 text-xs font-medium text-indigo-300 rounded-md bg-indigo-500/30">
                {lobbyCode}
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
          <div className="relative flex flex-wrap w-full aspect-square">
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
                    style={{
                      top: `${(100 / 3) * winningLine.index + 50 / 3 - 1}%`,
                    }}
                  />
                )}
                {winningLine.type === "col" && (
                  <div
                    className="absolute h-[95%] w-3 bg-gradient-to-b from-red-500 to-orange-500 rounded-full"
                    style={{
                      left: `${(100 / 3) * winningLine.index + 50 / 3 - 1}%`,
                    }}
                  />
                )}
                {winningLine.type === "diag" && winningLine.index === 0 && (
                  <div
                    className="absolute w-[130%] h-3 bg-gradient-to-tr from-red-500 to-orange-500 rounded-full"
                    style={{
                      transform: "rotate(45deg)",
                      top: "49.35%",
                    }}
                  />
                )}
                {winningLine.type === "diag" && winningLine.index === 1 && (
                  <div
                    className="absolute w-[130%] h-3 bg-gradient-to-br from-red-500 to-orange-500 rounded-full "
                    style={{
                      transform: "rotate(-45deg)",
                      top: "49.35%",
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
              className="w-full px-1 py-2 overflow-x-auto bg-gray-800 rounded scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
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
              className="flex items-center justify-center flex-1 gap-2 py-3 transition-colors bg-gray-700 rounded hover:bg-gray-600"
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
                className="flex items-center justify-center flex-1 gap-2 py-3 transition-colors bg-green-600 rounded hover:bg-green-500"
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
          <div className="p-6 bg-gray-800 rounded">
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
                  {gameMode === "player-vs-bot"
                    ? `Playing against ${bot?.name} ${bot?.icon}`
                    : gameMode === "online"
                    ? "Online Match"
                    : "Local"}
                </div>
              </div>

              {/* Bot Thinking Time */}
              {gameMode === "player-vs-bot" && (
                <div>
                  <div className="mb-1 text-sm text-gray-400">
                    {bot?.name}&apos;s Response Time
                  </div>
                  <div className="text-lg text-white">
                    {timeToMove >= 3600
                      ? `${Math.floor(timeToMove / 3600)}h ${Math.floor(
                          (timeToMove % 3600) / 60
                        )}m ${Math.round(timeToMove % 60)}s`
                      : timeToMove >= 60
                      ? `${Math.floor(timeToMove / 60)}m ${Math.round(
                          timeToMove % 60
                        )}s`
                      : `${timeToMove.toFixed(2)}s`}
                  </div>
                </div>
              )}

              {/* Game Status */}
              {gameOver ? (
                <div className="p-4 text-center bg-gray-700 rounded">
                  <div className="mb-1 text-sm text-gray-400">Game Result</div>
                  <div className="text-2xl font-bold text-green-400">
                    {gameWinner === "X" || gameWinner === "O"
                      ? `${gameWinner} Wins!`
                      : "Draw!"}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="mb-1 text-sm text-gray-400">Status</div>
                  <div className="text-lg text-green-400">
                    {isBotThinking
                      ? `${bot?.name + " " + bot?.icon} is thinking...`
                      : "Game in progress"}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Move History */}
          <div className="flex-1 p-4 bg-gray-800 rounded">
            <div className="flex items-center justify-between mb-2 text-sm text-gray-400">
              <span>Move History</span>
              <span className="text-xs">{moveHistory.length} moves</span>
            </div>
            <div
              ref={moveHistoryRef}
              className={`${
                gameMode === "player-vs-bot" ? "h-[200px]" : "h-[300px]"
              } pr-2 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent`}
            >
              <table className="w-full text-sm">
                <thead className="sticky top-0 z-10 bg-gray-800">
                  <tr className="text-xs text-gray-400">
                    <th className="p-2 font-normal text-left">#</th>
                    <th className="p-2 font-normal text-left">Turn</th>
                    <th className="p-2 font-normal text-left">Position</th>
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
                      <td className="p-2 rounded-l">{index + 1}</td>
                      <td
                        className={`p-2 ${
                          move.turn === "X" ? "text-blue-400" : "text-red-400"
                        } font-medium`}
                      >
                        {move.turn}
                      </td>
                      <td className="p-2 rounded-r">
                        ({move.coords.join(",")})
                      </td>
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
              className="flex items-center justify-center flex-1 gap-2 px-4 py-3 transition-colors bg-gray-700 rounded hover:bg-gray-600"
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
                className="flex items-center justify-center flex-1 gap-2 px-4 py-3 transition-colors bg-green-600 rounded hover:bg-green-500"
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
          starts={starts || null}
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
