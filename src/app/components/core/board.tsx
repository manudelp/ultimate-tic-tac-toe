import React, { useState, useEffect, useRef } from "react";
import MiniBoard from "@/app/components/core/miniboard";
import GameOverModal from "../ui/game-over";
import { useGame } from "../../hooks/useGame";

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
  } = useGame(gameMode, bot, starts || "player");

  const handlePlayAgain = () => {
    setCloseModal(true);
    setTimeout(() => {
      resetGame();
      setCloseModal(false);
    }, 0);
  };

  useEffect(() => {
    if (moveHistoryRef.current) {
      moveHistoryRef.current.scrollLeft = moveHistoryRef.current.scrollWidth;
    }
  }, [moveHistory]);

  return (
    <div className="relative w-full sm:w-[600px]">
      <div className="flex items-center justify-between py-2 px-4 bg-gray-800 rounded-md shadow-md">
        {/* Exit and Move Number */}
        <div className="flex items-center gap-4 cursor-pointer">
          <div
            title="Exit Game"
            onClick={onExit}
            className="flex items-center justify-center rounded-full transition-colors"
          >
            <svg
              className={`w-5 h-5 text-white ${
                gameOver && "stroke-green-300 animate-pulse"
              }`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
            >
              <path d="M13 12v.01"></path>
              <path d="M3 21h18"></path>
              <path d="M5 21v-16a2 2 0 0 1 2 -2h7.5m2.5 10.5v7.5"></path>
              <path d="M14 7h7m-3 -3l3 3l-3 3"></path>
            </svg>
          </div>
          <div
            title="Move Number"
            className="text-sm font-medium text-gray-300"
          >
            {moveNumber}
          </div>
        </div>

        {/* Game Mode Info */}
        {gameMode === "player-vs-bot" && (
          <div
            title={bot?.name + " " + bot?.icon}
            className="text-sm font-medium text-gray-300 truncate"
          >
            {!isBotThinking &&
              (window.innerWidth < 768
                ? bot?.name + " " + bot?.icon
                : `You vs ${bot?.name} ${bot?.icon}`)}
          </div>
        )}

        {/* Player Info and Turn */}
        <div className="flex items-center gap-4">
          {isBotThinking && (
            <div className="text-sm font-medium" title="Bot's move time">
              {timeToMove.toFixed(2)}s
            </div>
          )}
          <div
            title="Player"
            className="text-sm font-medium text-gray-300 truncate sm:max-w-[150px] text-end overflow-hidden"
          >
            {gameMode === "player-vs-player" && "Player"}
            {gameMode === "player-vs-bot" &&
              (turn === "X"
                ? starts === "player"
                  ? "You"
                  : bot?.icon + " " + bot?.name
                : starts === "player"
                ? bot?.icon + " " + bot?.name
                : "You")}
          </div>
          <div title="Turn" className="text-sm font-bold text-green-400">
            {turn}
          </div>
        </div>
      </div>
      <div className="flex flex-wrap gap-4 text-white mt-4">
        {/* BOARD */}
        <div className="w-full aspect-square flex flex-wrap relative">
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
            <div className="absolute inset-0 pointer-events-none">
              {winningLine.type === "row" && (
                <div
                  className="absolute h-2 bg-red-500 rounded-full left-0 right-0"
                  style={{
                    top: `${(winningLine.index + 0.5) * (100 / 3)}%`,
                    transform: "translateY(-50%)",
                  }}
                />
              )}
              {winningLine.type === "col" && (
                <div
                  className="absolute w-2 bg-red-500 rounded-full top-0 bottom-0"
                  style={{
                    left: `${(winningLine.index + 0.5) * (100 / 3)}%`,
                    transform: "translateX(-50%)",
                  }}
                />
              )}
              {winningLine.type === "diag" && winningLine.index === 0 && (
                <div
                  className="absolute h-2 bg-red-500 rounded-full"
                  style={{
                    width: "140%",
                    top: "50%",
                    left: "-20%",
                    transform: "rotate(45deg) translateY(-50%)",
                    transformOrigin: "center",
                  }}
                />
              )}
              {winningLine.type === "diag" && winningLine.index === 1 && (
                <div
                  className="absolute h-2 bg-red-500 rounded-full"
                  style={{
                    width: "140%",
                    top: "50%",
                    left: "-20%",
                    transform: "rotate(-45deg) translateY(-50%)",
                    transformOrigin: "center",
                  }}
                />
              )}
            </div>
          )}
        </div>
      </div>
      {/* GAME INFO */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mt-4 gap-2">
        {/* MATCH INFO - PLAYER VS BOT */}
        {gameMode === "player-vs-bot" && starts && !gameOver && !lastMove && (
          <h2>{starts === "player" ? "You start" : bot?.name + " starts"}</h2>
        )}
      </div>

      {/* MOVE HISTORY */}
      <div className="mt-6 w-full">
        <h3 className="text-sm text-gray-400 mb-2 px-2">Move History</h3>
        <div
          ref={moveHistoryRef}
          className="w-full max-w-full overflow-x-auto whitespace-nowrap px-2 py-2 bg-gray-800 rounded-md scrollbar-thin scrollbar-thumb-gray-500 scrollbar-track-gray-700 text-sm"
        >
          <div className="inline-flex gap-4">
            {moveHistory.map((move, index) => (
              <div
                key={index}
                className={`hover:text-green-400 cursor-pointer ${
                  index === moveHistory.length - 1 ? "underline" : ""
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
                {index + 1}. {move.turn}: ({move.coords.join(", ")})
              </div>
            ))}
          </div>
        </div>
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
