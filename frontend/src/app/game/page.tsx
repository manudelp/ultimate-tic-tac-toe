"use client";
import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useGameSocket } from "@/hooks/useGameSocket";
import Board from "@/components/core/board";
import Loader from "@/components/ui/loader";
import { Clipboard, ArrowLeft, Link } from "lucide-react";
import { toast } from "sonner";

export default function GamePage() {
  const router = useRouter();
  const initialized = useRef(false);
  const {
    gameState, myPlayer, gameId, connected, searching,
    lobbyId, opponent, isLocal, error,
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

    let config;
    try {
      config = JSON.parse(raw);
    } catch {
      sessionStorage.removeItem("uttt_game_config");
      router.replace("/play");
      return;
    }
    sessionStorage.removeItem("uttt_game_config");

    if (config.mode === "player-vs-bot") {
      findGame({ mode: "bot", botId: config.botId, starts: config.starts, timeControl: config.timeControl });
    } else if (config.mode === "player-vs-player") {
      findGame({ mode: "local", starts: config.starts, timeControl: config.timeControl });
    } else if (config.mode === "online") {
      if (config.matchmaking) {
        findGame({ mode: "matchmaking", timeControl: config.timeControl });
      } else if (config.lobbyCode) {
        findGame({ mode: "lobby_join", gameId: config.lobbyCode });
      } else {
        findGame({ mode: "lobby_create", timeControl: config.timeControl });
      }
    }
  }, [connected, router, findGame]);

  const handleExit = () => {
    disconnect();
    router.push("/play");
  };

  // Show errors
  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  // Connecting
  if (!connected) {
    return (
      <div className="flex flex-col items-center justify-center min-h-svh gap-6 px-4">
        <Loader />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-300">Connecting to server</p>
          <p className="text-xs text-gray-500 mt-1">Please wait...</p>
        </div>
        <button onClick={handleExit} className="flex items-center gap-2 px-5 py-2 text-sm text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to menu
        </button>
      </div>
    );
  }

  // Searching for match
  if (searching) {
    return (
      <div className="flex flex-col items-center justify-center min-h-svh gap-6 px-4">
        <Loader />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-300">Finding opponent</p>
          <p className="text-xs text-gray-500 mt-1">Searching for a match...</p>
        </div>
        <button onClick={handleExit} className="flex items-center gap-2 px-5 py-2 text-sm text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          Cancel
        </button>
      </div>
    );
  }

  // Lobby waiting
  if (lobbyId && !gameState) {
    const lobbyUrl = `${window.location.origin}/play?join=${lobbyId}`;
    return (
      <div className="flex flex-col items-center justify-center min-h-svh px-4 gap-6">
        <div className="text-center">
          <p className="text-sm font-medium text-gray-300">Private Lobby</p>
          <p className="text-xs text-gray-500 mt-1">Share this code with your opponent</p>
        </div>
        <div
          className="px-8 py-4 bg-gray-800 rounded-xl border border-gray-700/50 cursor-pointer hover:border-gray-600 transition-colors"
          onClick={() => {
            navigator.clipboard?.writeText(lobbyId);
            toast.success("Code copied!", { duration: 2000 });
          }}
        >
          <div className="flex items-center justify-center gap-3">
            <span className="font-mono text-2xl tracking-[0.3em] text-white">{lobbyId}</span>
            <Clipboard className="w-4 h-4 text-gray-500" />
          </div>
        </div>
        <button
          onClick={() => {
            navigator.clipboard?.writeText(lobbyUrl);
            toast.success("Link copied!", { duration: 2000 });
          }}
          className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          <Link className="w-3 h-3" />
          Copy invite link
        </button>
        <p className="text-xs text-gray-500 animate-pulse">Waiting for opponent to join...</p>
        <button onClick={handleExit} className="flex items-center gap-2 px-5 py-2 text-sm text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
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
          isLocal={isLocal}
          onCellClick={makeMove}
          onResign={resign}
          onExit={handleExit}
        />
      </div>
    );
  }

  // Fallback loading
  return (
    <div className="flex flex-col items-center justify-center min-h-svh gap-6 px-4">
      <Loader />
      <div className="text-center">
        <p className="text-sm font-medium text-gray-300">Setting up game</p>
        <p className="text-xs text-gray-500 mt-1">Please wait...</p>
      </div>
      <button onClick={handleExit} className="flex items-center gap-2 px-5 py-2 text-sm text-gray-400 hover:text-white transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" />
        Back to menu
      </button>
    </div>
  );
}
