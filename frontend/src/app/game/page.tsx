"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Board from "@/components/core/board";
import Loader from "@/components/ui/loader";
import { getSocket, disconnectSocket } from "@/socket";
import { toast } from "sonner";
import { Clipboard } from "lucide-react";
import type { BotInfo } from "@/types/game";

interface GameConfig {
  mode: "player-vs-bot" | "player-vs-player" | "online";
  botId?: number;
  bot?: BotInfo;
  starts?: string;
  lobbyCode?: string;
  matchmaking?: boolean;
}

export default function GamePage() {
  const router = useRouter();
  const [config, setConfig] = useState<GameConfig | null>(null);

  // Online state
  const [lobbyCode, setLobbyCode] = useState("");
  const [yourLetter, setYourLetter] = useState("X");
  const [waiting, setWaiting] = useState(true);
  const [copied, setCopied] = useState(false);
  const socketRef = useRef<ReturnType<typeof getSocket> | null>(null);

  // Load config
  useEffect(() => {
    const raw = sessionStorage.getItem("uttt_game_config");
    if (!raw) { router.replace("/play"); return; }
    const parsed: GameConfig = JSON.parse(raw);
    setConfig(parsed);
  }, [router]);

  // Online lobby/matchmaking setup
  useEffect(() => {
    if (!config || config.mode !== "online") return;

    const socket = getSocket();
    socketRef.current = socket;

    const setup = () => {
      if (config.matchmaking) {
        socket.emit("matchmakingSearch");
      } else if (config.lobbyCode) {
        setLobbyCode(config.lobbyCode);
        socket.emit("joinLobby", { code: config.lobbyCode });
      } else {
        const code = Math.random().toString(36).substring(2, 7).toUpperCase();
        setLobbyCode(code);
        socket.emit("createLobby", { code });
        navigator.clipboard?.writeText(`${window.location.origin}/game?join=${code}`);
        setCopied(true);
        toast.success("Lobby link copied!", { duration: 2000 });
      }
    };

    if (socket.connected) setup();
    else socket.on("connect", setup);

    socket.on("startGame", (data: { yourLetter: string }) => {
      setYourLetter(data.yourLetter);
      setWaiting(false);
      toast.success("Game starting!", { duration: 2000 });
    });

    socket.on("matchFound", ({ code, yourLetter: letter }: { code: string; yourLetter: string }) => {
      setLobbyCode(code);
      setYourLetter(letter);
      setWaiting(false);
    });

    socket.on("error", (err: { message?: string }) => {
      toast.error(err.message || "Connection error");
      setTimeout(() => router.replace("/play"), 2000);
    });

    return () => {
      socket.off("connect", setup);
      socket.off("startGame");
      socket.off("matchFound");
      socket.off("error");
    };
  }, [config, router]);

  const handleExit = () => {
    if (config?.mode === "online" && socketRef.current) {
      socketRef.current.emit("leaveLobby", { code: lobbyCode });
      disconnectSocket();
    }
    sessionStorage.removeItem("uttt_game_config");
    sessionStorage.removeItem("uttt_game_state");
    router.push("/play");
  };

  // Loading
  if (!config) {
    return (
      <div className="flex items-center justify-center min-h-svh">
        <Loader />
      </div>
    );
  }

  // Online waiting room
  if (config.mode === "online" && waiting) {
    return (
      <div className="flex flex-col items-center justify-center min-h-svh px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-2">
          {config.matchmaking ? "Finding opponent..." : "Waiting for opponent"}
        </h1>
        <p className="text-gray-400 mb-6 text-sm">
          {config.matchmaking ? "Searching for a match" : "Share the lobby code below"}
        </p>

        {!config.matchmaking && lobbyCode && (
          <div
            className="px-6 py-4 mb-6 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors"
            onClick={() => {
              navigator.clipboard?.writeText(`${window.location.origin}/game?join=${lobbyCode}`);
              setCopied(true);
              toast.success("Link copied!", { duration: 2000 });
            }}
          >
            <p className="text-xs text-gray-400 mb-1">Lobby code (click to copy)</p>
            <div className="flex items-center justify-center gap-2">
              <span className="font-mono text-2xl tracking-widest text-blue-400">{lobbyCode}</span>
              <Clipboard className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        )}

        {config.matchmaking && (
          <div className="mb-6">
            <Loader />
          </div>
        )}

        <button
          onClick={handleExit}
          className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors"
        >
          Cancel
        </button>
      </div>
    );
  }

  // Active game
  return (
    <div className="flex items-center justify-center min-h-svh px-4 py-8 sm:px-8">
      <Board
        gameMode={config.mode}
        bot={config.bot}
        starts={config.starts || "player"}
        onExit={handleExit}
        yourLetter={config.mode === "online" ? yourLetter : undefined}
        lobbyCode={config.mode === "online" ? lobbyCode : undefined}
      />
    </div>
  );
}
