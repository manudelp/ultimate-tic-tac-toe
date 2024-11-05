import React, { useState, useEffect, useCallback } from "react";
import { checkConnection, createLobby, joinLobby } from "@/api";
import Board from "@/app/components/core/board";
import PlayerX from "../ui/playerx";
import PlayerO from "../ui/playero";
import io from "socket.io-client";

const socket = io("http://localhost:5000");

const Dashboard: React.FC = () => {
  // Core
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [starts, setStarts] = useState<string | null>(null);
  const [totalGames, setTotalGames] = useState<number | null>(null);
  const [resetBoard, setResetBoard] = useState<boolean>(false);

  // Backend
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);

  // Online
  const [playerId, setPlayerId] = useState<string | null>(null);
  const [lobbyId, setLobbyId] = useState<string | null>(null);
  const [userLetter, setUserLetter] = useState<string | null>(null);
  const [onlineStarts, setOnlineStarts] = useState<string | null>(null);
  const [createdLobby, setCreatedLobby] = useState<boolean>(false);

  // Board visibility
  const isBoardVisible =
    gameMode &&
    (gameMode !== "player-vs-bot" || starts) &&
    (gameMode !== "bot-vs-bot" || totalGames) &&
    (gameMode !== "online" || (lobbyId && userLetter && onlineStarts));

  // Functions
  const selectMode = (mode: string) => {
    setGameMode(mode);
    setResetBoard(true);
    setStarts(null);
    setTotalGames(null);
  };

  const handleBoardReset = () => {
    setResetBoard(false);
  };

  const handleExitGame = () => {
    setGameMode(null);
    setResetBoard(true);
    setStarts(null);
    setTotalGames(null);
    setLobbyId(null);
    setUserLetter(null);
    setOnlineStarts(null);
    setCreatedLobby(false);
  };

  const handleCreateLobby = async (onlineStarts: string) => {
    const playerId = "player-" + Math.random().toString(36).substring(2, 12);
    setPlayerId(playerId);
    if (playerId && userLetter) {
      const response = await createLobby(playerId, userLetter, onlineStarts);
      if (response) {
        setLobbyId(response.lobby_id);
        setOnlineStarts(onlineStarts);
        socket.emit("join", {
          lobby_id: response.lobby_id,
          player_id: playerId,
          user_letter: userLetter,
          online_starts: starts,
        });
        console.log("Lobby created:", response.lobby_id);
      } else {
        alert("Failed to create lobby. Please try again.");
      }
    } else {
      alert("Player ID or user letter is not set. Please try again.");
    }
  };

  const handleJoinLobby = useCallback(async (lobbyId: string) => {
    const playerId = "player-" + Math.random().toString(36).substring(2, 12);
    const response = await joinLobby(lobbyId, playerId);
    if (response.status === "joined") {
      setLobbyId(lobbyId);
      setGameMode("online");
      socket.emit("join", {
        lobby_id: lobbyId,
        player_id: playerId,
      });
      console.log("Joined lobby:", lobbyId);
    } else {
      alert(response.message);
    }
  }, []);

  useEffect(() => {
    const checkBackendConnection = async () => {
      const isConnected = await checkConnection();
      setIsBackendConnected(isConnected);
    };

    checkBackendConnection();

    // Check if there's a lobby ID in the URL
    const urlParams = new URLSearchParams(window.location.search);
    const lobbyId = urlParams.get("lobbyId");
    if (lobbyId) {
      handleJoinLobby(lobbyId);
    }

    socket.on("game-started", (data) => {
      setUserLetter(data.user_letter);
      setOnlineStarts(data.online_starts);
      setLobbyId(data.lobby_id);
    });

    return () => {
      socket.off("game-started");
    };
  }, [handleJoinLobby]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 sm:p-8 text-white">
      <div className="text-center">
        {!isBoardVisible && (
          <>
            {/* Title */}
            <h1 className="text-4xl font-bold mb-8">Choose Your Game Mode</h1>

            {/* Choose Game Mode */}
            {gameMode === null && (
              <div className="flex flex-col sm:flex-row justify-center gap-6">
                <button
                  className="sm:w-64 py-4 bg-gray-800 hover:bg-gray-700 transition-colors font-medium text-lg"
                  onClick={() => selectMode("player-vs-player")}
                >
                  Player vs Player
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() =>
                    isBackendConnected && selectMode("player-vs-bot")
                  }
                  disabled={!isBackendConnected}
                >
                  Player vs Bot
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() => isBackendConnected && selectMode("bot-vs-bot")}
                  disabled={!isBackendConnected}
                >
                  Bot vs Bot
                </button>
                <button
                  disabled={!isBackendConnected}
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() => isBackendConnected && selectMode("online")}
                >
                  Online
                </button>
              </div>
            )}

            {/* Who Starts */}
            {gameMode === "player-vs-bot" && !starts && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Who Starts?</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="px-6 py-3 bg-red-500 hover:bg-red-400 transition-colors"
                    onClick={() => handleExitGame()}
                  >
                    Go Back
                  </button>
                  <button
                    className="px-6 py-3 bg-green-600 hover:bg-green-500 transition-colors"
                    onClick={() => setStarts("player")}
                  >
                    Player Starts
                  </button>
                  <button
                    className="px-6 py-3 bg-green-600 hover:bg-green-500 transition-colors"
                    onClick={() => setStarts("bot")}
                  >
                    Bot Starts
                  </button>
                </div>
              </div>
            )}

            {/* Number of Games */}
            {gameMode === "bot-vs-bot" && !totalGames && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Number of Games</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="px-6 py-3 bg-red-500 hover:bg-red-400 transition-colors"
                    onClick={() => handleExitGame()}
                  >
                    Go Back
                  </button>
                  <button
                    className="px-6 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setTotalGames(1)}
                  >
                    1 Game
                  </button>
                  <button
                    className="px-6 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setTotalGames(10)}
                  >
                    10 Games
                  </button>
                  <button
                    className="px-6 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
                    onClick={() => setTotalGames(100)}
                  >
                    100 Games
                  </button>
                  <form
                    className="flex gap-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      const input = (e.target as HTMLFormElement).querySelector(
                        "input"
                      );
                      if (input) {
                        const games = parseInt(input.value, 10);
                        setTotalGames(games);
                      }
                    }}
                  >
                    <input
                      className="w-full sm:w-24 px-3 py-2 border-b border-gray-500 bg-gray-900 focus:outline-none focus:border-gray-700 transition-colors"
                      type="number"
                      name="games"
                      placeholder="Custom"
                      min={1}
                    />
                    <button
                      className="w-1/2 sm:w-auto px-4 py-2 bg-gray-800 hover:bg-gray-700 transition-colors"
                      type="submit"
                    >
                      Set
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* Online Mode */}
            {gameMode === "online" && !createdLobby && (
              <>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() => setCreatedLobby(true)}
                  disabled={!isBackendConnected}
                >
                  Create Game
                </button>
                <button
                  className={`sm:w-64 py-4 transition-colors font-medium text-lg ${
                    isBackendConnected
                      ? "bg-gray-800 hover:bg-gray-700"
                      : "bg-gray-500 opacity-70 cursor-not-allowed"
                  }`}
                  onClick={() => {
                    const lobbyId = prompt("Enter Lobby ID:");
                    if (lobbyId) handleJoinLobby(lobbyId);
                  }}
                  disabled={!isBackendConnected}
                >
                  Join Game
                </button>
              </>
            )}

            {/* Choose Letter */}
            {gameMode === "online" && createdLobby && !userLetter && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">
                  Choose Your Letter
                </h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <button
                    className="w-24 px-6 py-3 bg-blue-500 hover:bg-blue-400 transition-colors"
                    onClick={() => setUserLetter("X")}
                  >
                    <PlayerX theme="dark" />
                  </button>
                  <button
                    className="w-24 px-6 py-3 bg-green-500 hover:bg-green-400 transition-colors"
                    onClick={() => setUserLetter("O")}
                  >
                    <PlayerO theme="dark" />
                  </button>
                </div>
              </div>
            )}

            {/* Who Starts (Online) */}
            {gameMode === "online" && userLetter && !onlineStarts && (
              <div className="mt-12 text-center">
                <h2 className="text-2xl font-semibold mb-4">Who Starts?</h2>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  {["X", "O"].map((letter) => (
                    <button
                      key={letter}
                      className={`px-6 py-3 ${
                        letter === "X"
                          ? "bg-blue-500 hover:bg-blue-400"
                          : "bg-green-500 hover:bg-green-400"
                      } transition-colors`}
                      onClick={() => {
                        handleCreateLobby(letter);
                      }}
                    >
                      {userLetter === letter ? "You" : "Opponent"}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Game Board */}
      {isBoardVisible && (
        <div className="w-full">
          <div className="w-full">
            <Board
              gameMode={gameMode}
              starts={starts}
              totalGames={totalGames}
              lobbyId={lobbyId}
              playerId={playerId}
              userLetter={userLetter}
              onlineStarts={onlineStarts}
              resetBoard={resetBoard}
              onReset={handleBoardReset}
            />
          </div>
          <button
            className="px-6 py-3 bg-red-500 text-white font-medium hover:bg-red-400 transition-colors"
            onClick={() => handleExitGame()}
          >
            Exit Game
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
