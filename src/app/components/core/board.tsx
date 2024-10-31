import React, { useEffect } from "react";
import MiniBoard from "@/app/components/core/miniboard";
import { useGame } from "../../hooks/useGame";

interface BoardProps {
  gameMode: string;
  starts?: string | null;
  botMatch?: number | null;
  resetBoard: boolean;
  onReset: () => void;
}

const Board: React.FC<BoardProps> = ({
  gameMode,
  starts,
  botMatch,
  resetBoard,
  onReset,
}) => {
  const {
    board,
    turn,
    lastMove,
    gameOver,
    activeMiniBoard,
    winners,
    disabled = [],
    winningLine,
    agentId,
    agentId2,
    agentIdTurn,
    agentId2Turn,
    playedGames,
    winPercentages,
    gameWinner,
    isBotThinking,
    handleCellClick,
    makeMove,
  } = useGame(gameMode, starts || "player", botMatch || 0, resetBoard);

  const progressPercentage = (playedGames / (botMatch || 1)) * 100;

  useEffect(() => {
    return () => {
      onReset();
    };
  }, [onReset]);

  return (
    <div className="w-screen h-full flex">
      <div
        className={`w-[600px] h-full aspect-square flex flex-wrap relative ${
          gameOver ? "pointer-events-none opacity-50" : ""
        }`}
      >
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
                className="absolute w-full h-2 bg-red-500"
                style={{ top: `${(winningLine.index + 0.5) * 33.33}%` }}
              />
            )}
            {winningLine.type === "col" && (
              <div
                className="absolute h-full w-2 bg-red-500"
                style={{ left: `${(winningLine.index + 0.5) * 33.33}%` }}
              />
            )}
            {winningLine.type === "diag" && winningLine.index === 0 && (
              <div
                className="absolute w-full h-2 bg-red-500"
                style={{
                  transform: "rotate(45deg)",
                  width: "141.42%",
                  top: "50%",
                  left: "-20.71%",
                }}
              />
            )}
            {winningLine.type === "diag" && winningLine.index === 1 && (
              <div
                className="absolute w-full h-2 bg-red-500"
                style={{
                  transform: "rotate(-45deg)",
                  width: "141.42%",
                  top: "50%",
                  left: "-20.71%",
                }}
              />
            )}
          </div>
        )}
      </div>
      <div className="w-full sm:w-auto flex flex-col gap-4 items-center sm:items-start">
        <h2 className="text-black dark:text-white text-lg sm:text-2xl uppercase">
          {gameMode.replace(/-/g, " ")}
        </h2>

        {gameMode === "player-vs-bot" && (
          <div className="">
            <h2 className="text-black dark:text-white text-lg sm:text-2xl">
              Playing against {agentId}
            </h2>
            {isBotThinking && (
              <div className="text-black dark:text-white text-sm sm:text-xl">
                {agentId} is thinking...
              </div>
            )}
          </div>
        )}

        {gameMode === "player-vs-bot" && starts && (
          <h2 className="text-black dark:text-white text-lg sm:text-2xl">
            {starts === "player" ? "You start" : agentId + " starts"}
          </h2>
        )}

        {gameMode === "bot-vs-bot" && (
          <div className="w-full">
            <div className="text-black dark:text-white text-lg sm:text-2xl">
              {agentId} ({agentIdTurn}) vs {agentId2} ({agentId2Turn})
            </div>
            {botMatch && (
              <>
                <div className="my-4 w-full flex gap-2">
                  <div className="w-full h-6 bg-black rounded-xl">
                    <div
                      className="w-full h-full bg-primary rounded-xl relative"
                      style={{ width: `${progressPercentage}%` }}
                    >
                      <p className="text-black dark:text-white font-medium absolute inset-y-0 right-2 m-0 p-0">
                        {playedGames}
                      </p>
                    </div>
                  </div>
                  <p className="text-black dark:text-white">{botMatch}</p>
                </div>
              </>
            )}
          </div>
        )}

        {gameMode === "bot-vs-bot" && isBotThinking && (
          <div className="text-black dark:text-white text-lg sm:text-xl">
            {turn === "O" ? agentId : agentId2} is thinking...
          </div>
        )}

        {gameMode === "player-vs-bot" && (
          <h2 className="text-black dark:text-white text-lg sm:text-2xl">
            Turn: {turn === "O --> " + agentId ? agentId : "X --> You"}
          </h2>
        )}

        {gameMode === "player-vs-player" && (
          <h2 className="text-black dark:text-white text-4xl">Turn: {turn}</h2>
        )}

        {gameWinner && (
          <>
            {gameMode === "player-vs-bot" && (
              <h2 className="text-black dark:text-white text-lg sm:text-2xl md:text-4xl">
                {gameWinner === "X"
                  ? "You win!"
                  : gameWinner === "O"
                  ? agentId + " wins! You lose!"
                  : "Draw!"}
              </h2>
            )}

            {gameMode === "player-vs-player" && (
              <h2 className="text-black dark:text-white sm:text-2xl md:text-4xl">
                {gameWinner === "X"
                  ? "Player X wins!"
                  : gameWinner === "O"
                  ? "Player O wins!"
                  : "Draw!"}
              </h2>
            )}

            {gameMode === "bot-vs-bot" && (
              <h2 className="text-black dark:text-white text-lg sm:text-2xl md:text-4xl">
                {gameWinner === "X"
                  ? agentId2 + " wins! (X)"
                  : gameWinner === "O"
                  ? agentId + " wins! (O)"
                  : "Draw!"}
              </h2>
            )}
          </>
        )}

        {playedGames === botMatch && (
          <>
            <div className="text-black dark:text-white text-sm">
              <p>
                {agentId} ({agentIdTurn}) Won {winPercentages[1]}% of the games
              </p>
              <p>
                {agentId2} ({agentId2Turn}) Won {winPercentages[0]}% of the
                games
              </p>
              <p>Draw Percentage: {winPercentages[2]}%</p>
            </div>
            <h2 className="text-black dark:text-white text-lg sm:text-2xl md:text-4xl">
              Winner:{" "}
              {winPercentages[1] > winPercentages[0]
                ? agentId
                : winPercentages[0] > winPercentages[1]
                ? agentId2
                : "None! (Draw)"}
            </h2>
          </>
        )}
      </div>
    </div>
  );
};

export default Board;
