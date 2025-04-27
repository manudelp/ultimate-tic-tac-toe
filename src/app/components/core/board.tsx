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
  isOnline: boolean;
  yourLetter?: string;
}

const Board: React.FC<BoardProps> = ({
  gameMode,
  bot,
  starts,
  onExit,
  isOnline,
  yourLetter,
}) => {
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
  } = useGame(gameMode, bot, starts || "player", yourLetter);

  const handlePlayAgain = () => {
    setCloseModal(true);
    setTimeout(() => {
      resetGame();
      setCloseModal(false);
    }, 0);
  };

  useEffect(() => {
    if (window.innerWidth < 768 && moveHistoryRef.current) {
      moveHistoryRef.current.scrollLeft = moveHistoryRef.current.scrollWidth;
    }
  }, [moveHistory]);

  useEffect(() => {
    if (window.innerWidth >= 768 && moveHistoryRef.current) {
      moveHistoryRef.current.scrollTop = moveHistoryRef.current.scrollHeight;
    }
  }, [moveHistory]);

  return (
    <div className="relative w-full max-h-[600px] gap-4 sm:grid sm:grid-cols-3">
      {/* GAME INFO DESKTOP */}
      {window.innerWidth >= 768 && (
        <div className="relative w-1/2 max-h-[600px] bg-gray-800 rounded-md justify-self-end p-4">
          {/* Game Mode */}
          {gameMode === "player-vs-bot" && (
            <div className="flex items-center gap-4">
              <div className="grid text-4xl bg-gray-700 rounded-lg w-14 h-14 place-items-center">
                {bot?.icon}
              </div>
              <p className="text-2xl font-medium">{bot?.name}</p>
              <p>
                <small>{isBotThinking ? "Thinking..." : "Your turn"}</small>
              </p>
            </div>
          )}

          {gameMode === "player-vs-player" && !isOnline && (
            <div className="text-2xl font-medium">
              Local match {new Date().toLocaleDateString()}
            </div>
          )}

          {/* Current Turn */}
          <div className="mt-4">
            <h3 className="text-lg font-semibold text-gray-300">
              Current Turn
            </h3>
            <p className="text-2xl font-bold text-green-400">{turn}</p>
          </div>

          {/* Move Number */}
          <div className="mt-4">
            <h3 className="text-lg font-semibold text-gray-300">Move Number</h3>
            <p className="text-2xl font-bold text-gray-200">{moveNumber}</p>
          </div>

          {/* Game Mode */}
          <div className="mt-4">
            <h3 className="text-lg font-semibold text-gray-300">Game Mode</h3>
            <p className="text-xl text-gray-200">
              {gameMode === "player-vs-player"
                ? "Player vs Player"
                : `Playing against ${bot?.name}`}
            </p>
          </div>

          {/* Time to Move */}
          {gameMode === "player-vs-bot" && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold text-gray-300">
                {bot?.name} has thoutght for
              </h3>
              <p className="text-2xl font-bold text-gray-200">
                {timeToMove.toFixed(2)}s
              </p>
            </div>
          )}

          {/* Game Winner */}
          {gameOver && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold text-gray-300">
                Game Winner
              </h3>
              <p className="text-2xl font-bold text-green-400">
                {gameWinner || "Draw"}
              </p>
            </div>
          )}

          {/* Exit game */}
          <button
            className="absolute bottom-0 left-0 right-0 max-w-full px-6 py-3 m-2 transition-colors bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-red-500 hover:bg-red-600"
            onClick={onExit}
            aria-label="Exit Game"
          >
            Exit Game
          </button>
        </div>
      )}

      {/* GAME INFO MOBILE */}
      {window.innerWidth < 768 && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-800 rounded-md shadow-md">
          {/* Exit and Move Number */}
          <div className="flex items-center gap-4 cursor-pointer">
            <div
              title="Exit Game"
              onClick={onExit}
              className="flex items-center justify-center transition-colors rounded-full"
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
      )}

      <div className="flex flex-wrap gap-4 text-white">
        {/* BOARD */}
        <div className="relative flex flex-wrap w-full sm:w-[600px] max-h-[600px] aspect-square">
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
                  className="absolute left-0 right-0 h-2 bg-red-500 rounded-full"
                  style={{
                    top: `${(winningLine.index + 0.5) * (100 / 3)}%`,
                    transform: "translateY(-50%)",
                  }}
                />
              )}
              {winningLine.type === "col" && (
                <div
                  className="absolute top-0 bottom-0 w-2 bg-red-500 rounded-full"
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

      {/* MOVE HISTORY DESKTOP */}
      {window.innerWidth >= 768 && (
        <div className="w-1/2 max-h-[600px] p-4 bg-gray-800 rounded-md">
          <h3 className="px-2 mb-2 text-sm text-gray-400">Move History</h3>
          <div
            ref={moveHistoryRef}
            className="w-full max-h-[95%] overflow-y-auto"
            style={{ scrollBehavior: "smooth" }}
          >
            <table className="w-full text-left text-gray-300">
              <thead className="sticky top-0 bg-gray-800">
                <tr>
                  <th className="px-2 py-1 border-b border-gray-700">#</th>
                  <th className="px-2 py-1 border-b border-gray-700">Turn</th>
                  <th className="px-2 py-1 border-b border-gray-700">
                    Coordinates
                  </th>
                </tr>
              </thead>
              <tbody>
                {moveHistory.map((move: any, index: number) => (
                  <tr
                    key={index}
                    className={`hover:text-green-400 cursor-pointer ${
                      index === moveHistory.length - 1 ? "font-bold" : ""
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
                    <td className="px-2 py-1 whitespace-nowrap">{index + 1}</td>
                    <td className="px-2 py-1 whitespace-nowrap">{move.turn}</td>
                    <td className="px-2 py-1 whitespace-nowrap">
                      ({move.coords.join(", ")})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MOVE HISTORY MOBILE */}
      {window.innerWidth < 768 && (
        <div className="w-full mt-6">
          <h3 className="px-2 mb-2 text-sm text-gray-400">Move History</h3>
          <div
            ref={moveHistoryRef}
            className="w-full max-w-full px-2 py-2 overflow-x-auto text-sm bg-gray-800 rounded-md whitespace-nowrap scrollbar-thin scrollbar-thumb-gray-500 scrollbar-track-gray-700"
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
      )}

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
