// src/pages/lobby.tsx

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import socket from "@/socket";
import Button from "@/app/components/ui/button";
import { toast } from "sonner";

export default function Lobby() {
  const router = useRouter();
  const { code } = router.query;

  const [lobbyCode, setLobbyCode] = useState("");
  const [copied, setCopied] = useState(false);
  const [waiting, setWaiting] = useState(true);

  useEffect(() => {
    if (!router.isReady) return;

    if (typeof code === "string") {
      setLobbyCode(code);
      socket.emit("joinLobby", { code });
    } else {
      const newCode = Math.random().toString(36).substring(2, 7).toUpperCase();
      setLobbyCode(newCode);
      socket.emit("createLobby", { code: newCode });

      const lobbyLink = `${window.location.origin}/lobby?code=${newCode}`;
      navigator.clipboard.writeText(lobbyLink).then(() => {
        setCopied(true);
      });
    }
  }, [router.isReady, code]);

  useEffect(() => {
    socket.on("startGame", () => {
      console.log("Game starting!");
      setWaiting(false);
    });

    socket.on("error", (error) => {
      alert(error.message || "An error occurred");
    });

    return () => {
      socket.off("startGame");
      socket.off("error");
    };
  }, []);

  const handleCopyLink = () => {
    const lobbyLink = `${window.location.origin}/lobby?code=${lobbyCode}`;
    navigator.clipboard.writeText(lobbyLink).then(() => {
      setCopied(true);
    });
    toast.success("Link copied to clipboard!", { duration: 2000 });
  };

  useEffect(() => {
    if (copied) {
      toast.success("Link copied to clipboard!", { duration: 2000 });
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }
  }, [copied]);

  if (!waiting) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-bold">
          Debugging! You have entered the game.
        </h1>
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
      <p className="mt-4 text-sm sm:text-base italic">
        Waiting for a player to join...
      </p>
    </div>
  );
}
