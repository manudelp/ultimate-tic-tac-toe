"use client";
import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useGameSocket } from "@/hooks/useGameSocket";
import Board from "@/components/core/board";
import Loader from "@/components/ui/loader";
import { Clipboard } from "lucide-react";
import { toast } from "sonner";

export default function GamePage() {
  const router = useRouter();
  const initialized = useRef(false);
  const {
    gameState, myPlayer, gameId, connected, searching,
    lobbyId, opponent, error,
    findGame, makeMove, resign, disconnect,
  } = useGameSocket();

  // Read config and start game — wait for connection
  useEffect(() => {
    if (!connected || initialized.current) return;
    initialized.current = true;

    const raw = sessionStorage.getItem("uttt_game_config");
    if (!raw) {
      router.replace("/play");
      return;
    }

    const config = JSON.parse(raw);

    if (config.mode === "player-vs-bot") {
      findGame({ mode: "bot", botId: config.botId, starts: config.starts });
    } else if (config.mode === "player-vs-player") {
      findGame({ mode: "bot", botId: 0, starts: config.starts });
    } else if (config.mode === "online") {
      if (config.matchmaking) {
        findGame({ mode: "matchmaking" });
      } else if (config.lobbyCode) {
        findGame({ mode: "lobby_join", gameId: config.lobbyCode });
      } else {
        findGame({ mode: "lobby_create" });
      }
    }
  }, [connected, router, findGame]);

  const handleExit = () => {
    disconnect();
    sessionStorage.removeItem("uttt_game_config");
    router.push("/play");
  };

  // Show errors
  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  // Connecting
  if (!connected) {
    return (
      <div className="flex flex-col items-center justify-center min-h-svh gap-4">
        <Loader />
        <p className="text-sm text-gray-400">Connecting to server...</p>
      </div>
    );
  }

  // Searching for match
  if (searching) {
    return (
      <div className="flex flex-col items-center justify-center min-h-svh gap-4">
        <Loader />
        <p className="text-sm text-gray-400">Finding opponent...</p>
        <button onClick={handleExit} className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors">
          Cancel
        </button>
      </div>
    );
  }

  // Lobby waiting
  if (lobbyId && !gameState) {
    return (
      <div className="flex flex-col items-center justify-center min-h-svh px-4 py-8 text-center gap-4">
        <h1 className="text-2xl font-bold">Lobby</h1>
        <p className="text-gray-400 text-sm">Share this code with your opponent</p>
        <div
          className="px-6 py-4 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors"
          onClick={() => {
            navigator.clipboard?.writeText(lobbyId);
            toast.success("Code copied!", { duration: 2000 });
          }}
        >
          <div className="flex items-center justify-center gap-2">
            <span className="font-mono text-2xl tracking-widest text-blue-400">{lobbyId}</span>
            <Clipboard className="w-4 h-4 text-gray-400" />
          </div>
        </div>
        <p className="text-sm text-gray-400 animate-pulse">Waiting for opponent</p>
        <button onClick={handleExit} className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors">
          Cancel
        </button>
      </div>
    );
  }

  // Game active
  if (gameState && myPlayer) {
    return (
      <div className="flex items-center justify-center min-h-svh px-4 py-8 sm:px-8">
        <Board
          state={gameState}
          myPlayer={myPlayer}
          opponent={opponent}
          onCellClick={makeMove}
          onResign={resign}
          onExit={handleExit}
        />
      </div>
    );
  }

  // Fallback loading
  return (
    <div className="flex flex-col items-center justify-center min-h-svh gap-4">
      <Loader />
      <p className="text-sm text-gray-400">Setting up game...</p>
    </div>
  );
}
