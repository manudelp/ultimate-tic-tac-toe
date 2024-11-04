import React, { useEffect } from "react";
import MiniBoard from "@/app/components/core/miniboard";
import { useGame } from "../../hooks/useGame";

interface BoardProps {
  gameMode: string;
  starts?: string | null;
  totalGames?: number | null;
  resetBoard: boolean;
  onReset: () => void;
}

const Board: React.FC<BoardProps> = ({
  gameMode,
  starts,
  totalGames,
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
    disabled,
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
  } = useGame(gameMode, starts || "player", totalGames || 0, resetBoard);

  const progressPercentage = (playedGames / (totalGames || 1)) * 100;

  useEffect(() => {
    return () => {
      onReset();
    };
  }, [onReset]);

  return (
    <>
      {/* PLAYING AGAINST - PLAYER VS BOT */}
      {gameMode === "player-vs-bot" && (
        <div className="py-4">
          <h2 className="flex items-center gap-2 text-lg sm:text-2xl">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-8"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
              />
            </svg>
            {agentId}
          </h2>
        </div>
      )}

      <div className="h-full flex flex-wrap gap-4 p-2 text-white">
        {/* BOARD */}
        <div
          className={`w-full sm:w-[600px] h-full aspect-square flex flex-wrap relative ${
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

        {/* GAME INFO */}
        <div className="w-full sm:w-auto flex flex-col gap-4 items-center sm:items-start">
          {/* GAME MODE */}
          {gameMode === "player-vs-player" && (
            <h2 className="bg-blue-500 px-2 rounded-full text-sm uppercase">
              Player vs Player
            </h2>
          )}
          {gameMode === "player-vs-bot" && (
            <h2 className="bg-green-500 px-2 rounded-full text-sm uppercase">
              Player vs Bot
            </h2>
          )}
          {gameMode === "bot-vs-bot" && (
            <h2 className="bg-red-500 px-2 rounded-full text-sm uppercase">
              Bot vs Bot
            </h2>
          )}

          {/* WHO STARTS */}
          {gameMode === "player-vs-bot" && starts && !lastMove && (
            <h2 className="text-lg sm:text-2xl">
              {starts === "player" ? "You start" : agentId + " starts"}
            </h2>
          )}

          {/* MATCH INFO - BOT VS BOT */}
          {gameMode === "bot-vs-bot" && (
            <div className="w-full">
              <div className="text-lg sm:text-2xl text-center sm:text-start">
                {agentId} ({agentIdTurn}) vs {agentId2} ({agentId2Turn})
              </div>
              {totalGames && (
                <div className="my-4">
                  <p className="text-indigo-500 p-0 m-0">Games played:</p>
                  <div className="w-full flex gap-2">
                    <div className="w-full h-6 bg-gray-500 rounded-full overflow-hidden relative">
                      <div
                        className="h-full bg-indigo-500"
                        style={{ width: `${progressPercentage}%` }}
                      />
                      <p className="font-medium text-white absolute inset-y-0 right-2 m-0 p-0">
                        {playedGames + "/" + totalGames}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {playedGames > 0 && playedGames < (totalGames || 0) && (
                <div className="text-sm text-center sm:text-start">
                  <p>
                    {agentId} ({agentIdTurn}) won{" "}
                    <span
                      style={{
                        color:
                          winPercentages[1] > winPercentages[0]
                            ? "green"
                            : "red",
                      }}
                    >
                      {winPercentages[1]}%
                    </span>{" "}
                    of the games
                  </p>
                  <p>
                    {agentId2} ({agentId2Turn}) won{" "}
                    <span
                      style={{
                        color:
                          winPercentages[0] > winPercentages[1]
                            ? "green"
                            : "red",
                      }}
                    >
                      {winPercentages[0]}%
                    </span>{" "}
                    of the games
                  </p>
                  <p>Draw Percentage: {winPercentages[2]}%</p>
                </div>
              )}
            </div>
          )}

          {/* IS BOT THINKING */}
          {gameMode === "bot-vs-bot" && isBotThinking && (
            <div className="text-lg sm:text-xl">
              {turn === "O" ? agentId : agentId2} is thinking...
            </div>
          )}

          {/* TURN PLAYER VS BOT*/}
          {gameMode === "player-vs-bot" && (
            <h2 className="text-lg sm:text-2xl">
              Turn: {turn === "X" ? `You (${turn})` : `${agentId} (${turn})`}
            </h2>
          )}

          {isBotThinking && (
            <div className="text-sm sm:text-xl">{agentId} is thinking...</div>
          )}

          {/* TURN PLAYER VS PLAYER */}
          {gameMode === "player-vs-player" && (
            <h2 className="text-4xl">Turn: {turn}</h2>
          )}

          {/* GAME WINNER */}
          {gameWinner && (
            <>
              {gameMode === "player-vs-bot" && (
                <h2 className="text-lg sm:text-2xl md:text-4xl">
                  {gameWinner === "X"
                    ? "You win!"
                    : gameWinner === "O"
                    ? agentId + " wins! You lose!"
                    : "Draw!"}
                </h2>
              )}

              {/* Show game winner in player vs player */}
              {gameMode === "player-vs-player" && (
                <h2 className="sm:text-2xl md:text-4xl">
                  {gameWinner === "X"
                    ? "Player X wins!"
                    : gameWinner === "O"
                    ? "Player O wins!"
                    : "Draw!"}
                </h2>
              )}

              {/* Show game winner in bot vs bot */}
              {gameMode === "bot-vs-bot" && (
                <h2 className="text-lg sm:text-2xl md:text-4xl">
                  {gameWinner === "X"
                    ? agentId2 + " wins! (X)"
                    : gameWinner === "O"
                    ? agentId + " wins! (O)"
                    : "Draw!"}
                </h2>
              )}
            </>
          )}

          {/* WINNER PERCENTAGES */}
          {playedGames === totalGames && (
            <>
              <div className="text-sm">
                <p>
                  {agentId} ({agentIdTurn}) Won {winPercentages[1]}% of the
                  games
                </p>
                <p>
                  {agentId2} ({agentId2Turn}) Won {winPercentages[0]}% of the
                  games
                </p>
                <p>Draw Percentage: {winPercentages[2]}%</p>
              </div>
              <h2 className="text-lg sm:text-2xl md:text-4xl">
                Winner:{" "}
                {winPercentages[1] > winPercentages[0]
                  ? `${agentId} (${agentIdTurn})`
                  : winPercentages[0] > winPercentages[1]
                  ? `${agentId2} (${agentId2Turn})`
                  : "None! (Draw)"}
              </h2>
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default Board;
