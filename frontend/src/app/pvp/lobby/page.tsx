"use client";
import { useEffect, useState, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getSocket, disconnectSocket } from "@/socket";
import type { Socket } from "socket.io-client";
import type { DefaultEventsMap } from "@socket.io/component-emitter";
import Button from "@/components/ui/button-2";
import Board from "@/components/core/board";
import Share from "@/components/ui/share";
import { toast } from "sonner";
import { ClipboardIcon } from "@heroicons/react/24/outline";

interface StartGameData {
  yourLetter: string;
  yourTurn: boolean;
}

function LobbyContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const codeParam = searchParams.get("code") ?? "";

  const lobbyInitialized = useRef(false);
  const [lobbyCode, setLobbyCode] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const [waiting, setWaiting] = useState(true);
  const socketRef = useRef<Socket<DefaultEventsMap, DefaultEventsMap> | null>(
    null
  );
  const [hydrated, setHydrated] = useState(false);

  const [yourLetter, setYourLetter] = useState<string>("X");

  // Mark hydrated after client mount to avoid SSR/client mismatch
  useEffect(() => {
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    if (lobbyInitialized.current) return;
    lobbyInitialized.current = true;

    socketRef.current = getSocket();
    const socket = socketRef.current;

    const joinOrCreateLobby = () => {
      if (codeParam) {
        setLobbyCode(codeParam);
        socket.emit("joinLobby", { code: codeParam });
      } else {
        const newCode = Math.random()
          .toString(36)
          .substring(2, 7)
          .toUpperCase();
        setLobbyCode(newCode);
        socket.emit("createLobby", { code: newCode });

        if (typeof window !== "undefined") {
          setTimeout(() => {
            const lobbyLink = `${window.location.origin}/pvp/lobby?code=${newCode}`;
            navigator.clipboard.writeText(lobbyLink).then(() => {
              setCopied(true);
              toast.success("Link copied to clipboard!", { duration: 2000 });
            });
          }, 0);
        }
      }
    };

    if (socket.connected) {
      joinOrCreateLobby();
    } else {
      socket.on("connect", joinOrCreateLobby);
    }

    return () => {
      if (socket) {
        socket.off("connect", joinOrCreateLobby);
        if (lobbyCode) {
          socket.emit("leaveLobby", { code: lobbyCode });
        }
        disconnectSocket();
      }
    };
  }, [codeParam, hydrated, lobbyCode]);

  useEffect(() => {
    if (!hydrated) return;

    const socket = socketRef.current;
    if (!socket) return;

    const onStartGame = (data: StartGameData) => {
      setYourLetter(data.yourLetter);
      setWaiting(false);

      if (data.yourLetter === "X") {
        toast.success("Opponent joined! Game starting...", { duration: 3000 });
      } else {
        toast.success("Joined game! Starting...", { duration: 3000 });
      }
    };

    const onError = (error: { message?: string }) => {
      console.error("Socket error:", error);
      toast.error(error.message || "An error occurred", { duration: 3000 });
      setTimeout(() => {
        window.location.href = "/pvp";
      }, 3000);
    };

    socket.on("startGame", onStartGame);
    socket.on("error", onError);

    return () => {
      socket.off("lobbyCreated");
      socket.off("startGame", onStartGame);
      socket.off("error", onError);
    };
  }, [hydrated]);

  useEffect(() => {
    if (!hydrated) return;

    if (lobbyCode && waiting) {
      const dots = [".", "..", "..."];
      const titleInterval = setInterval(() => {
        const currentDotIndex = new Date().getSeconds() % 3;
        document.title = `Waiting${dots[currentDotIndex]} | Lobby ${lobbyCode} - Ultimate Tic Tac Toe`;
      }, 1000);

      return () => {
        clearInterval(titleInterval);
        document.title = "Ultimate Tic Tac Toe";
      };
    } else if (lobbyCode) {
      document.title = `IN GAME! | Lobby ${lobbyCode} - Ultimate Tic Tac Toe`;
    }

    return () => {
      document.title = "Ultimate Tic Tac Toe";
    };
  }, [lobbyCode, waiting, hydrated]);

  if (!hydrated) return null;

  if (!waiting) {
    return (
      <div className="flex flex-col items-center justify-center px-4 py-8 min-h-svh sm:px-8 sm:py-16">
        <Board
          gameMode="online"
          starts={yourLetter}
          onExit={() => {
            const socket = socketRef.current;
            if (socket) {
              socket.emit("leaveLobby", { code: lobbyCode });
            }
            disconnectSocket();
            router.push("/");
          }}
          yourLetter={yourLetter}
          lobbyCode={lobbyCode}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 text-center">
      <div className="w-full max-w-md p-8 space-y-6">
        <h1 className="text-2xl font-bold sm:text-4xl">The Lobby</h1>
        <h2 className="text-md">Share your lobby link below:</h2>

        <div
          className="px-6 py-4 mb-6 transition-colors bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700"
          onClick={() => {
            const lobbyLink = `/pvp/lobby?code=${lobbyCode}`;
            const fullLink =
              typeof window !== "undefined"
                ? `${window.location.origin}${lobbyLink}`
                : lobbyLink;
            if (typeof navigator !== "undefined" && navigator.clipboard) {
              navigator.clipboard.writeText(fullLink).then(() => {
                setCopied(true);
                toast.success("Link copied to clipboard!", { duration: 2000 });
              });
            }
          }}
          title="Click to copy lobby link"
        >
          <p className="text-sm text-gray-400">
            Your lobby code (click to copy):
          </p>
          <div className="flex items-center justify-center gap-2">
            <span className="font-mono text-2xl tracking-widest text-blue-400">
              {lobbyCode}
            </span>
            <ClipboardIcon className="w-6 h-6 text-white" />
          </div>
        </div>
        {!copied ? (
          <div className="p-2 font-mono text-xs break-all bg-gray-700 rounded select-all">
            {typeof window !== "undefined"
              ? `${window.location.origin}/pvp/lobby?code=${lobbyCode}`
              : lobbyCode}
          </div>
        ) : null}
        <p className="flex items-center justify-center mt-6 text-sm text-gray-400 animate-pulse">
          Waiting for opponent
        </p>
        <Button
          text="Leave Lobby"
          onClick={() => {
            const socket = socketRef.current;
            if (socket) {
              socket.emit("leaveLobby", { code: lobbyCode });
            }
            disconnectSocket();
            router.push("/");
          }}
          variant="danger"
        />
      </div>

      <Share />
    </div>
  );
}

export default function Lobby() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          Loading...
        </div>
      }
    >
      <LobbyContent />
    </Suspense>
  );
}
