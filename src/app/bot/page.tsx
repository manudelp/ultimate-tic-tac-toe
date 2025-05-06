"use client";
import React from "react";
import { useEffect, useState } from "react";
import { getBots, loadBot } from "@/api";
import Board from "@/components/core/board/board";
import Button from "@/components/ui/button";
import Loader from "@/components/ui/loader";
import Share from "@/components/ui/share";

// Types
type BotListResponse = {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
};

export default function Bot() {
  // State variables
  const [starts, setStarts] = useState<string | null>(null);
  const [bots, setBots] = useState<BotListResponse[] | null>(null);
  const [selectedBot, setSelectedBot] = useState<BotListResponse | null>(null);
  const [bot, setBot] = useState<BotListResponse | null>(null);
  const [botsLoaded, setBotsLoaded] = useState<boolean[]>([]);

  const handleExitGame = () => {
    setBots(null);
    setSelectedBot(null);
    setBot(null);
    setStarts(null);
  };

  const updateBotsLoaded = (id: number) => {
    setBotsLoaded((prev) => {
      const updated = [...prev];
      updated[id] = true;
      return updated;
    });
  };

  useEffect(() => {
    if (!bots) {
      getBots().then((bots) => {
        setBots(bots.map((bot: BotListResponse) => ({ ...bot })));

        bots.forEach((bot) => {
          loadBot(bot.id).then(() => {
            updateBotsLoaded(bot.id);
          });
        });
      });
    }
  }, [bots]);

  return (
    <div className="flex flex-col items-center justify-center px-4 py-8  min-h-svh sm:px-8 sm:py-16">
      {/* Choose Bot */}
      {!bot && (
        <>
          <h1 className="mt-20 text-2xl font-bold sm:text-4xl">
            So you dare to face us...
          </h1>

          <div className="max-w-4xl px-2 mx-auto mt-4 sm:px-4">
            <h2 className="mb-6 text-xl font-bold text-center sm:text-2xl">
              Choose your opponent
            </h2>

            <div
              className={`grid ${
                selectedBot ? "sm:grid-cols-[2fr_1fr]" : "grid-cols-1"
              } gap-4`}
            >
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-2">
                {bots?.map((botOption) => (
                  <div
                    key={botOption.id}
                    className={`relative bg-gray-800 rounded-lg overflow-hidden transition-all duration-200 ring-2 ${
                      !botsLoaded[botOption.id] && "opacity-60"
                    } ${
                      selectedBot?.id === botOption.id
                        ? "ring-red-500"
                        : "ring-transparent"
                    }`}
                  >
                    <button
                      className="flex flex-col items-center w-full h-full p-4 text-left"
                      disabled={!botsLoaded[botOption.id]}
                      onClick={() => {
                        setSelectedBot(botOption);
                        setStarts(null); // Reset start choice when bot changes
                        if (window.innerWidth <= 768) {
                          setTimeout(() => {
                            const selectedBotMenu =
                              document.getElementById("selectedBotMenu");
                            if (selectedBotMenu) {
                              selectedBotMenu.scrollIntoView({
                                behavior: "smooth",
                                block: "start",
                              });
                            }
                          }, 100);
                        }
                      }}
                    >
                      {/* Bot avatar */}
                      <div
                        className={`relative rounded-full text-4xl w-20 h-20 grid place-items-center mb-3 ${
                          botOption.id === -1 ? "bg-black" : "bg-gray-700"
                        }`}
                        style={
                          botOption.id === -1
                            ? { backgroundImage: `url('/fire.gif')` }
                            : undefined
                        }
                      >
                        {botOption.icon}
                      </div>

                      {/* Bot info */}
                      <div className="w-full text-center">
                        <h3 className="mb-1 text-lg font-bold">
                          {botOption.name}
                        </h3>

                        {/* Difficulty rating */}
                        <div className="flex justify-center mb-2">
                          {Array(5)
                            .fill(0)
                            .map((_, i) => (
                              <span key={i} className="mx-0.5">
                                {i < botOption.difficulty ? "🔥" : "⚪"}
                              </span>
                            ))}
                        </div>
                      </div>

                      {/* Loading indicator */}
                      {!botsLoaded[botOption.id] && (
                        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-70">
                          <Loader />
                        </div>
                      )}
                    </button>
                  </div>
                ))}
              </div>

              {/* Full description panel with "Who starts" choice */}
              {selectedBot && (
                <div
                  id="selectedBotMenu"
                  className="flex flex-col justify-between p-4 mt-6 bg-gray-800 rounded-lg shadow-lg sm:mt-0"
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div className="flex items-center justify-center w-16 h-16 text-4xl bg-gray-700 rounded-full">
                      {selectedBot.icon}
                    </div>
                    <div className="flex flex-col items-start justify-center">
                      <h3 className="text-xl font-bold">{selectedBot.name}</h3>
                      <div className="flex">
                        {Array(selectedBot.difficulty)
                          .fill("🔥")
                          .map((fire, i) => (
                            <span key={i}>{fire}</span>
                          ))}
                      </div>
                    </div>
                  </div>

                  <p className="mb-4 text-gray-300">
                    {selectedBot.description || "No description available."}
                  </p>

                  {/* Who starts section */}
                  <div className="mb-4">
                    <h3 className="mb-2 font-semibold">Who starts?</h3>
                    <div className="flex gap-2 mb-4">
                      <button
                        className={`flex-1 px-3 py-2 text-sm border rounded-md transition-colors ${
                          starts === "player"
                            ? "bg-blue-600 border-blue-400"
                            : "bg-gray-700 border-gray-600 hover:bg-gray-600"
                        }`}
                        onClick={() => setStarts("player")}
                      >
                        You
                      </button>
                      <button
                        className={`flex-1 px-3 py-2 text-sm border rounded-md transition-colors ${
                          starts === "bot"
                            ? "bg-red-600 border-red-400"
                            : "bg-gray-700 border-gray-600 hover:bg-gray-600"
                        }`}
                        onClick={() => setStarts("bot")}
                      >
                        Bot
                      </button>
                    </div>
                  </div>

                  <Button
                    text="Play Now"
                    variant="success"
                    className={`!w-full !h-12 text-sm !p-0 ${
                      !starts ? "opacity-50 cursor-not-allowed" : ""
                    }`}
                    disabled={!starts}
                    onClick={() => setBot(selectedBot)}
                  />
                </div>
              )}
            </div>
          </div>

          <Button
            text="Exit"
            className="mt-6 sm:!w-48"
            variant="danger"
            onClick={() => (window.location.href = "/")}
          />
        </>
      )}

      {/* Game container would go here */}
      {bot && starts && (
        <Board
          gameMode="player-vs-bot"
          bot={bot}
          starts={starts}
          onExit={handleExitGame}
        />
      )}

      <Share />
    </div>
  );
}
