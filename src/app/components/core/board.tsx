import React, { useEffect } from "react";
import MiniBoard from "@/app/components/core/miniboard";
import { useGame } from "../../hooks/useGame";

interface BoardProps {
  gameMode: string;
  starts: string | null;
  totalGames: number | null;
  lobbyId: string | null;
  playerId: string | null;
  userLetter: string | null;
  onlineStarts: string | null;
  resetBoard: boolean;
  onReset: () => void;
  onExit: () => void;
}

const Board: React.FC<BoardProps> = ({
  gameMode,
  starts,
  lobbyId,
  playerId,
  userLetter,
  onlineStarts,
  totalGames,
  resetBoard,
  onReset,
  onExit,
}) => {
  const {
    board,
    turn,
    lastMove,
    activeMiniBoard,
    winners,
    disabled,
    winningLine,
    agentId,
    agentId2,
    agentIdTurn,
    playedGames,
    winPercentages,
    gameWinner,
    isBotThinking,
    moveNumber,
    handleCellClick,
    makeMove,
  } = useGame(
    gameMode,
    starts || "player",
    lobbyId,
    playerId,
    userLetter,
    onlineStarts,
    totalGames || 0,
    resetBoard
  );

  const [play, setPlay] = React.useState(false);

  useEffect(() => {
    return () => {
      onReset();
    };
  }, [onReset]);

  return (
    <div className="relative w-full sm:w-[600px]">
      <div className="flex items-center justify-between">
        <div className="flex gap-2 cursor-pointer">
          <div onClick={onExit}>
            <svg
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
          <div>
            <svg
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
              <path d="M9 14l-4 -4l4 -4"></path>
              <path d="M5 10h11a4 4 0 1 1 0 8h-1"></path>
            </svg>
          </div>
          {gameMode === "bot-vs-bot" && (
            <div onClick={() => setPlay(!play)}>
              {play ? (
                <svg
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
                  <path d="M7 4v16l13 -8z"></path>
                </svg>
              ) : (
                <svg
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
                  <path d="M6 5m0 1a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1z"></path>
                  <path d="M14 5m0 1a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1z"></path>
                </svg>
              )}
            </div>
          )}
          <div>
            <svg
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
              <path d="M15 14l4 -4l-4 -4"></path>
              <path d="M19 10h-11a4 4 0 1 0 0 8h1"></path>
            </svg>
          </div>
          <div>{moveNumber}</div>
        </div>
        <div className="absolute w-40 inset-x-0 m-auto text-center">
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
          {gameMode === "online" && (
            <h2 className="bg-yellow-500 px-2 rounded-full text-sm uppercase">
              Online
            </h2>
          )}
        </div>
        <div className="flex gap-2">
          <div>
            {gameMode === "player-vs-player" && "Player"}
            {gameMode === "player-vs-bot" && (turn === "X" ? "You" : agentId)}
            {gameMode === "bot-vs-bot" &&
              (turn === agentIdTurn ? agentId : agentId2)}
            {gameMode === "online" &&
              (turn === userLetter ? "You" : "Opponent")}
          </div>
          <div>{turn}</div>
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
      </div>

      {/* GAME INFO */}
      <div className="flex items-center justify-between">
        {/* WHO STARTS */}
        {gameMode === "player-vs-bot" && starts && (
          <h2>{starts === "player" ? "You start" : agentId + " starts"}</h2>
        )}

        {/* IS BOT THINKING */}
        {gameMode === "player-vs-bot" && isBotThinking && (
          <div>{agentId} is thinking...</div>
        )}

        {/* MATCH INFO - BOT VS BOT */}
        {gameMode === "bot-vs-bot" && (
          <>
            {playedGames + "/" + totalGames}

            <div className="flex gap-2">
              <div>
                {(agentId?.slice(-2) ?? "") + (winPercentages[1] ?? 0) + "%"}
              </div>
              <div>
                {(agentId2?.slice(-2) ?? "") + (winPercentages[0] ?? 0) + "%"}
              </div>
              <div>{"🟰" + (winPercentages[2] ?? 0) + "%"}</div>
            </div>
          </>
        )}

        {/* GAME WINNER */}
        {gameWinner && (
          <>
            {gameMode === "player-vs-bot" && (
              <h2>
                {gameWinner === "X"
                  ? "You win!"
                  : gameWinner === "O"
                  ? agentId + " wins! You lose!"
                  : "Draw!"}
              </h2>
            )}

            {/* Show game winner in player vs player */}
            {gameMode === "player-vs-player" && (
              <h2>
                {gameWinner === "X"
                  ? "Player X wins!"
                  : gameWinner === "O"
                  ? "Player O wins!"
                  : "Draw!"}
              </h2>
            )}

            {/* Show game winner in bot vs bot */}
            {gameMode === "bot-vs-bot" && (
              <h2>
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
        {/* {playedGames === totalGames && (
          <>
            <table className="w-full text-sm text-center sm:text-start ">
              <thead>
                <tr>
                  <th className="text-start">Agent</th>
                  <th className="text-start">Win Percentage</th>
                  <th className="text-start">Games Won</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="text-start">
                    {agentId} ({agentIdTurn})
                  </td>
                  <td
                    className="text-start"
                    style={{
                      color:
                        winPercentages[1] > winPercentages[0] ? "green" : "red",
                    }}
                  >
                    {winPercentages[1]}%
                  </td>
                  <td className="text-start">
                    {Math.round((winPercentages[1] / 100) * playedGames)}
                  </td>
                </tr>
                <tr>
                  <td className="text-start">
                    {agentId2} ({agentId2Turn})
                  </td>
                  <td
                    className="text-start"
                    style={{
                      color:
                        winPercentages[0] > winPercentages[1] ? "green" : "red",
                    }}
                  >
                    {winPercentages[0]}%
                  </td>
                  <td className="text-start">
                    {Math.round((winPercentages[0] / 100) * playedGames)}
                  </td>
                </tr>
                <tr>
                  <td>Draw</td>
                  <td>{winPercentages[2]}%</td>
                  <td>{Math.round((winPercentages[2] / 100) * playedGames)}</td>
                </tr>
              </tbody>
            </table>
            <h2 className="text-lg sm:text-2xl md:text-4xl">
              Winner:{" "}
              {winPercentages[1] > winPercentages[0]
                ? `${agentId} (${agentIdTurn})`
                : winPercentages[0] > winPercentages[1]
                ? `${agentId2} (${agentId2Turn})`
                : "None! (Draw)"}
            </h2>
          </>
        )} */}

        {/* ONLINE INFO */}
        {gameMode === "online" && (
          <>
            <h2
              title="Click to Copy!"
              className="cursor-pointer"
              onClick={() => navigator.clipboard.writeText(lobbyId || "")}
            >
              Lobby ID
            </h2>
            <p>{onlineStarts} starts</p>
            <h2>You are {userLetter}</h2>
          </>
        )}
      </div>
    </div>
  );
};

export default Board;
