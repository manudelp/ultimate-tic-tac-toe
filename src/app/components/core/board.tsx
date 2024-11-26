import React, { useState, useEffect, useRef } from "react";
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

          <div title="Move number">{moveNumber}</div>
        </div>
        {gameMode === "player-vs-bot" && (
          <div title={bot?.icon + " " + bot?.name}>
            You vs{" "}
            {window.innerWidth > 768 ? bot?.icon + " " + bot?.name : bot?.icon}
          </div>
        )}
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
                hoveredMove={hoveredMove} // Pass the hovered move to MiniBoard
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
                  className="absolute w-[95%] h-2 bg-red-500 rounded-full"
                  style={{ top: `${(winningLine.index + 0.5) * 33.33}%` }}
                />
              )}
              {winningLine.type === "col" && (
                <div
                  className="absolute h-[95%] w-2 bg-red-500 rounded-full"
                  style={{ left: `${(winningLine.index + 0.5) * 33.33}%` }}
                />
              )}
              {winningLine.type === "diag" && winningLine.index === 0 && (
                <div
                  className="absolute w-full h-2 bg-red-500 rounded-full"
                  style={{
                    transform: "rotate(45deg)",
                    width: "120%",
                    top: "50%",
                    left: "0",
                  }}
                />
              )}
              {winningLine.type === "diag" && winningLine.index === 1 && (
                <div
                  className="absolute w-full h-2 bg-red-500 rounded-full"
                  style={{
                    transform: "rotate(-45deg)",
                    width: "120%",
                    top: "50%",
                    left: "0",
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

        {/* MOVE HISTORY */}
        <div
          title="Move History"
          ref={moveHistoryRef}
          className="flex gap-4 max-w-full overflow-x-auto whitespace-nowrap scrollbar-thin scrollbar-thumb-gray-500 scrollbar-track-gray-700 cursor-help"
        >
          {moveHistory.map((move, index) => (
            <div
              key={index}
              className={`inline-block hover:text-green-500 ${
                index === moveHistory.length - 1 ? "underline" : ""
              }`}
              onMouseEnter={() =>
                handleMoveHover([
                  move.coords[0], // localRowIndex
                  move.coords[1], // localColIndex
                  move.coords[2], // rowIndex
                  move.coords[3], // cellIndex
                ])
              }
              onMouseLeave={() => handleMoveHover(null)}
            >
              {index + 1}. {move.turn}: ({move.coords.join(", ")})
            </div>
          ))}
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
