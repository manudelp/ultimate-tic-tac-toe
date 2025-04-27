// src/pages/lobby.tsx

import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import socket from "@/socket";
import Button from "@/app/components/ui/button";
import { toast } from "sonner";
import Board from "../core/board";

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
  const [yourTurn, setYourTurn] = useState<boolean>(false);

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
      <h1 className="text-2xl font-extrabold sm:text-4xl mb-4">
        Welcome to the Lobby!
      </h1>
      <p className="text-lg sm:text-xl mb-6">
        Your lobby code is:{" "}
        <span className="text-blue-400 font-mono text-2xl">{lobbyCode}</span>
      </p>
      <p className="text-sm sm:text-base mb-8">
        The link has been copied to your clipboard! <br /> Share it with a
        friend to join and play against you.
      </p>
      <Button
        text="Copy Link Again"
        onClick={handleCopyLink}
        variant="secondary"
      />
      <p className="mt-4 text-sm sm:text-base italic flex items-center justify-center">
        Waiting for a player to join
        <span className="inline-flex ml-1">
          <span className="animate-bounce mx-0.5 delay-0">.</span>
          <span className="animate-bounce mx-0.5 delay-150">.</span>
          <span className="animate-bounce mx-0.5 delay-300">.</span>
        </span>
      </p>
    </div>
  );
}
