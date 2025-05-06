"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import socket from "@/socket";
import Button from "@/components/ui/button";
import Board from "@/components/core/board/board";
import Share from "@/components/ui/share";
import { toast } from "sonner";
import { ClipboardIcon } from "@heroicons/react/24/outline";

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
  const [yourLetter, setYourLetter] = useState<string>("X");
  const [, setYourTurn] = useState<boolean>(false);

  // Page title
  useEffect(() => {
    if (lobbyCode && waiting) {
      // Change title with animated dots
      const dots = [".", "..", "..."];
      const titleInterval = setInterval(() => {
        const currentDotIndex = new Date().getSeconds() % 3;
        document.title = `Waiting${dots[currentDotIndex]} | Lobby ${lobbyCode} - Ultimate Tic Tac Toe`;
      }, 1000);

      // Clear interval when component unmounts or state changes
      return () => {
        clearInterval(titleInterval);
        document.title = "Ultimate Tic Tac Toe";
      };
    } else if (lobbyCode) {
      // Set title when waiting is false
      document.title = `IN GAME! | Lobby ${lobbyCode} - Ultimate Tic Tac Toe`;
    }

    // Restore original title when component unmounts
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

      // Handle clipboard in useEffect to avoid hydration mismatch
      if (typeof window !== "undefined") {
        // Using setTimeout to ensure this runs after component mounts
        setTimeout(() => {
          const lobbyLink = `${window.location.origin}/pvp/lobby?code=${newCode}`;
          navigator.clipboard.writeText(lobbyLink).then(() => {
            setCopied(true);
            toast.success("Link copied to clipboard!", { duration: 2000 });
          });
        }, 0);
      } else {
        toast.success("Link copied to clipboard!", { duration: 2000 });
      }
    }
  }, [code]);

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
      <div className="flex flex-col items-center justify-center px-4 py-8  min-h-svh sm:px-8 sm:py-16">
        <Board
          gameMode="online"
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
    <div className="flex flex-col items-center justify-center min-h-screen px-4 text-center ">
      <div className="w-full max-w-md p-8 space-y-6 ">
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
              : `${lobbyCode}`}
          </div>
        ) : null}
        <p className="flex items-center justify-center mt-6 text-sm text-gray-400 animate-pulse">
          Waiting for opponent
        </p>

        <Button
          text="Leave Lobby"
          onClick={() => {
            socket.emit("leaveLobby", { code: lobbyCode });
            router.push("/");
          }}
          variant="danger"
        />
      </div>

      <Share />
    </div>
  );
}
