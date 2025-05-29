"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { getSocket, disconnectSocket } from "@/socket";
import type { Socket } from "socket.io-client";
import type { DefaultEventsMap } from "@socket.io/component-emitter";
import Board from "@/components/core/board";
import {
  ArrowPathIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

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

  const toggleSearch = () => {
    setIsSearching((prev) => !prev);
    setSearchTime(0);
  };

  // Simulate connection to matchmaking server
  useEffect(() => {
    const timer = setTimeout(() => {
      setConnectionStatus("Connected");
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  // Handle search timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSearching) {
      interval = setInterval(() => {
        setSearchTime((prev) => prev + 1);
        setAnimateIcon((prev) => !prev); // Toggle animation state
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

    socket.on("searching", () => {
      setConnectionStatus("Searching...");
    });

    socket.on("matchFound", ({ code }) => {
      setMatchFound(true);
      setLobbyCode(code);
      setYourLetter(Math.random() > 0.5 ? "X" : "O");
    });

    if (isSearching) {
      socket.emit("matchmakingSearch");
    }

    return () => {
      socket.off("searching");
      socket.off("matchFound");
      disconnectSocket();
    };
  }, [isSearching]);

  if (matchFound) {
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
    <div className="flex flex-col items-center justify-center min-h-svh bg-gray-900">
      <div className="w-full max-w-2xl px-6 py-8 bg-gray-800/50 backdrop-blur-sm p-8 rounded">
        <h1 className="text-4xl font-bold text-center mb-2 text-white">
          Matchmaking
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Looking for an opponent
        </p>
        <TooltipProvider delayDuration={300}>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="cursor-help absolute top-4 left-4 flex items-center space-x-1 bg-gray-700/30 rounded-lg px-2 py-1 text-xs">
                <span
                  className={`inline-block w-2 h-2 rounded-full ${
                    connectionStatus === "Connected"
                      ? "bg-green-500"
                      : "bg-yellow-500 animate-pulse"
                  }`}
                ></span>
                <span className="text-gray-400">{connectionStatus}</span>
              </div>
            </TooltipTrigger>
            <TooltipContent
              side="right"
              className="bg-gray-800 text-white text-xs px-2 py-1 z-50"
            >
              <span>ID: {socketRef.current?.id || "Not connected"}</span>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {isSearching ? (
          <div className="mb-8 text-center">
            <div
              className={`inline-block p-4 mb-4 rounded-full bg-blue-500/10 ${
                animateIcon ? "scale-110" : "scale-100"
              } transition-all duration-500`}
            >
              <ArrowPathIcon
                className={`h-12 w-12 text-blue-400 ${
                  animateIcon ? "rotate-180" : "rotate-0"
                } transition-all duration-500`}
              />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Finding Opponent
            </h2>
            <p className="mb-2">{formatTime(searchTime)}</p>
          </div>
        ) : (
          <div className="mb-8 text-center">
            <div className="flex justify-center mb-6">
              <div className="flex flex-col items-center">
                <div className="p-3 rounded-full bg-emerald-500/10 mb-2">
                  <MagnifyingGlassIcon className="h-12 w-12 text-emerald-400" />
                </div>
                <span className="text-2xl font-bold text-white">
                  Click below to start looking for a match
                </span>
                <span className="text-sm text-gray-400">
                  You will be matched with a random opponent
                </span>
              </div>
            </div>
          </div>
        )}

        <button
          className={`w-full py-3 rounded-lg font-medium text-white transition-colors ${
            isSearching
              ? "bg-red-500 hover:bg-red-600"
              : "bg-blue-500 hover:bg-blue-600"
          }`}
          onClick={toggleSearch}
        >
          {isSearching ? "Cancel Search" : "Find Match"}
        </button>
      </div>
    </div>
  );
}
