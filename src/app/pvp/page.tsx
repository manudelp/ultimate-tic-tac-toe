"use client";
import { useState } from "react";
import Link from "next/link";
import Button from "@/components/ui/button-2";
import Board from "@/components/core/board";
import Share from "@/components/ui/share";
import { toast } from "sonner";

export default function PVP() {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  return (
    <div className="flex flex-col items-center justify-center px-4 py-8 min-h-svh sm:px-8 sm:py-16">
      {isOnline === null && (
        <>
          <h1 className="mb-8 text-3xl font-bold sm:text-4xl bg-gradient-to-r from-green-400 to-blue-500 text-transparent bg-clip-text">
            Ready to play?
          </h1>
          <h2 className="mb-6 text-xl font-semibold sm:text-2xl">
            Select mode
          </h2>
          <div className="flex items-center gap-4 flex-wrap">
            <Button text="Local" onClick={() => setIsOnline(false)} />
            <Button text="Online" onClick={() => setIsOnline(true)} />
          </div>
        </>
      )}

      {isOnline === false && (
        <Board gameMode="player-vs-player" onExit={() => setIsOnline(null)} />
      )}

      {isOnline === true && (
        <>
          <h1 className="mb-8 text-3xl font-bold sm:text-4xl">Online Mode</h1>

          <div className="flex flex-col sm:flex-row justify-center items-center mx-auto gap-12 w-full max-w-3xl">
            <div className="flex flex-col items-center gap-4">
              <Link href="/pvp/lobby">
                <Button text="Create Lobby" />
              </Link>

              <div className="flex items-center">
                <input
                  type="text"
                  id="lobby-id"
                  placeholder="Enter Lobby ID"
                  className="px-4 py-2 w-40 sm:w-48 text-black rounded-l"
                />
                <Button
                  text="Join"
                  className="!px-4 !py-2 !w-fit !rounded-l-none"
                  onClick={() => {
                    const input = document.querySelector(
                      "#lobby-id"
                    ) as HTMLInputElement;
                    if (input) {
                      const lobbyId = input.value;
                      if (lobbyId.length === 5) {
                        window.location.href = `/pvp/lobby?code=${lobbyId.toUpperCase()}`;
                      } else {
                        toast.error("Please enter a valid lobby ID.");
                      }
                    }
                  }}
                />
              </div>
            </div>

            <span className="hidden sm:block w-px h-48 bg-gray-300/20"></span>

            <div className="flex flex-col items-center gap-4">
              <p className="text-lg font-medium">Quick Match</p>
              <Link href="/pvp/matchmaking">
                <Button text="Find Opponent" />
              </Link>
            </div>
          </div>
        </>
      )}

      {isOnline !== false && (
        <Button
          text={isOnline ? "Go Back" : "Exit"}
          className="mt-8 !w-48"
          variant="danger"
          onClick={() => {
            if (isOnline) {
              setIsOnline(null);
            } else {
              window.location.href = "/";
            }
          }}
        />
      )}

      <Share />
    </div>
  );
}
