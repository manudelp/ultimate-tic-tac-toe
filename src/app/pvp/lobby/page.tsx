"use client";
import { useEffect, useState, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getSocket, disconnectSocket } from "@/socket";
import type { Socket } from "socket.io-client";
import type { DefaultEventsMap } from "@socket.io/component-emitter";
import Button from "@/components/ui/button";
import Board from "@/components/core/board/board";
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

  const [yourLetter, setYourLetter] = useState<string>("X");

  useEffect(() => {
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
  }, [lobbyCode, waiting]);

  const handleCopyLink = () => {
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
  };

  useEffect(() => {
    if (lobbyInitialized.current) return;
    lobbyInitialized.current = true;

    console.log("Initializing socket connection for lobby");
    socketRef.current = getSocket();
    const socket = socketRef.current;

    // Debug the current socket configuration
    console.log("Socket configuration:", {
      id: socket.id,
      connected: socket.connected,
      disconnected: socket.disconnected,
    });

    // Connect to the socket first, then join/create lobby
    const joinOrCreateLobby = () => {
      if (codeParam) {
        console.log(`Joining existing lobby with code: ${codeParam}`);
        setLobbyCode(codeParam);
        socket.emit("joinLobby", { code: codeParam });
        toast.success("Attempting to join lobby...", { duration: 2000 });
      } else {
        const newCode = Math.random()
          .toString(36)
          .substring(2, 7)
          .toUpperCase();
        console.log(`Creating new lobby with code: ${newCode}`);
        setLobbyCode(newCode);
        socket.emit("createLobby", { code: newCode });
        toast.success("Creating lobby...", { duration: 2000 });

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

    // If already connected, join/create lobby immediately
    if (socket.connected) {
      joinOrCreateLobby();
    } else {
      // Otherwise wait for connection before proceeding
      socket.on("connect", joinOrCreateLobby);
    }

    // Clean up on unmount
    return () => {
      if (socket) {
        socket.off("connect", joinOrCreateLobby);
        console.log("Cleaning up socket connection");
        if (lobbyCode) {
          socket.emit("leaveLobby", { code: lobbyCode });
        }
        disconnectSocket();
      }
    };
  }, [codeParam]);

  useEffect(() => {
    const socket = socketRef.current;
    if (!socket) return;

    console.log("Setting up socket event listeners");

    // Listen for lobby created confirmation
    socket.on("lobbyCreated", (data) => {
      console.log("Lobby created successfully:", data);
      toast.success(`Lobby ${data.code} created!`, { duration: 2000 });
    });

    const onStartGame = (data: StartGameData) => {
      console.log("Game starting with data:", data);
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
    };

    socket.on("startGame", onStartGame);
    socket.on("error", onError);

    return () => {
      console.log("Removing socket event listeners");
      socket.off("lobbyCreated");
      socket.off("startGame", onStartGame);
      socket.off("error", onError);
    };
  }, []);

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
          onClick={handleCopyLink}
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
