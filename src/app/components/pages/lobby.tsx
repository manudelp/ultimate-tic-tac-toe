// src/pages/lobby.tsx

import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import socket from "@/socket";
import Button from "@/app/components/ui/button";
import { toast } from "sonner";
import Board from "../core/board";
import { ClipboardIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";

export default function Lobby() {
  // Router and search params
  const router = useRouter();
  const searchParams = useSearchParams();
  const code = searchParams.get("code");

  // State variables
  const lobbyInitialized = useRef(false);
  const [lobbyCode, setLobbyCode] = useState("");
  const [copied, setCopied] = useState(false);
  const [waiting, setWaiting] = useState(true);

  // Match states
  const [yourLetter, setYourLetter] = useState<"X" | "O" | null>(null);
  const [, setYourTurn] = useState<boolean>(false);

  useEffect(() => {
    // Only run this effect once
    if (lobbyInitialized.current) return;
    lobbyInitialized.current = true;

    if (code) {
      setLobbyCode(code);
      socket.emit("joinLobby", { code });
      toast.success("Joined lobby successfully!", {
        duration: 2000,
      });
    } else {
      const newCode = Math.random().toString(36).substring(2, 7).toUpperCase();
      setLobbyCode(newCode);
      socket.emit("createLobby", { code: newCode });

      toast.success("Lobby created successfully!", {
        duration: 2000,
      });

      const lobbyLink = `${window.location.origin}/lobby?code=${newCode}`;
      navigator.clipboard.writeText(lobbyLink).then(() => {
        setCopied(true);
      });
    }
  }, [code]);

  const handleCopyLink = () => {
    const lobbyLink = `${window.location.origin}/lobby?code=${lobbyCode}`;
    navigator.clipboard.writeText(lobbyLink).then(() => {
      setCopied(true);
    });
    toast.success("Link copied to clipboard!", { duration: 2000 });
  };

  // Handle socket events for the game
  useEffect(() => {
    socket.on("startGame", (data) => {
      setYourLetter(data.yourLetter);
      setYourTurn(data.yourTurn);
      setWaiting(false);

      // Only show "Opponent joined" toast to the lobby creator (X player)
      if (data.yourLetter === "X") {
        toast.success("Opponent joined! Game starting...", { duration: 3000 });
      }
    });

    socket.on("error", (error) => {
      alert(error.message || "An error occurred");
    });

    return () => {
      socket.off("startGame");
      socket.off("error");
    };
  }, []);

  if (!waiting) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <Board
          gameMode="online"
          bot={null}
          starts={yourLetter}
          onExit={() => {
            socket.emit("leaveLobby", { code: lobbyCode });
            router.push("/");
          }}
          yourLetter={yourLetter || undefined}
          lobbyCode={lobbyCode}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-center text-white px-4">
      <div className="w-full max-w-md p-8 bg-gray-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-gray-700">
        <h1 className="text-2xl font-extrabold sm:text-4xl mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
          Welcome to the Lobby!
        </h1>

        <div className="bg-gray-900 py-4 px-6 rounded-lg mb-6">
          <p className="text-sm text-gray-400 mb-2">Your lobby code:</p>
          <div className="flex items-center justify-center gap-2">
            <span className="text-blue-400 font-mono text-2xl tracking-widest">
              {lobbyCode}
            </span>
            <button
              onClick={handleCopyLink}
              className="p-1.5 rounded-full bg-gray-700 hover:bg-blue-600 transition-colors"
              aria-label="Copy lobby code"
            >
              <ClipboardIcon className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>

        <div className="relative mb-8">
          <Button
            content={
              <div className="flex items-center justify-center gap-2">
                <ClipboardIcon className="w-4 h-4" />
                <span>Share Link with Friend</span>
              </div>
            }
            onClick={handleCopyLink}
            variant="primary"
            className="w-full bg-blue-600 hover:bg-blue-700"
          />
        </div>

        <div className="mb-6 flex flex-col items-center">
          <div className="relative w-16 h-16 mb-2">
            <div className="absolute inset-0 bg-blue-500 rounded-full opacity-20 animate-ping"></div>
            <div className="relative flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full">
              <span className="text-white text-lg font-bold">
                {yourLetter || "?"}
              </span>
            </div>
          </div>
          <p className="text-sm text-gray-300 flex items-center justify-center mt-6 animate-pulse">
            Waiting for opponent{copied ? " (Link copied!)" : ""}
          </p>
        </div>

        <Button
          content={
            <div className="flex items-center justify-center gap-2">
              <ArrowLeftIcon className="w-4 h-4" />
              <span>Back to Menu</span>
            </div>
          }
          onClick={() => {
            socket.emit("leaveLobby", { code: lobbyCode });
            router.push("/");
          }}
          variant="danger"
          className="w-full bg-gray-700 hover:bg-gray-600 border-none text-gray-200"
        />
      </div>
    </div>
  );
}
