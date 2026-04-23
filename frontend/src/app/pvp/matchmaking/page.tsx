"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { getSocket, disconnectSocket } from "@/socket";
import type { Socket } from "socket.io-client";
import type { DefaultEventsMap } from "@socket.io/component-emitter";
import Board from "@/components/core/board";
import Button from "@/components/ui/button";
import { RefreshCw, Search } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import Share from "@/components/ui/share";

export default function Matchmaking() {
  const router = useRouter();
  const socketRef = useRef<Socket<DefaultEventsMap>>();
  const [connectionStatus, setConnectionStatus] = useState("Connecting...");
  const [isSearching, setIsSearching] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [animateIcon, setAnimateIcon] = useState(false);
  const [matchFound, setMatchFound] = useState(false);
  const [yourLetter, setYourLetter] = useState("X");
  const [lobbyCode, setLobbyCode] = useState("");
  const [connectedUsers, setConnectedUsers] = useState(0);

  const toggleSearch = () => {
    setIsSearching((prev) => !prev);
    setSearchTime(0);
  };

  // Handle search timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSearching) {
      interval = setInterval(() => {
        setSearchTime((prev) => prev + 1);
        setAnimateIcon((prev) => !prev);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isSearching]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  useEffect(() => {
    const socket = getSocket();
    socketRef.current = socket;

    socket.on("connect", () => {
      setConnectionStatus("Connected");
    });

    socket.on("disconnect", () => {
      setConnectionStatus("Not connected");
    });

    socket.on("connectedUsers", (count) => {
      setConnectedUsers(count);
    });

    socket.on("matchFound", ({ code, yourLetter: assignedLetter }) => {
      setMatchFound(true);
      setLobbyCode(code);
      setYourLetter(assignedLetter);
    });

    return () => {
      socket.off("connect");
      socket.off("searching");
      socket.off("connectedUsers");
      socket.off("matchFound");
      disconnectSocket();
    };
  }, []);

  useEffect(() => {
    const socket = socketRef.current;

    if (socketRef.current?.connected) {
      setConnectionStatus(isSearching ? "Searching..." : "Connected");
    }

    if (socket && isSearching) {
      socket.emit("matchmakingSearch");
    }
  }, [isSearching]);

  if (matchFound) {
    return (
      <div className="flex flex-col items-center justify-center px-2 py-4 min-h-svh sm:px-8 sm:py-16">
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
    <div className="flex flex-col items-center justify-center min-h-svh px-4 py-8 max-w-md mx-auto w-full">
      <h1 className="text-3xl sm:text-4xl font-bold text-center text-white mb-1">
        Find Opponent
      </h1>
      <p className="text-sm text-gray-400 mb-6">
        Quick match with a random player
      </p>

      <div className="flex items-center justify-center gap-3 mb-6">
        <TooltipProvider delayDuration={300}>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="cursor-help flex items-center gap-2 bg-gray-800/50 rounded-full px-3 py-1.5">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    connectionStatus === "Connected"
                      ? "bg-green-500"
                      : connectionStatus === "Not connected"
                      ? "bg-red-500"
                      : "bg-green-500 animate-pulse"
                  }`}
                />
                <span className="text-gray-300 text-sm">
                  {!socketRef.current?.id ? "Not connected" : connectionStatus}
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent
              side="bottom"
              className="bg-gray-800 text-white text-xs px-2 py-1 z-50"
            >
              <span>ID: {socketRef.current?.id || "Not connected"}</span>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div
                className={`flex items-center gap-2 bg-gray-800/50 rounded-full px-3 py-1.5 ${
                  connectedUsers <= 1 ? "ring-1 ring-red-500/50" : ""
                }`}
              >
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    connectedUsers > 1 ? "bg-green-500" : "bg-red-500"
                  }`}
                />
                <span className="text-gray-300 text-sm">
                  {connectedUsers} online
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent
              side="bottom"
              className="bg-gray-800 text-white text-xs"
            >
              {connectedUsers <= 1
                ? "Need at least 2 players to match"
                : `${connectedUsers} players available`}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <div className="w-full bg-gray-800/30 rounded-xl p-8 mb-6 flex flex-col items-center">
        {isSearching ? (
          <>
            <div
              className={`p-4 mb-4 rounded-full bg-blue-500/20 ${
                animateIcon ? "scale-105" : "scale-100"
              } transition-all duration-300`}
            >
              <RefreshCw
                className={`h-10 w-10 text-blue-400 ${
                  animateIcon ? "rotate-180" : "rotate-0"
                } transition-all duration-300`}
              />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Searching...</h2>
            <p className="text-lg text-gray-300 font-mono">
              {formatTime(searchTime)}
            </p>
          </>
        ) : (
          <>
            <div className="p-4 mb-4 rounded-full bg-emerald-500/20">
              <Search className="h-10 w-10 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Ready</h2>
            <p className="text-gray-400">Click below to start matchmaking</p>
          </>
        )}

        <Button
          className="mt-4 w-full"
          text={isSearching ? "Cancel Search" : "Find Match"}
          variant={isSearching ? "primary" : "secondary"}
          onClick={toggleSearch}
        />
      </div>

      <Button
        text="Back to Home"
        variant="danger"
        onClick={() => router.push("/")}
      />

      <Share />
    </div>
  );
}
