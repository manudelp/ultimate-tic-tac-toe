"use client";
import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Button from "@/components/ui/button";
import Board from "@/components/core/board";
import { toast } from "sonner";

function PVPContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const savedPage = typeof window !== "undefined" ? sessionStorage.getItem("uttt_pvp_page") : null;
  const parsed = savedPage ? JSON.parse(savedPage) : null;

  const modeParam = searchParams.get("mode");
  const initialOnline = parsed?.isOnline ?? (modeParam === "online" ? true : modeParam === "local" ? false : null);

  const [isOnline, setIsOnline] = useState<boolean | null>(initialOnline);
  const [localStarts, setLocalStarts] = useState<string | null>(parsed?.localStarts ?? null);
  const [lobbyInput, setLobbyInput] = useState("");

  useEffect(() => {
    if (isOnline === false && localStarts) {
      sessionStorage.setItem("uttt_pvp_page", JSON.stringify({ isOnline, localStarts }));
    }
  }, [isOnline, localStarts]);

  const handleExitLocal = () => {
    setIsOnline(null);
    setLocalStarts(null);
    sessionStorage.removeItem("uttt_pvp_page");
    sessionStorage.removeItem("uttt_game_state");
  };

  const handleJoinLobby = () => {
    const code = lobbyInput.trim().toUpperCase();
    if (code.length === 5) {
      router.push(`/pvp/lobby?code=${code}`);
    } else {
      toast.error("Please enter a valid 5-character lobby ID.");
    }
  };

  // In-game: full screen, no chrome
  if (isOnline === false && localStarts) {
    return (
      <div className="flex items-center justify-center min-h-svh px-4 py-8">
        <Board
          gameMode="player-vs-player"
          starts={localStarts}
          onExit={handleExitLocal}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center px-4 py-8 min-h-svh sm:px-8 sm:py-16">
      {isOnline === null && (
        <>
          <h1 className="mb-8 text-3xl font-bold sm:text-4xl bg-gradient-to-r from-green-400 to-blue-500 text-transparent bg-clip-text">
            Player vs Player
          </h1>
          <div className="flex items-center gap-4 flex-wrap">
            <Button text="Local" onClick={() => setIsOnline(false)} />
            <Button text="Online" onClick={() => setIsOnline(true)} />
          </div>
          <Button
            text="Back to Menu"
            className="mt-8 !w-48"
            variant="danger"
            onClick={() => router.push("/")}
          />
        </>
      )}

      {isOnline === false && !localStarts && (
        <div className="flex flex-col items-center">
          <h2 className="mb-6 text-xl font-semibold">Who goes first?</h2>
          <div className="flex gap-4">
            <Button text="Player X" variant="secondary" onClick={() => setLocalStarts("player")} />
            <Button text="Player O" onClick={() => setLocalStarts("bot")} />
          </div>
          <Button
            text="Go Back"
            className="mt-6 !w-48"
            variant="danger"
            onClick={() => setIsOnline(null)}
          />
        </div>
      )}

      {isOnline === true && (
        <div className="flex flex-col items-center">
          <h1 className="mb-8 text-3xl font-bold sm:text-4xl">Online</h1>

          <div className="flex flex-col sm:flex-row justify-center items-start mx-auto gap-12 w-full max-w-3xl">
            <div className="flex flex-col items-center gap-4">
              <p className="text-lg font-medium">Create or join a lobby</p>
              <Link href="/pvp/lobby" className="w-full">
                <Button text="Create Lobby" />
              </Link>
              <div className="flex items-center">
                <input
                  type="text"
                  value={lobbyInput}
                  onChange={(e) => setLobbyInput(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === "Enter" && handleJoinLobby()}
                  placeholder="Enter Lobby ID"
                  maxLength={5}
                  className="px-4 py-2 w-40 sm:w-48 text-black rounded-l"
                />
                <Button
                  text="Join"
                  className="!px-4 !py-2 !w-fit !rounded-l-none"
                  onClick={handleJoinLobby}
                />
              </div>
            </div>

            <span className="hidden sm:block w-px h-48 bg-gray-300/20" />

            <div className="w-full flex flex-col justify-center items-center gap-4">
              <p className="text-lg font-medium">Quick Match</p>
              <Link href="/pvp/matchmaking" className="w-full">
                <Button text="Find Opponent" />
              </Link>
            </div>
          </div>

          <Button
            text="Go Back"
            className="mt-8 !w-48"
            variant="danger"
            onClick={() => setIsOnline(null)}
          />
        </div>
      )}
    </div>
  );
}

export default function PVP() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-svh">Loading...</div>}>
      <PVPContent />
    </Suspense>
  );
}
