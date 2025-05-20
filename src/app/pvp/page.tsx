"use client";
import { useState } from "react";
import Link from "next/link";
import Button from "@/components/ui/button";
import Board from "@/components/core/board";
import Share from "@/components/ui/share";
import { toast } from "sonner";

export default function PVP() {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  return (
    <div className="flex flex-col items-center justify-center px-4 py-8 min-h-svh sm:px-8 sm:py-16">
      <>
        {/* Local or Online */}
        {isOnline === null && (
          <>
            <h1 className="mb-8 text-2xl font-bold sm:text-4xl">
              Ready to play?
            </h1>

            <div className="text-center">
              <h2 className="mb-4 text-xl font-semibold sm:text-2xl">How?</h2>
              <div className="flex flex-col justify-center gap-6 sm:flex-row">
                <Button text="Local" onClick={() => setIsOnline(false)} />
                <Button text="Online" onClick={() => setIsOnline(true)} />
              </div>
            </div>
          </>
        )}

        {isOnline === false && (
          <Board gameMode="player-vs-player" onExit={() => setIsOnline(null)} />
        )}

        {isOnline === true && (
          <>
            <h1 className="mb-8 text-2xl font-bold sm:text-4xl">
              Got friends?
            </h1>

            <div className="space-y-6 text-center">
              <h2 className="text-xl font-semibold sm:text-2xl">
                Be honest...
              </h2>
              <div className="flex flex-col justify-center gap-6 sm:flex-row">
                <Link href="/pvp/lobby">
                  <Button text="Share a link" />
                </Link>
                <Link href="/pvp/matchmaking">
                  <Button text="No, I don't" />
                </Link>
              </div>

              <h3 className="text-lg font-semibold">Or join a lobby:</h3>
              <div>
                <input
                  type="text"
                  id="lobby-id"
                  placeholder="Lobby ID"
                  className="px-6 py-4 text-black rounded-l"
                />
                <Button
                  text="Join"
                  className="!w-fit !rounded-l-none"
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
          </>
        )}

        {isOnline !== false && (
          <Button
            text={isOnline ? "Go Back" : "Exit"}
            className="mt-6 sm:!w-48"
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
      </>
      <Share />
    </div>
  );
}
